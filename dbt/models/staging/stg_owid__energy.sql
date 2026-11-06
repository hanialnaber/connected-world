select
    coalesce(iso_code, case when country = 'World' then 'OWID_WRL' end) as iso3,
    year::integer                    as year,
    solar_share_elec::double         as solar_share_elec,
    wind_share_elec::double          as wind_share_elec,
    renewables_share_elec::double    as renewables_share_elec,
    low_carbon_share_elec::double    as low_carbon_share_elec,
    energy_per_capita::double        as energy_per_capita,
    electricity_generation::double   as electricity_generation_twh
from {{ source('bronze', 'owid_energy') }}
where length(iso_code) = 3 or country = 'World'
