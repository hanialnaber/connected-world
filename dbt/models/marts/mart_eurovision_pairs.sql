-- Average points one country gives another per final in which both took part (1975 to 2022),
-- with land-border and shared-language flags from mledoze/countries.
with yearly as (
    select contest_year, from_iso3, to_iso3, sum(points) as points
    from {{ ref('stg_eurovision__votes') }}
    where from_iso3 is not null and to_iso3 is not null
    group by 1, 2, 3
), pairs as (
    select from_iso3, to_iso3, count(*) as finals_together, avg(points) as avg_points
    from yearly group by 1, 2
)
select
    p.*,
    f.country_name as from_country, t.country_name as to_country,
    exists (select 1 from {{ ref('stg_countries__borders') }} b where b.iso3 = p.from_iso3 and b.neighbour_iso3 = p.to_iso3) as shares_border,
    exists (select 1 from {{ ref('stg_countries__languages') }} a join {{ ref('stg_countries__languages') }} b
            on a.language = b.language and a.language <> 'English'
            where a.iso3 = p.from_iso3 and b.iso3 = p.to_iso3)                                         as shares_language
from pairs p
left join {{ ref('dim_country') }} f on f.iso3 = p.from_iso3
left join {{ ref('dim_country') }} t on t.iso3 = p.to_iso3
where p.finals_together >= 10
