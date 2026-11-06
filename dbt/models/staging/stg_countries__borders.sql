-- Land borders as country pairs (mledoze/countries, ODbL). Kosovo appears as UNK there.
select distinct
    case when iso3 = 'UNK' then 'XKX' else iso3 end as iso3,
    case when b = 'UNK' then 'XKX' else b end       as neighbour_iso3
from {{ source('bronze', 'countries') }}, unnest(borders::varchar[]) as t(b)
