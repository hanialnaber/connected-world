-- Fail the build if a source stops mapping onto the country dimension (a renamed country, a new code).
-- Excluded on purpose: historical states (Yugoslavia, Serbia & Montenegro) and non-FIFA football teams.
select source, mapped_share
from {{ ref('mart_source_coverage') }}
where (source = 'Olympic results' and mapped_share < 0.99)
   or (source = 'Eurovision votes (finals)' and mapped_share < 0.97)
   or (source = 'Nobel laureates' and mapped_share < 0.99)
   or (source = 'International football results' and mapped_share < 0.90)
