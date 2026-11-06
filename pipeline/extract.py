"""Extract + land: download every source into raw/, then write typed bronze Parquet with lineage.

Bronze keeps each source as delivered (no business logic), plus `_source_file` and `_loaded_at`,
so any number on the page can be traced back to a file, a checksum and a load time.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from .config import BRONZE, RAW, SOURCES, Source
from .http import cached_fetch, sha256

log = logging.getLogger("connected_world")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _land(con: duckdb.DuckDBPyConnection, select_sql: str, target: str) -> int:
    dest = BRONZE / f"{target}.parquet"
    con.execute(f"COPY ({select_sql}) TO '{dest}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    return con.execute(f"SELECT count(*) FROM read_parquet('{dest}')").fetchone()[0]


def _entry(src: Source, table: str, rows: int, files: list[Path], loaded_at: str) -> dict:
    return {"source": src.key, "table": table, "rows": rows, "files": [f.name for f in files],
            "sha256": {f.name: sha256(f) for f in files}, "url": src.url, "license": src.license,
            "loaded_at": loaded_at}


def ddf(con, src: Source, refresh: bool) -> list[dict]:
    """Gapminder / Open Numbers DDF: one CSV per indicator -> one long table (geo, year, indicator, value)."""
    files, selects = [], []
    for ind in src.files:
        path = cached_fetch(f"{src.url}/{src.extra['pattern'].format(i=ind)}", RAW / src.key / f"{ind}.csv", refresh=refresh)
        files.append(path)
        selects.append(
            f"SELECT lower({src.extra['geo_col']}) AS geo, time::INTEGER AS year, '{ind}' AS indicator, "
            f"\"{ind}\"::DOUBLE AS value, '{path.name}' AS _source_file FROM read_csv_auto('{path}', header = true)"
        )
    loaded_at = _now()
    out = []
    rows = _land(con, f"SELECT *, TIMESTAMP '{loaded_at}' AS _loaded_at FROM ({' UNION ALL '.join(selects)}) WHERE value IS NOT NULL",
                 f"{src.key}_datapoints")
    out.append(_entry(src, f"{src.key}_datapoints", rows, files, loaded_at))
    if "entities" in src.extra:
        path = cached_fetch(f"{src.url}/{src.extra['entities']}", RAW / src.key / "countries.csv", refresh=refresh)
        rows = _land(con, f"SELECT *, '{path.name}' AS _source_file, TIMESTAMP '{loaded_at}' AS _loaded_at "
                          f"FROM read_csv_auto('{path}', header = true, all_varchar = true)", f"{src.key}_countries")
        out.append(_entry(src, f"{src.key}_countries", rows, [path], loaded_at))
    return out


def csv(con, src: Source, refresh: bool) -> list[dict]:
    out = []
    for rel in src.files:
        path = cached_fetch(f"{src.url}/{rel}", RAW / src.key / Path(rel).name, refresh=refresh)
        loaded_at = _now()
        rows = _land(con, f"SELECT *, '{path.name}' AS _source_file, TIMESTAMP '{loaded_at}' AS _loaded_at "
                          f"FROM read_csv('{path}', header = true, sample_size = -1)", src.key)
        out.append(_entry(src, src.key, rows, [path], loaded_at))
    return out


def countries_json(con, src: Source, refresh: bool) -> list[dict]:
    """mledoze/countries is nested JSON; keep only the fields the models use, one row per country."""
    path = cached_fetch(f"{src.url}/{src.files[0]}", RAW / src.key / src.files[0], refresh=refresh)
    flat = []
    for c in json.loads(path.read_text(encoding="utf-8")):
        flat.append({
            "iso3": c.get("cca3"), "iso2": c.get("cca2"), "ioc": c.get("cioc") or None,
            "name_common": c["name"]["common"], "name_official": c["name"]["official"],
            "alt_spellings": c.get("altSpellings", []), "borders": c.get("borders", []),
            "languages": sorted((c.get("languages") or {}).values()), "landlocked": c.get("landlocked"),
            "area_km2": c.get("area"), "region": c.get("region"), "subregion": c.get("subregion"),
            "independent": c.get("independent"), "un_member": c.get("unMember"),
        })
    flat_path = RAW / src.key / "countries_flat.json"
    flat_path.write_text(json.dumps(flat), encoding="utf-8")
    loaded_at = _now()
    rows = _land(con, f"SELECT *, '{path.name}' AS _source_file, TIMESTAMP '{loaded_at}' AS _loaded_at "
                      f"FROM read_json_auto('{flat_path}')", src.key)
    return [_entry(src, src.key, rows, [path], loaded_at)]


LANDERS = {"ddf": ddf, "csv": csv, "json": countries_json}


def run(refresh: bool = False) -> list[dict]:
    BRONZE.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    manifest = []
    for src in SOURCES:
        entries = LANDERS[src.kind](con, src, refresh)
        manifest.extend(entries)
        for e in entries:
            log.info("landed %-28s %10s rows  (%s)", e["table"], f"{e['rows']:,}", src.license)
    (BRONZE / "_manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest
