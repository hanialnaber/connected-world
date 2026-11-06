"""Who does better (or worse) than their size and wealth predict?

Each row of SPECS is an ordinary least-squares model fitted across countries. Predictors are logged
(population, income, health spending), the residual is actual minus expected, and residual_z puts
residuals on a common scale. Expected Olympic medals come from a model of log(1 + medals), so a
country can be expected to win a fraction of a medal.
"""
import numpy as np
import pandas as pd

SPECS = [
    # model, outcome, predictors, outcome transform, minimum population
    ("happiness", "hapiscore_whr", ["gdp_pcap"], None, 1e6),
    ("olympics", "olympic_medals", ["pop", "gdp_pcap"], "log1p", 1e6),
    ("football", "football_elo", ["pop", "gdp_pcap"], None, 3e5),
    ("passports", "passport_power", ["gdp_pcap"], None, 1e6),
    ("health", "lex", ["sh_xpd_chex_pp_cd"], None, 1e6),
]


def model(dbt, session):
    dbt.config(materialized="table")
    latest = dbt.ref("int_country_latest").df()
    dims = dbt.ref("dim_country").df().set_index("iso3")
    medals = dbt.ref("int_olympics__country_medals").df().set_index("iso3")["medals"]

    wide = latest.pivot(index="iso3", columns="indicator", values="value")
    wide["olympic_medals"] = medals.reindex(wide.index).fillna(0)
    wide.loc[wide["olympic_medals_per_million"].isna(), "olympic_medals"] = np.nan  # not assessed

    out = []
    for name, outcome, preds, how, min_pop in SPECS:
        d = wide[[outcome, *preds]].copy()
        d = d[d.index.isin(dims.index[dims.population >= min_pop])].dropna()
        y = np.log1p(d[outcome]) if how == "log1p" else d[outcome]
        X = np.column_stack([np.ones(len(d))] + [np.log(d[p]) for p in preds])
        beta, *_ = np.linalg.lstsq(X, y.to_numpy(), rcond=None)
        fit = X @ beta
        resid_model = y.to_numpy() - fit
        r2 = 1 - (resid_model ** 2).sum() / ((y - y.mean()) ** 2).sum()
        expected = np.expm1(fit) if how == "log1p" else fit
        actual = d[outcome].to_numpy()
        res = actual - expected
        z = resid_model / resid_model.std(ddof=len(preds) + 1)
        for iso3, a, e, r, zz in zip(d.index, actual, expected, res, z):
            out.append((name, iso3, float(a), float(e), float(r), float(zz), float(r2), len(d),
                        float(beta[1]), " + ".join(f"log {p}" for p in preds)))
    df = pd.DataFrame(out, columns=["model", "iso3", "actual", "expected", "residual", "residual_z", "r_squared",
                                    "n_countries", "first_slope", "predictors"])
    return df.astype({"model": object, "iso3": object, "predictors": object})
