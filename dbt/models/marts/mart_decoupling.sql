-- Did the economy grow while emissions fell? 2005 vs the latest year with GDP (countries of 1M+).
with base as (
    select * from {{ ref('stg_owid__co2') }} where population >= 1e6
), latest_year as (
    select max(year) as y from base where gdp_ppp is not null
)
select
    a.iso3, d.country_name, d.region_4, b.year as latest_year,
    b.gdp_ppp / a.gdp_ppp - 1                         as gdp_change,
    b.co2_mt / a.co2_mt - 1                           as co2_change,
    b.consumption_co2_mt / a.consumption_co2_mt - 1   as consumption_co2_change,
    b.co2_per_capita                                  as co2_per_capita_latest,
    (b.gdp_ppp > a.gdp_ppp and b.co2_mt < a.co2_mt)   as is_decoupled_territorial,
    (b.gdp_ppp > a.gdp_ppp and b.co2_mt < a.co2_mt and b.consumption_co2_mt < a.consumption_co2_mt) as is_decoupled_both
from base a
join base b on b.iso3 = a.iso3 and b.year = (select y from latest_year)
join {{ ref('dim_country') }} d on d.iso3 = a.iso3
where a.year = 2005 and a.gdp_ppp is not null and b.gdp_ppp is not null and a.co2_mt > 0
