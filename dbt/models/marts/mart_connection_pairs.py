"""Which country statistics move together, and which links survive once wealth is held fixed.

For every pair of indicators in the catalogue: Spearman's rank correlation across countries, then
the partial rank correlation controlling for income (GDP per person): both indicators' ranks are
regressed on the income rank and the residuals are correlated. p-values use the t distribution;
q-values apply the Benjamini-Hochberg false-discovery correction across all pairs tested.
Countries under 500,000 people are left out so micro-states do not dominate the ranks.
"""
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats


def _transform(x: pd.Series, how: str) -> pd.Series:
    if how == "log":
        return np.log(x.where(x > 0))
    if how == "log1p":
        return np.log1p(x.where(x >= 0))
    return x


def _bh(p: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg q-values (NaN-safe)."""
    q = np.full_like(p, np.nan, dtype=float)
    ok = ~np.isnan(p)
    pv = p[ok]
    order = np.argsort(pv)
    ranked = pv[order] * len(pv) / (np.arange(len(pv)) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty_like(pv)
    out[order] = np.minimum(ranked, 1.0)
    q[ok] = out
    return q


def _residual(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    X = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta


def model(dbt, session):
    dbt.config(materialized="table")
    min_n = int(dbt.config.get("min_countries"))
    max_q = float(dbt.config.get("max_q"))
    min_partial = float(dbt.config.get("min_partial"))

    latest = dbt.ref("int_country_latest").df()
    catalog = dbt.ref("indicator_catalog").df()
    dims = dbt.ref("dim_country").df()
    catalog = catalog[catalog.in_network.astype(str).str.lower() == "true"]
    keep = set(dims.loc[dims.population >= 5e5, "iso3"])

    wide = latest[latest.iso3.isin(keep)].pivot(index="iso3", columns="indicator", values="value")
    wide = wide[[c for c in catalog.indicator if c in wide.columns]]
    for row in catalog.itertuples():
        if row.indicator in wide:
            wide[row.indicator] = _transform(wide[row.indicator].astype(float), row.transform)

    income = "gdp_pcap"
    rows = []
    for a, b in combinations(wide.columns, 2):
        cols = [a, b] if income in (a, b) else [a, b, income]
        d = wide[cols].dropna()
        n = len(d)
        if n < 20:
            continue
        rho, p_raw = stats.spearmanr(d[a], d[b])
        partial, p_partial = np.nan, np.nan
        if income not in (a, b):
            ra, rb, ri = (d[c].rank().to_numpy() for c in (a, b, income))
            ea, eb = _residual(ra, ri), _residual(rb, ri)
            partial = float(np.corrcoef(ea, eb)[0, 1])
            dof = n - 3
            t = partial * np.sqrt(dof / max(1e-12, 1 - partial ** 2))
            p_partial = float(2 * stats.t.sf(abs(t), dof))
        rows.append((a, b, n, float(rho), float(p_raw), partial, p_partial))

    out = pd.DataFrame(rows, columns=["indicator_a", "indicator_b", "n_countries", "rho", "p_raw", "partial_rho", "p_partial"])
    out["q_raw"] = _bh(out.p_raw.to_numpy())
    out["q_partial"] = _bh(out.p_partial.to_numpy())
    involves_income = (out.indicator_a == income) | (out.indicator_b == income)
    out["is_income_link"] = involves_income & (out.n_countries >= min_n) & (out.q_raw <= max_q) & (out.rho.abs() >= 0.5)
    out["is_link_beyond_income"] = (~involves_income) & (out.n_countries >= min_n) & (out.q_partial <= max_q) & (out.partial_rho.abs() >= min_partial)
    out["is_explained_by_income"] = (~involves_income) & (out.n_countries >= min_n) & (out.rho.abs() >= 0.5) & (out.partial_rho.abs() < 0.2)
    return out.astype({"indicator_a": object, "indicator_b": object})
