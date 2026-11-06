-- World Development Indicators in long form; regional aggregates (wld, eas, ...) fall out on the join.
select
    c.iso3,
    d.year,
    d.indicator,
    d.value
from {{ source('bronze', 'wdi_datapoints') }} d
join {{ ref('stg_gapminder__countries') }} c on lower(c.iso3) = d.geo
where d.year <= {{ var('max_year') }}
