-- Our World in Data CO2: countries only (OWID_ aggregates and regions have no 3-letter ISO code).
select
    iso_code                         as iso3,
    year::integer                    as year,
    population::double               as population,
    gdp::double                      as gdp_ppp,
    co2::double                      as co2_mt,
    co2_per_capita::double           as co2_per_capita,
    consumption_co2::double          as consumption_co2_mt,
    consumption_co2_per_capita::double as consumption_co2_per_capita
from {{ source('bronze', 'owid_co2') }}
where length(iso_code) = 3
