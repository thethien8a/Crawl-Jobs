{{ config(
    materialized='table',
    schema='gold',
    post_hook=[
        "DO $$ 
         BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'dim_dates_pk') THEN 
                ALTER TABLE {{ this }} ADD CONSTRAINT dim_dates_pk PRIMARY KEY (date_key); 
            END IF; 
         END $$;"
    ]
) }}

with date_series as (
    select generate_series(
        '2025-01-01'::date,
        '2035-12-31'::date,
        '1 day'::interval
    )::date as date_day
),

final as (
    select
        date_day as date_key,
        date_day as full_date,
        extract(day from date_day) as day,
        extract(month from date_day) as month,
        to_char(date_day, 'Month') as month_name,
        extract(quarter from date_day) as quarter,
        extract(year from date_day) as year,
        extract(dow from date_day) as day_of_week,
        to_char(date_day, 'Day') as day_name,
        case 
            when extract(dow from date_day) in (0, 6) then true 
            else false 
        end as is_weekend
    from date_series
)

select * from final

