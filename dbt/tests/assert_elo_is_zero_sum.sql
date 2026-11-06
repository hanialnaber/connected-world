-- Elo only moves points between the two teams in a match, so all changes must sum to zero.
select sum(rating_change) as total_change
from {{ ref('int_football__elo') }}
having abs(sum(rating_change)) > 1e-6
