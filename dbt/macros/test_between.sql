{# Generic test: every non-null value must sit inside [min_value, max_value]. #}
{% test between(model, column_name, min_value, max_value) %}
select {{ column_name }} as offending_value
from {{ model }}
where {{ column_name }} is not null
  and ({{ column_name }} < {{ min_value }} or {{ column_name }} > {{ max_value }})
{% endtest %}
