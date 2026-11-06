select iso3, indicator, count(*) as n
from {{ ref('int_country_latest') }}
group by 1, 2
having count(*) > 1
