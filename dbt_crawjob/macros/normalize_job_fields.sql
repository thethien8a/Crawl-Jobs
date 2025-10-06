{% macro normalize_salary(salary_column, source_type='generic') %}
  case 
    when {{ salary_column }} is null or trim({{ salary_column }}) = '' then null
    
    -- Common patterns across all sources
    when lower({{ salary_column }}) like '%thỏa thuận%' 
      or lower({{ salary_column }}) like '%thoa thuan%' 
      or lower({{ salary_column }}) like '%negotiable%' then 'Negotiable'
    
    when lower({{ salary_column }}) like '%cạnh tranh%' 
      or lower({{ salary_column }}) like '%competitive%' then 'Competitive'
    
    {% if source_type == 'joboko' %}
    -- JobOKO specific patterns
    when lower({{ salary_column }}) like '%thỏa thuận%' then 'Negotiable'
    
    {% elif source_type == 'topcv' %}
    -- TopCV specific patterns
    when lower({{ salary_column }}) like '%up to%' then trim({{ salary_column }})
    when {{ salary_column }} ~ '\d+\s*-\s*\d+\s*triệu' 
      then regexp_replace({{ salary_column }}, '\s+', ' ', 'g')
    
    {% elif source_type == 'vietnamworks' %}
    -- VietnamWorks specific patterns
    when lower({{ salary_column }}) like '%you%ll love it%' then 'Attractive'
    when {{ salary_column }} like '%USD%' or {{ salary_column }} like '%$%' 
      then trim({{ salary_column }})
    
    {% endif %}
    
    else trim({{ salary_column }})
  end
{% endmacro %}


{% macro normalize_experience(exp_column, source_type='generic') %}
  case 
    when {{ exp_column }} is null then null
    
    -- Common entry level patterns
    when lower({{ exp_column }}) like '%không yêu cầu%' 
      or lower({{ exp_column }}) like '%no experience%'
      or lower({{ exp_column }}) like '%entry level%'
      or lower({{ exp_column }}) like '%chưa có kinh nghiệm%' then 'Entry Level'
    
    {% if source_type == 'joboko' %}
    -- JobOKO specific experience patterns
    when lower({{ exp_column }}) like '%dưới 1 năm%' then '< 1 year'
    when lower({{ exp_column }}) like '%1-2 năm%' or lower({{ exp_column }}) like '%1 - 2%' then '1-2 years'
    when lower({{ exp_column }}) like '%2-5 năm%' or lower({{ exp_column }}) like '%2 - 5%' then '2-5 years'
    when lower({{ exp_column }}) like '%trên 5 năm%' or lower({{ exp_column }}) like '%> 5%' then '5+ years'
    
    {% elif source_type == 'topcv' %}
    -- TopCV specific experience patterns
    when lower({{ exp_column }}) like '%dưới 1 năm%' then '< 1 year'
    when lower({{ exp_column }}) like '%1 năm%' then '1 year'
    when lower({{ exp_column }}) like '%2 năm%' then '2 years'
    when lower({{ exp_column }}) like '%3 năm%' then '3 years'
    when lower({{ exp_column }}) like '%trên 5 năm%' then '5+ years'
    
    {% elif source_type == 'vietnamworks' %}
    -- VietnamWorks specific patterns (English terms)
    when lower({{ exp_column }}) like '%experienced%' or lower({{ exp_column }}) like '%professional%' then 'Experienced'
    when lower({{ exp_column }}) like '%manager%' then 'Manager'
    when lower({{ exp_column }}) like '%senior%' then 'Senior'
    when lower({{ exp_column }}) like '%junior%' then 'Junior'
    
    {% endif %}
    
    else trim({{ exp_column }})
  end
{% endmacro %}


{% macro clean_whitespace(text_column) %}
  trim(regexp_replace({{ text_column }}, '\s+', ' ', 'g'))
{% endmacro %}


{% macro normalize_deadline(deadline_column) %}
  case 
    when {{ deadline_column }} is null or trim({{ deadline_column }}) = '' then null
    when {{ deadline_column }} ~ '^\d{1,2}/\d{1,2}/\d{4}$' then {{ deadline_column }}
    else null
  end
{% endmacro %}
