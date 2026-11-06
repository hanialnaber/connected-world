with sci as (
    select laureate_id, prize_year, category, any_value(birth_iso3) as birth_iso3,
           min(organization_iso3) as organization_iso3
    from {{ ref('stg_nobel__laureates') }}
    where category in ('Physics', 'Chemistry', 'Medicine')
    group by 1, 2, 3
)
select
    birth_iso3, b.country_name as birth_country,
    organization_iso3, o.country_name as organization_country,
    count(*) as laureates
from sci
left join {{ ref('dim_country') }} b on b.iso3 = sci.birth_iso3
left join {{ ref('dim_country') }} o on o.iso3 = sci.organization_iso3
where birth_iso3 is not null and organization_iso3 is not null and birth_iso3 <> organization_iso3
group by all
