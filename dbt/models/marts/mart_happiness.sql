select
    o.iso3, d.country_name, d.region_4, d.population,
    d.gdp_pcap, o.actual as happiness, o.expected as expected_happiness,
    o.residual, o.residual_z, o.r_squared, o.n_countries
from {{ ref('mart_overperformers') }} o
join {{ ref('dim_country') }} d using (iso3)
where o.model = 'happiness'
