{% macro clean_job_position(column_name) %}
    {% set cleaned_col = "LOWER(" ~ remove_accents(column_name) ~ ")" %}
    
    CASE 
        -- Executive / C-Level
        WHEN {{ cleaned_col }} ~ '(giam doc|cap cao hon|truong chi nhanh|c-level|executive)' THEN 'Giám đốc'
        
        -- Managerial
        WHEN {{ cleaned_col }} ~ '(truong phong|pho phong|quan ly|truong/pho phong|manager)' THEN 'Trưởng phòng'
        
        -- Team Lead / Supervisory
        WHEN {{ cleaned_col }} ~ '(truong nhom|giam sat|quan ly / giam sat|truong nhom / giam sat|supervisor|lead)' THEN 'Trưởng nhóm'
        
        -- Staff / Entry-Level (Including Fresh Graduates)
        WHEN {{ cleaned_col }} ~ '(nhan vien|chuyên viên|chuyen vien|nhan vien/chuyen vien|moi tot nghiep|fresh graduate|staff|officer)' THEN 'Nhân viên'
        
        -- Internship / Student
        WHEN {{ cleaned_col }} ~ '(intern|thuc tap sinh|sinh vien|thuc tap sinh/sinh vien|sinh vien/ thuc tap sinh)' THEN 'Thực tập sinh'
        
        ELSE 'Không đề cập'
    END as job_position
{% endmacro %}
