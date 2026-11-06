-- Every country-level indicator in one long table: (iso3, indicator, year, value, source).
select iso3, indicator, year, value, 'Gapminder' as source
from {{ ref('stg_gapminder__datapoints') }}

union all
select iso3, indicator, year, value, 'World Bank'
from {{ ref('stg_wdi__datapoints') }}

union all
select iso3, 'co2_per_capita', year, co2_per_capita, 'Our World in Data'
from {{ ref('stg_owid__co2') }}
where co2_per_capita is not null and iso3 in (select iso3 from {{ ref('dim_country') }})

union all
select iso3, unnest(['energy_per_capita', 'renewables_share_elec']),
       year, unnest([energy_per_capita, renewables_share_elec]), 'Our World in Data'
from {{ ref('stg_owid__energy') }}
where iso3 in (select iso3 from {{ ref('dim_country') }})

union all
select m.iso3, 'olympic_medals_per_million', 2020, m.medals / (d.population / 1e6), 'Olympedia'
from {{ ref('int_olympics__country_medals') }} m join {{ ref('dim_country') }} d using (iso3)

union all
-- countries that never won a medal in 2000 to 2020 are real zeros, not missing values
select d.iso3, 'olympic_medals_per_million', 2020, 0, 'Olympedia'
from {{ ref('dim_country') }} d
where d.population >= 1e6 and d.iso3 not in (select iso3 from {{ ref('int_olympics__country_medals') }})

union all
select iso3, 'football_elo', year(rated_at), rating, 'International results (Elo)'
from {{ ref('int_football__current_ratings') }} where iso3 is not null and is_active

union all
select iso3, unnest(['passport_power', 'passport_openness']), 2026,
       unnest([passport_power, passport_openness]), 'Passport Index'
from {{ ref('int_passports__scores') }}
