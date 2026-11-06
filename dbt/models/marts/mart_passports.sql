select
    s.iso3, d.country_name, d.region_4, d.population, d.gdp_pcap,
    s.passport_power, s.passport_openness,
    rank() over (order by s.passport_power desc) as power_rank,
    o.expected as expected_power, o.residual as power_above_expected, o.residual_z
from {{ ref('int_passports__scores') }} s
join {{ ref('dim_country') }} d using (iso3)
left join {{ ref('mart_overperformers') }} o on o.iso3 = s.iso3 and o.model = 'passports'
