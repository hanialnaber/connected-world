"""Publish: read the marts and render the static page, with the data embedded as JSON.

The website never queries the warehouse. A refresh is "run the pipeline, ship the new file".
"""
from __future__ import annotations

import json
import logging
import math
from datetime import date, datetime, timezone

import duckdb

from .config import BRONZE, EXPORTS, ROOT, SITE_TEMPLATE, SOURCES, WAREHOUSE

log = logging.getLogger("connected_world")
PLACEHOLDER = "/*__CONNECTED_WORLD_DATA__*/"


def _clean(value):
    if isinstance(value, float):
        return None if math.isnan(value) or math.isinf(value) else round(value, 5)
    if isinstance(value, (date, datetime)):
        return value.isoformat()[:10]
    return value


def _rows(con: duckdb.DuckDBPyConnection, sql: str) -> list[dict]:
    cur = con.execute(sql)
    cols = [c[0] for c in cur.description]
    return [{k: _clean(v) for k, v in zip(cols, row)} for row in cur.fetchall()]


def _dbt_run_stats() -> dict:
    path = ROOT / "dbt" / "target" / "run_results.json"
    if not path.exists():
        return {}
    results = json.loads(path.read_text())["results"]
    kinds = {"model": 0, "seed": 0, "test": 0}
    passed = 0
    for r in results:
        kind = r["unique_id"].split(".")[0]
        if kind in kinds:
            kinds[kind] += 1
        passed += r["status"] in ("pass", "success")
    return {"models": kinds["model"], "seeds": kinds["seed"], "tests": kinds["test"], "passed": passed, "nodes": len(results)}


def build_payload(con: duckdb.DuckDBPyConnection, runtime_s: float | None = None) -> dict:
    manifest = json.loads((BRONZE / "_manifest.json").read_text())
    m = "marts"
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "kpis": _rows(con, f"select * from {m}.mart_headline_kpis")[0],
        "nodes": _rows(con, f"select * from {m}.mart_connection_nodes order by domain, indicator"),
        "edges": _rows(con, f"""
            select indicator_a as a, indicator_b as b, n_countries as n, rho, partial_rho, q_partial,
                   is_link_beyond_income as beyond, is_income_link as income
            from {m}.mart_connection_pairs where is_link_beyond_income or is_income_link"""),
        "happiness": _rows(con, f"select * from {m}.mart_happiness order by iso3"),
        "olympics": _rows(con, f"select * from {m}.mart_olympics order by performance_ratio desc"),
        "football": _rows(con, f"select * from {m}.mart_football order by rating desc"),
        "football_history": _rows(con, f"select * from {m}.mart_football_history order by team, year"),
        "passports": _rows(con, f"select * from {m}.mart_passports order by passport_power desc"),
        "bigmac": _rows(con, f"select * from {m}.mart_bigmac order by big_macs_per_day_of_income desc"),
        "nobel": _rows(con, f"select * from {m}.mart_nobel_countries where born_here + won_here >= 5 order by net_gain desc"),
        "nobel_flows": _rows(con, f"select * from {m}.mart_nobel_flows order by laureates desc limit 12"),
        "eurovision_effects": _rows(con, f"""
            select shares_border, shares_language, count(*) as pairs, avg(avg_points) as avg_points
            from {m}.mart_eurovision_pairs group by 1, 2 order by 1, 2"""),
        "eurovision_pairs": _rows(con, f"""
            select a.from_country as country_a, a.to_country as country_b, a.avg_points as a_to_b,
                   b.avg_points as b_to_a, least(a.finals_together, b.finals_together) as finals,
                   a.shares_border, a.shares_language
            from {m}.mart_eurovision_pairs a
            join {m}.mart_eurovision_pairs b on a.from_iso3 = b.to_iso3 and a.to_iso3 = b.from_iso3
            where a.from_iso3 < a.to_iso3
            order by a.avg_points + b.avg_points desc limit 10"""),
        "decoupling": _rows(con, f"select * from {m}.mart_decoupling order by co2_change"),
        "energy": _rows(con, f"select * from {m}.mart_energy order by change_pts desc"),
        "health": _rows(con, f"select * from {m}.mart_health order by iso3"),
        "coverage": _rows(con, f"select * from {m}.mart_source_coverage"),
        "lineage": {
            "sources": [{"key": s.key, "name": s.name, "publisher": s.publisher, "license": s.license,
                         "citation": s.citation, "url": s.url} for s in SOURCES],
            "bronze": manifest,
            "rows_landed": sum(b["rows"] for b in manifest),
            "dbt": _dbt_run_stats(),
            "runtime_s": round(runtime_s, 1) if runtime_s else None,
        },
    }


def run(runtime_s: float | None = None) -> dict:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE), read_only=True)
    payload = build_payload(con, runtime_s)
    (EXPORTS / "connected_world.json").write_text(json.dumps(payload, indent=1))
    template = SITE_TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise ValueError("template is missing the data placeholder")
    data = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    html = template.replace(PLACEHOLDER, data)
    (EXPORTS / "world.html").write_text(html, encoding="utf-8")
    log.info("rendered page -> %s (%d KB)", EXPORTS / "world.html", len(html) // 1024)
    return payload
