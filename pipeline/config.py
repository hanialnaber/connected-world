"""Paths and the source registry: every dataset the pipeline reads, where it comes from, and its licence."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
BRONZE = DATA / "bronze"
WAREHOUSE = DATA / "warehouse.duckdb"
EXPORTS = ROOT / "exports"
SITE_TEMPLATE = ROOT / "site" / "template.html"

GH = "https://raw.githubusercontent.com"


@dataclass(frozen=True)
class Source:
    key: str            # short id used for raw/ and bronze/ paths
    name: str           # human name shown on the page
    publisher: str      # who produces the data
    url: str            # base URL
    files: tuple        # file paths relative to url (or indicator ids for DDF sources)
    license: str
    kind: str           # csv | json | ddf
    note: str = ""
    citation: str = ""
    extra: dict = field(default_factory=dict)


GAPMINDER = Source(
    key="gapminder", name="Gapminder Fast Track", publisher="Gapminder Foundation",
    url=f"{GH}/open-numbers/ddf--gapminder--fasttrack/master",
    files=(
        "pop", "gdp_pcap", "lex", "hapiscore_whr", "child_mortality_0_5_year_olds_dying_per_1000_born",
        "children_per_woman_total_fertility", "immigrant_pc", "gini",
    ),
    license="CC BY 4.0", kind="ddf",
    citation="Free data from Gapminder.org (Fast Track), CC BY 4.0",
    extra={"pattern": "countries_etc_datapoints/ddf--datapoints--{i}--by--country--time.csv",
           "entities": "ddf--entities--geo--country.csv", "geo_col": "country"},
)

WDI = Source(
    key="wdi", name="World Development Indicators", publisher="World Bank (via Open Numbers)",
    url=f"{GH}/open-numbers/ddf--open_numbers--world_development_indicators/master",
    files=(
        "it_net_user_zs", "sh_xpd_chex_pp_cd", "sp_urb_totl_in_zs", "gb_xpd_rsdv_gd_zs", "eg_elc_accs_zs",
        "ag_lnd_frst_zs", "sh_med_phys_zs", "sp_pop_65up_to_zs", "it_cel_sets_p2", "ne_trd_gnfs_zs",
        "bx_trf_pwkr_dt_gd_zs", "en_pop_dnst",
    ),
    license="CC BY 4.0", kind="ddf",
    citation="The World Bank: World Development Indicators (via Open Numbers), CC BY 4.0",
    extra={"pattern": "datapoints/ddf--datapoints--{i}--by--geo--time.csv", "geo_col": "geo"},
)

OWID_CO2 = Source(
    key="owid_co2", name="CO2 and greenhouse gas emissions", publisher="Our World in Data",
    url=f"{GH}/owid/co2-data/master", files=("owid-co2-data.csv",),
    license="CC BY 4.0", kind="csv",
    citation="Our World in Data, CO2 and Greenhouse Gas Emissions dataset, CC BY 4.0",
)

OWID_ENERGY = Source(
    key="owid_energy", name="Energy mix", publisher="Our World in Data",
    url=f"{GH}/owid/energy-data/master", files=("owid-energy-data.csv",),
    license="CC BY 4.0", kind="csv",
    citation="Our World in Data, Energy dataset (Energy Institute, Ember and others), CC BY 4.0",
)

FOOTBALL = Source(
    key="football", name="International football results, 1872 to date", publisher="Mart Jürisoo",
    url=f"{GH}/martj42/international_results/master", files=("results.csv",),
    license="CC0 1.0", kind="csv",
    citation="Mart Jürisoo, International football results from 1872 (CC0)",
)

OLYMPICS = Source(
    key="olympics", name="Olympic results, 1896 to 2022", publisher="Olympedia, compiled by Keith Galli",
    url=f"{GH}/KeithGalli/Olympics-Dataset/master", files=("clean-data/results.csv",),
    license="MIT (repository); results are public facts", kind="csv",
    citation="Olympedia.org results, compiled in KeithGalli/Olympics-Dataset",
)

EUROVISION = Source(
    key="eurovision", name="Eurovision Song Contest votes, 1975 to 2022", publisher="TidyTuesday (Data.World, eurovision.tv)",
    url=f"{GH}/rfordatascience/tidytuesday/master/data/2022/2022-05-17", files=("eurovision-votes.csv",),
    license="Public facts, cited", kind="csv",
    citation="TidyTuesday 2022-05-17, Eurovision votes (from Data.World / eurovision.tv)",
)

NOBEL = Source(
    key="nobel", name="Nobel laureates, 1901 to 2016", publisher="Nobel Prize data via TidyTuesday",
    url=f"{GH}/rfordatascience/tidytuesday/master/data/2019/2019-05-14", files=("nobel_winners.csv",),
    license="CC0 (Nobel Prize data)", kind="csv",
    citation="Nobel laureate data (nobelprize.org, CC0) via TidyTuesday 2019-05-14",
)

PASSPORTS = Source(
    key="passports", name="Passport Index", publisher="Passport Index Data (imorte)",
    url=f"{GH}/imorte/passport-index-data/main", files=("passport-index-tidy-iso3.csv",),
    license="MIT", kind="csv",
    citation="imorte/passport-index-data (MIT), updated February 2026",
)

BIGMAC = Source(
    key="bigmac", name="The Big Mac index", publisher="The Economist",
    url=f"{GH}/TheEconomist/big-mac-data/master", files=("output-data/big-mac-full-index.csv",),
    license="CC BY 4.0", kind="csv",
    citation="The Economist, The Big Mac index, CC BY 4.0",
)

COUNTRIES = Source(
    key="countries", name="Country borders and languages", publisher="mledoze/countries",
    url=f"{GH}/mledoze/countries/master", files=("countries.json",),
    license="ODbL 1.0", kind="json",
    citation="Contains information from mledoze/countries, made available under the ODbL",
)

SOURCES = (GAPMINDER, WDI, OWID_CO2, OWID_ENERGY, FOOTBALL, OLYMPICS, EUROVISION, NOBEL, PASSPORTS, BIGMAC, COUNTRIES)
