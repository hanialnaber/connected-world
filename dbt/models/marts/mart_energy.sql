-- Solar and wind's share of electricity, 2015 vs latest, for countries generating 5 TWh+.
with e as (select * from {{ ref('stg_owid__energy') }}),
latest as (
    select iso3, max(year) as year from e where solar_share_elec is not null and wind_share_elec is not null group by 1
)
select
    case when l.iso3 = 'OWID_WRL' then 'WLD' else l.iso3 end as iso3,
    coalesce(d.country_name, 'World') as country_name, l.year as latest_year,
    s15.solar_share_elec + s15.wind_share_elec as solar_wind_2015,
    sl.solar_share_elec + sl.wind_share_elec   as solar_wind_latest,
    sl.solar_share_elec as solar_latest, sl.wind_share_elec as wind_latest,
    (sl.solar_share_elec + sl.wind_share_elec) - (s15.solar_share_elec + s15.wind_share_elec) as change_pts,
    sl.electricity_generation_twh
from latest l
join e sl on sl.iso3 = l.iso3 and sl.year = l.year
join e s15 on s15.iso3 = l.iso3 and s15.year = 2015
left join {{ ref('dim_country') }} d on d.iso3 = l.iso3
where sl.electricity_generation_twh >= 5 and (d.iso3 is not null or l.iso3 = 'OWID_WRL')
