-- Medals by country at the Summer Games 2000 to 2020 (Sydney to Tokyo).
-- A team event counts once per country, so a gold-winning relay squad is one gold, not four.
with medal_events as (
    select distinct games_year, event, iso3, medal
    from {{ ref('stg_olympics__results') }}
    where season = 'Summer'
      and games_year between 2000 and 2020
      and medal is not null
      and iso3 is not null
)
select
    iso3,
    count(*)                                        as medals,
    count(*) filter (where medal = 'Gold')          as gold,
    count(*) filter (where medal = 'Silver')        as silver,
    count(*) filter (where medal = 'Bronze')        as bronze,
    count(distinct games_year)                      as games_with_medals
from medal_events
group by 1
