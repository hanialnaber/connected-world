-- Olympic Games results only: Youth Olympic Games events are tagged "(YOG)" and dropped.
select
    year::integer                   as games_year,
    type                            as season,
    discipline,
    event,
    noc,
    nullif(x.iso3, '')              as iso3,
    athlete_id,
    medal
from {{ source('bronze', 'olympics') }} o
left join {{ ref('country_aliases') }} x on x.alias = 'IOC:' || o.noc
where o.event like '%(Olympic)'
