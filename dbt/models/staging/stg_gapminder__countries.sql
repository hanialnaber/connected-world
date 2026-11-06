-- One row per Gapminder geo entity that is a present-day country, keyed by ISO 3166 alpha-3.
-- Kosovo has no ISO code; it gets the widely used user-assigned XKX.
select
    country                                                        as gapminder_geo,
    coalesce(iso3166_1_alpha3, case when country = 'kos' then 'XKX' end) as iso3,
    name                                                           as country_name,
    world_4region                                                  as region_4,
    world_6region                                                  as region_6,
    income_groups                                                  as income_group,
    try_cast(landlocked = 'landlocked' as boolean)                 as is_landlocked,
    try_cast(latitude as double)                                   as latitude,
    try_cast(longitude as double)                                  as longitude,
    try_cast(un_state as boolean)                                  as is_un_state
from {{ source('bronze', 'gapminder_countries') }}
where "is--country" = 'TRUE'
  and coalesce(iso3166_1_alpha3, case when country = 'kos' then 'XKX' end) is not null
