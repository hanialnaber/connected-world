-- Every international result since 1872, with both teams mapped to the country dimension.
-- Regional and diaspora teams (CONIFA etc.) map to nothing and are excluded downstream.
with r as (
    select *, row_number() over (order by date, home_team, away_team, tournament) as match_id
    from {{ source('bronze', 'football') }}
    where home_score is not null and away_score is not null
)
select
    r.match_id,
    r.date                          as match_date,
    r.home_team,
    r.away_team,
    r.home_score::integer           as home_score,
    r.away_score::integer           as away_score,
    r.tournament,
    r.neutral                       as is_neutral,
    nullif(h.iso3, '')              as home_code,
    nullif(a.iso3, '')              as away_code
from r
left join {{ ref('country_aliases') }} h on h.alias = r.home_team
left join {{ ref('country_aliases') }} a on a.alias = r.away_team
