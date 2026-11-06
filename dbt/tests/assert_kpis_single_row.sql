select count(*) as n from {{ ref('mart_headline_kpis') }} having count(*) <> 1
