-- Current Elo ratings for active teams, with what population and income would predict (where the
-- team is a country; England, Scotland, Wales and Northern Ireland are rated but not modelled).
select
    r.team, r.team_code, r.iso3, d.country_name, d.population, d.gdp_pcap,
    r.rating, r.world_rank, r.rated_at, r.matches_rated, r.change_since_2000,
    o.expected as expected_rating, o.residual as rating_above_expected, o.residual_z,
    o.r_squared, o.n_countries
from {{ ref('int_football__current_ratings') }} r
left join {{ ref('dim_country') }} d on d.iso3 = r.iso3
left join {{ ref('mart_overperformers') }} o on o.iso3 = r.iso3 and o.model = 'football'
where r.is_active
