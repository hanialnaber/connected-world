-- Latest Big Mac price per country and how many Big Macs a day of GDP per person buys.
-- GDP per person is The Economist's own series, so price and income share one source.
-- Only the latest survey is used, so every price comes from the same date.
with latest as (
    select iso3, price_date
    from {{ ref('stg_bigmac__prices') }}
    where gdp_per_person_usd is not null and iso3 <> 'EUZ'
      and price_date = (select max(price_date) from {{ ref('stg_bigmac__prices') }} where gdp_per_person_usd is not null)
)
select
    p.iso3, p.country_name, d.region_4,
    p.price_date, p.local_price, p.dollar_price, p.gdp_per_person_usd,
    p.gdp_per_person_usd / 365 / p.dollar_price as big_macs_per_day_of_income
from {{ ref('stg_bigmac__prices') }} p
join latest using (iso3, price_date)
left join {{ ref('dim_country') }} d on d.iso3 = p.iso3
