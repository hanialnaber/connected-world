-- Science laureates (Physics, Chemistry, Medicine), 1901 to 2016: where they were born vs where
-- they worked when they won (first listed affiliation).
with sci as (
    select laureate_id, prize_year, category, any_value(birth_iso3) as birth_iso3,
           min(organization_iso3) as organization_iso3
    from {{ ref('stg_nobel__laureates') }}
    where category in ('Physics', 'Chemistry', 'Medicine')
    group by 1, 2, 3
), born as (
    select birth_iso3 as iso3, count(*) as born_here from sci where birth_iso3 is not null group by 1
), won as (
    select organization_iso3 as iso3, count(*) as won_here from sci where organization_iso3 is not null group by 1
), kept as (
    select birth_iso3 as iso3, count(*) as born_and_won_here from sci where birth_iso3 = organization_iso3 group by 1
)
select
    iso3, d.country_name,
    coalesce(born_here, 0) as born_here,
    coalesce(won_here, 0) as won_here,
    coalesce(born_and_won_here, 0) as born_and_won_here,
    coalesce(won_here, 0) - coalesce(born_here, 0) as net_gain
from born full outer join won using (iso3)
left join kept using (iso3)
left join {{ ref('dim_country') }} d using (iso3)
