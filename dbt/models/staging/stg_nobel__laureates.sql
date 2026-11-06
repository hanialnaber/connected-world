-- One row per laureate and prize. Birth countries use the present-day country the Nobel data
-- records in brackets ("Prussia (Poland)" -> Poland); organisations (pre-award affiliation) likewise.
with base as (
    select distinct
        prize_year, category, laureate_id, full_name, laureate_type,
        birth_country, organization_country
    from {{ source('bronze', 'nobel') }}
    where laureate_type = 'Individual'
)
select
    b.prize_year,
    b.category,
    b.laureate_id,
    b.full_name,
    b.birth_country,
    -- the shared alias table maps Scotland etc. to football teams; laureates map to the UK
    case when bc.iso3 like 'GB-%' then 'GBR' else nullif(bc.iso3, '') end as birth_iso3,
    nullif(b.organization_country, 'NA') as organization_country,
    case when oc.iso3 like 'GB-%' then 'GBR' else nullif(oc.iso3, '') end as organization_iso3
from base b
left join {{ ref('country_aliases') }} bc on bc.alias = b.birth_country
left join {{ ref('country_aliases') }} oc on oc.alias = b.organization_country
