-- Latest value of each indicator per country, from latest_from_year onwards.
select
    iso3,
    indicator,
    arg_max(value, year)    as value,
    max(year)               as year,
    any_value(source)       as source
from {{ ref('int_indicators_long') }}
where year between {{ var('latest_from_year') }} and {{ var('max_year') }} + 1
  and value is not null
group by 1, 2
