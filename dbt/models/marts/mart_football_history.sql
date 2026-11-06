-- Year-end ratings since 1990 for today's top 8 and the biggest risers since 2000.
with picks as (
    select team from {{ ref('int_football__current_ratings') }} where is_active and world_rank <= 8
    union
    select team from (
        select team from {{ ref('int_football__current_ratings') }}
        where is_active and change_since_2000 is not null order by change_since_2000 desc limit 4
    )
), year_end as (
    select team, year(match_date) as year, arg_max(rating_after, match_id) as rating
    from {{ ref('int_football__elo') }}
    where team in (select team from picks) and year(match_date) >= 1990
    group by 1, 2
)
select * from year_end
