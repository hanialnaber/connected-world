select distinct
    case when iso3 = 'UNK' then 'XKX' else iso3 end as iso3,
    lang                                            as language
from {{ source('bronze', 'countries') }}, unnest(languages::varchar[]) as t(lang)
