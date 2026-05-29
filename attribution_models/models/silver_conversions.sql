{{ config(materialized='view') }}

select
    ingestion_id,
    json_value(raw_payload, '$.order_id') as order_id,
    json_value(raw_payload, '$.user_cookie_id') as user_cookie_id,
    cast(json_value(raw_payload, '$.revenue_usd') as number) as revenue_usd,
    cast(json_value(raw_payload, '$.timestamp') as number) as conversion_timestamp,
    ingested_at
from {{ source('oracle_bronze', 'bronze_conversions') }}
