-- Conformed country dimension: every analysis joins on iso3 from here.
with pop as (
    select iso3, arg_max(value, year) as population, max(year) as population_year
    from {{ ref('stg_gapminder__datapoints') }}
    where indicator = 'pop'
    group by 1
), gdp as (
    select iso3, arg_max(value, year) as gdp_pcap
    from {{ ref('stg_gapminder__datapoints') }}
    where indicator = 'gdp_pcap'
    group by 1
)
select
    c.iso3,
    c.country_name,
    c.region_4,
    c.region_6,
    c.income_group,
    c.is_landlocked,
    c.is_un_state,
    c.latitude,
    c.longitude,
    pop.population,
    pop.population_year,
    gdp.gdp_pcap
from {{ ref('stg_gapminder__countries') }} c
left join pop using (iso3)
left join gdp using (iso3)
