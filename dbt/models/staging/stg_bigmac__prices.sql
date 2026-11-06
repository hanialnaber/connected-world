select
    date                            as price_date,
    iso_a3                          as iso3,
    name                            as country_name,
    local_price,
    dollar_ex,
    dollar_price,
    GDP_bigmac                      as gdp_per_person_usd
from {{ source('bronze', 'bigmac') }}
