select
    o.iso3, d.country_name, d.region_4, d.population,
    w.value as health_spend_per_person, o.actual as life_expectancy,
    o.expected as expected_life_expectancy, o.residual, o.residual_z, o.r_squared
from {{ ref('mart_overperformers') }} o
join {{ ref('dim_country') }} d using (iso3)
join {{ ref('int_country_latest') }} w on w.iso3 = o.iso3 and w.indicator = 'sh_xpd_chex_pp_cd'
where o.model = 'health'
