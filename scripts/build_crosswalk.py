"""One-off helper: propose name -> ISO3 mappings for team / country names used by the sources.

Run it after `python -m pipeline extract`. It matches names against Gapminder and mledoze/countries
(common, official and alternative spellings, IOC codes) and writes dbt/seeds/country_aliases.csv,
leaving unmatched names flagged for a manual decision. Manual decisions live in MANUAL below, so
the seed can be regenerated reproducibly.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "data" / "bronze"

# name -> ISO3 (or "" to exclude on purpose, e.g. historical states or non-country teams)
MANUAL = {
    # football / general
    "England": "GB-ENG", "Scotland": "GB-SCT", "Wales": "GB-WLS", "Northern Ireland": "GB-NIR",
    "Republic of Ireland": "IRL", "Ireland": "IRL", "China PR": "CHN", "DR Congo": "COD", "Congo": "COG",
    "Ivory Coast": "CIV", "Cape Verde": "CPV", "Czech Republic": "CZE", "Czechia": "CZE", "Eswatini": "SWZ",
    "Swaziland": "SWZ", "North Macedonia": "MKD", "F.Y.R. Macedonia": "MKD", "Macedonia": "MKD",
    "Kosovo": "XKX", "Taiwan": "TWN", "Chinese Taipei": "TWN", "Palestine": "PSE", "Hong Kong": "HKG", "Macau": "MAC",
    "South Korea": "KOR", "North Korea": "PRK", "Korea": "KOR", "United States": "USA", "USA": "USA",
    "Russia": "RUS", "Iran": "IRN", "Syria": "SYR", "Laos": "LAO", "Vietnam": "VNM", "Brunei": "BRN",
    "Moldova": "MDA", "Bolivia": "BOL", "Venezuela": "VEN", "Tanzania": "TZA", "Gambia": "GMB", "The Gambia": "GMB",
    "São Tomé and Príncipe": "STP", "Sao Tome and Principe": "STP", "East Timor": "TLS", "Timor-Leste": "TLS",
    "Curaçao": "CUW", "Turkey": "TUR", "Türkiye": "TUR", "Bosnia and Herzegovina": "BIH", "Bosnia & Herzegovina": "BIH",
    "Myanmar": "MMR", "Burma": "MMR", "The Netherlands": "NLD", "Netherlands": "NLD", "Vatican City": "",
    "Saint Kitts and Nevis": "KNA", "Saint Lucia": "LCA", "Saint Vincent and the Grenadines": "VCT",
    "Antigua and Barbuda": "ATG", "Trinidad and Tobago": "TTO", "United States Virgin Islands": "VIR",
    "British Virgin Islands": "VGB", "Turks and Caicos Islands": "TCA", "Micronesia": "FSM",
    # historical or non-country entities: excluded on purpose
    "Yugoslavia": "", "Serbia & Montenegro": "", "Serbia and Montenegro": "", "Soviet Union": "", "USSR": "",
    "Czechoslovakia": "", "East Germany": "", "West Germany": "", "German DR": "", "Zaïre": "COD",
    # Nobel organisation / birth-country spellings
    "Russian Federation": "RUS", "Federal Republic of Germany": "DEU", "Union of Soviet Socialist Republics": "",
    "Scotland (United Kingdom)": "GBR", "Northern Ireland (United Kingdom)": "GBR",
    "Bosnia and Herzegovina": "BIH", "Republic of Macedonia": "MKD", "Guadeloupe Island": "GLP",
    "Faroe Islands": "FRO", "Guadeloupe": "GLP", "Hong Kong SAR China": "HKG",
    "Tahiti": "PYF", "Ellan Vannin": "", "Alsace (then Germany, now France)": "FRA", "then Germany, now France": "FRA", "Trinidad": "TTO",
}

# Olympic NOC codes that are not in mledoze's IOC field
IOC_MANUAL = {"SSD": "SSD", "COR": "", "ROC": "RUS", "OAR": "RUS", "RPC": "RUS", "KOS": "XKX", "TPE": "TWN", "PUR": "PRI",
              "IOA": "", "IOP": "", "EOR": "", "ROT": "", "SCG": "", "AHO": "", "EUN": "", "ANZ": "", "MIX": ""}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", "", s).replace("&", "and")
    return re.sub(r"[^a-z]+", " ", s).strip()


def main() -> int:
    con = duckdb.connect()
    countries = json.loads((ROOT / "data" / "raw" / "countries" / "countries_flat.json").read_text())
    gm = con.execute(f"select coalesce(iso3166_1_alpha3, case when country='kos' then 'XKX' end), name from read_parquet('{B}/gapminder_countries.parquet')").fetchall()
    lookup: dict[str, str] = {}
    for c in countries:
        iso3 = "XKX" if c["iso3"] == "UNK" else c["iso3"]
        for n in [c["name_common"], c["name_official"], *c["alt_spellings"]]:
            lookup.setdefault(norm(n), iso3)
    for iso3, name in gm:
        if iso3:
            lookup.setdefault(norm(name), iso3)
    ioc = {c["ioc"]: ("XKX" if c["iso3"] == "UNK" else c["iso3"]) for c in countries if c.get("ioc")}

    names: dict[str, set] = {}
    def add(rows, src):
        for (n,) in rows:
            if n and n != "NA":
                names.setdefault(n, set()).add(src)
    add(con.execute(f"select distinct t from (select home_team t from read_parquet('{B}/football.parquet') where date >= '2010-01-01' union select away_team from read_parquet('{B}/football.parquet') where date >= '2010-01-01')").fetchall(), "football")
    add(con.execute(f"select distinct x from (select from_country x from read_parquet('{B}/eurovision.parquet') union select to_country from read_parquet('{B}/eurovision.parquet'))").fetchall(), "eurovision")
    for col in ("birth_country", "organization_country"):
        for (n,) in con.execute(f"select distinct {col} from read_parquet('{B}/nobel.parquet')").fetchall():
            if n and n != "NA":
                m = re.search(r"\(([^)]*)\)\s*$", n)            # "Prussia (Poland)" -> modern country "Poland"
                names.setdefault(n, set()).add("nobel")
                if m:
                    names.setdefault(m.group(1), set()).add("nobel-modern")

    rows, unmatched = [], []
    for n in sorted(names):
        modern = re.search(r"\(([^)]*)\)\s*$", n)
        key = modern.group(1) if modern and "nobel" in names[n] else n
        if key in MANUAL:
            iso3, method = MANUAL[key], "manual"
        elif norm(key) in lookup:
            iso3, method = lookup[norm(key)], "auto"
        elif names[n] == {"football"}:
            # regional, diaspora and other non-FIFA teams (CONIFA etc.): excluded from every analysis
            iso3, method = "", "excluded_non_fifa"
        else:
            iso3, method = "", "unmatched"
            unmatched.append((n, sorted(names[n])))
        rows.append({"alias": n, "iso3": iso3, "method": method, "used_by": "|".join(sorted(names[n]))})
    for code in sorted({r[0] for r in con.execute(f"select distinct noc from read_parquet('{B}/olympics.parquet') where year >= 2000 and event like '%(Olympic)' and noc is not null").fetchall()}):
        iso3 = IOC_MANUAL.get(code, ioc.get(code, ""))
        rows.append({"alias": f"IOC:{code}", "iso3": iso3, "method": "manual" if code in IOC_MANUAL else ("auto" if iso3 else "unmatched"), "used_by": "olympics"})
        if not iso3 and code not in IOC_MANUAL:
            unmatched.append((f"IOC:{code}", ["olympics"]))

    out = ROOT / "dbt" / "seeds" / "country_aliases.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["alias", "iso3", "method", "used_by"])
        w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} aliases, {len(unmatched)} unmatched")
    for n, s in unmatched:
        print("  UNMATCHED", n, s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
