-- Gapminder Fast Track series in long form. Projections beyond max_year are dropped.
select
    c.iso3,
    d.year,
    d.indicator,
    d.value
from {{ source('bronze', 'gapminder_datapoints') }} d
join {{ ref('stg_gapminder__countries') }} c on c.gapminder_geo = d.geo
where d.year <= {{ var('max_year') }}
