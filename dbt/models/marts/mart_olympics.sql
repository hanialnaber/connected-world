-- Summer Games 2000 to 2020: medals vs what population and income predict.
select
    o.iso3, d.country_name, d.region_4, d.population, d.gdp_pcap,
    coalesce(m.gold, 0) as gold, coalesce(m.silver, 0) as silver, coalesce(m.bronze, 0) as bronze,
    o.actual as medals, o.expected as expected_medals,
    o.actual - o.expected as medals_above_expected,
    (o.actual + 1) / (o.expected + 1) as performance_ratio,
    o.actual / (d.population / 1e6) as medals_per_million,
    o.r_squared, o.n_countries
from {{ ref('mart_overperformers') }} o
join {{ ref('dim_country') }} d using (iso3)
left join {{ ref('int_olympics__country_medals') }} m using (iso3)
where o.model = 'olympics'
