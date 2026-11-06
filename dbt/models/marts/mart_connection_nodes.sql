-- One node per indicator for the connections map: domain, coverage, how closely it follows income,
-- and how many links it keeps once income is held fixed.
with p as (select * from {{ ref('mart_connection_pairs') }}),
ends as (
    select indicator_a as indicator, indicator_b as other, rho, is_link_beyond_income, is_explained_by_income from p
    union all
    select indicator_b, indicator_a, rho, is_link_beyond_income, is_explained_by_income from p
),
cov as (select indicator, count(*) as countries from {{ ref('int_country_latest') }} group by 1)
select
    c.indicator, c.label, c.short_label, c.domain, c.unit, c.source,
    cov.countries,
    max(e.rho) filter (where e.other = 'gdp_pcap')           as rho_with_income,
    count(*) filter (where e.is_link_beyond_income)           as links_beyond_income,
    count(*) filter (where e.is_explained_by_income)          as links_explained_by_income
from {{ ref('indicator_catalog') }} c
left join ends e on e.indicator = c.indicator
left join cov on cov.indicator = c.indicator
where c.in_network
group by all
