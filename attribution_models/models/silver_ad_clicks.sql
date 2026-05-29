{{ config(materialized='view') }}

select
    ingestion_id,
    json_value(raw_payload, '$.click_id') as click_id,
    json_value(raw_payload, '$.user_cookie_id') as user_cookie_id,
    json_value(raw_payload, '$.ad_network') as ad_network,
    json_value(raw_payload, '$.campaign_name') as campaign_name,
    cast(json_value(raw_payload, '$.cost_per_click') as number) as cost_per_click,
    cast(json_value(raw_payload, '$.timestamp') as number) as click_timestamp,
    ingested_at
from {{ source('oracle_bronze', 'bronze_ad_clicks') }}
