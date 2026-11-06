-- Passport power = destinations a holder can enter without arranging a visa in advance
-- (visa free, visa on arrival or electronic travel authorisation). Openness is the mirror image:
-- how many passports a destination admits on those terms.
with r as (
    select * from {{ ref('stg_passports__requirements') }} where entry_type <> 'own country'
)
select
    p.iso3,
    coalesce(pw.power, 0)       as passport_power,
    coalesce(op.openness, 0)    as passport_openness
from {{ ref('dim_country') }} p
left join (select passport_iso3 as iso3, count(*) filter (where is_without_prior_visa) as power from r group by 1) pw using (iso3)
left join (select destination_iso3 as iso3, count(*) filter (where is_without_prior_visa) as openness from r group by 1) op using (iso3)
where p.iso3 in (select passport_iso3 from r)
