-- Country-to-country points in Eurovision finals; self-vote placeholder rows are dropped.
select
    v.year                          as contest_year,
    v.jury_or_televoting            as vote_type,
    v.from_country,
    v.to_country,
    nullif(f.iso3, '')              as from_iso3,
    nullif(t.iso3, '')              as to_iso3,
    v.points::integer               as points
from {{ source('bronze', 'eurovision') }} v
left join {{ ref('country_aliases') }} f on f.alias = v.from_country
left join {{ ref('country_aliases') }} t on t.alias = v.to_country
where v.semi_final = 'f'
  and v.from_country <> v.to_country
