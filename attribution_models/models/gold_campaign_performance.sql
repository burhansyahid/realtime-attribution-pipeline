{{ config(materialized='table') }}

with clicks as (
    select * from {{ ref('silver_ad_clicks') }}
),

conversions as (
    select * from {{ ref('silver_conversions') }}
),

-- Join the clicks and conversions based on the user's cookie ID
joined_data as (
    select
        c.ad_network,
        c.campaign_name,
        c.cost_per_click,
        conv.revenue_usd,
        case when conv.order_id is not null then 1 else 0 end as is_conversion
    from clicks c
    left join conversions conv
        on c.user_cookie_id = conv.user_cookie_id
        -- Ensure the purchase happened AFTER the ad click
        and conv.conversion_timestamp >= c.click_timestamp 
)

-- Aggregate the final metrics
select
    ad_network,
    campaign_name,
    count(*) as total_clicks,
    sum(cost_per_click) as total_spend,
    sum(is_conversion) as total_conversions,
    coalesce(sum(revenue_usd), 0) as total_revenue,
    case
        when sum(cost_per_click) = 0 then 0
        else round(coalesce(sum(revenue_usd), 0) / sum(cost_per_click), 2)
    end as roas
from joined_data
group by
    ad_network,
    campaign_name
order by
    total_revenue desc
