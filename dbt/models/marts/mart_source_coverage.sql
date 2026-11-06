-- What each source contributes and how much of it maps onto the country dimension.
with s as (
    select 'Gapminder Fast Track' as source, count(*) as rows, count(distinct iso3) as countries, min(year) as first_year, max(year) as last_year, 1.0 as mapped_share from {{ ref('stg_gapminder__datapoints') }}
    union all select 'World Bank WDI', count(*), count(distinct iso3), min(year), max(year), 1.0 from {{ ref('stg_wdi__datapoints') }}
    union all select 'Our World in Data: CO2', count(*), count(distinct iso3), min(year), max(year), 1.0 from {{ ref('stg_owid__co2') }}
    union all select 'Our World in Data: energy', count(*), count(distinct iso3), min(year), max(year), 1.0 from {{ ref('stg_owid__energy') }}
    union all select 'International football results', count(*), count(distinct home_code), min(year(match_date)), max(year(match_date)),
        avg((home_code is not null and away_code is not null)::int) from {{ ref('stg_football__results') }}
    union all select 'Olympic results', count(*), count(distinct iso3), min(games_year), max(games_year),
        avg((iso3 is not null)::int) filter (where games_year >= 2000) from {{ ref('stg_olympics__results') }}
    union all select 'Eurovision votes (finals)', count(*), count(distinct from_iso3), min(contest_year), max(contest_year),
        avg((from_iso3 is not null and to_iso3 is not null)::int) from {{ ref('stg_eurovision__votes') }}
    union all select 'Nobel laureates', count(*), count(distinct birth_iso3), min(prize_year), max(prize_year),
        avg((birth_iso3 is not null)::int) from {{ ref('stg_nobel__laureates') }}
    union all select 'Passport Index', count(*), count(distinct passport_iso3), 2026, 2026, 1.0 from {{ ref('stg_passports__requirements') }}
    union all select 'Big Mac index', count(*), count(distinct iso3), min(year(price_date)), max(year(price_date)), 1.0 from {{ ref('stg_bigmac__prices') }}
    union all select 'Borders and languages', (select count(*) from {{ source('bronze', 'countries') }}), count(distinct iso3), null, null, 1.0 from {{ ref('stg_countries__borders') }}
)
select * from s
