-- Each team's rating after its latest match. Active = at least 5 rated matches since the start of 2023.
with last_match as (
    select team, arg_max(rating_after, match_id) as rating, max(match_date) as rated_at,
           any_value(team_code) as team_code,
           count(*) filter (where match_date >= date '2023-01-01') as matches_since_2023,
           count(*) as matches_rated
    from {{ ref('int_football__elo') }}
    group by 1
), year_2000 as (
    select team, arg_max(rating_after, match_id) as rating_2000
    from {{ ref('int_football__elo') }}
    where match_date <= date '2000-12-31'
    group by 1
)
select
    l.team,
    l.team_code,
    case when l.team_code like 'GB-%' then null else l.team_code end as iso3,
    l.rating,
    l.rated_at,
    l.matches_rated,
    l.matches_since_2023,
    l.matches_since_2023 >= 5                          as is_active,
    y.rating_2000,
    l.rating - y.rating_2000                           as change_since_2000,
    case when l.matches_since_2023 >= 5
         then rank() over (partition by l.matches_since_2023 >= 5 order by l.rating desc) end as world_rank
from last_match l
left join year_2000 y using (team)
