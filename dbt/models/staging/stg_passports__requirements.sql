-- Passport x destination entry rules. A numeric value is the number of visa-free days.
select
    Passport                        as passport_iso3,
    Destination                     as destination_iso3,
    Requirement                     as requirement,
    case
        when Requirement = '-1' then 'own country'
        when Requirement = 'no admission' then 'no admission'
        when Requirement in ('visa free') or regexp_matches(Requirement, '^[0-9]+$') then 'visa free'
        when Requirement in ('visa on arrival', 'eta') then Requirement
        when Requirement = 'e-visa' then 'e-visa'
        else 'visa required'
    end                             as entry_type,
    (Requirement in ('visa free', 'visa on arrival', 'eta') or regexp_matches(Requirement, '^[0-9]+$'))
                                    as is_without_prior_visa
from {{ source('bronze', 'passports') }}
