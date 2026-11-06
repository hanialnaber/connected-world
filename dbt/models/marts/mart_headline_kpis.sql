with p as (select * from {{ ref('mart_connection_pairs') }}),
strong as (
    select count(*) as strong_links, count(*) filter (where is_explained_by_income) as explained
    from p where indicator_a <> 'gdp_pcap' and indicator_b <> 'gdp_pcap' and abs(rho) >= 0.5 and n_countries >= {{ var('min_countries_per_link') }}
)
select
    (select count(*) from {{ ref('mart_source_coverage') }})                         as sources,
    (select sum(rows) from {{ ref('mart_source_coverage') }})                        as source_rows,
    (select count(*) from {{ ref('dim_country') }} where population >= 5e5)          as countries,
    (select count(*) from {{ ref('mart_connection_nodes') }})                        as indicators,
    (select count(*) from p)                                                         as pairs_tested,
    (select count(*) from p where is_link_beyond_income)                             as links_beyond_income,
    strong.strong_links,
    strong.explained                                                                 as strong_links_explained_by_income,
    strong.explained / strong.strong_links                                           as share_explained_by_income,
    (select count(*) from {{ ref('int_football__elo') }}) / 2                         as football_matches_rated,
    (select max(match_date) from {{ ref('int_football__elo') }})                     as football_through,
    (select count(*) from {{ ref('int_olympics__country_medals') }})                 as olympic_medal_countries
from strong
