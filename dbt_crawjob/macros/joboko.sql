{% macro joboko_normalize_salary(salary_column) %}
    case
    when salary_raw is null or trim(salary_raw) = '' then null
    when lower(salary_raw) like '%thỏa thuận%' or lower(salary_raw) like '%negotiable%' then 'Negotiable'
    when lower(salary_raw) like '%cạnh tranh%' or lower(salary_raw) like '%competitive%' then 'Competitive'
    else trim(salary_raw)
    end
{% endmacro %}