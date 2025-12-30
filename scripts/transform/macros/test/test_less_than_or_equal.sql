{% test less_than_or_equal(model, column_name, compare_column) %}

select
    *
from {{ model }}
where {{ column_name }} > {{ compare_column }}

{% endtest %}

