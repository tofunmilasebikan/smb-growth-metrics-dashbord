-- =============================================================================
-- SMB Growth Metrics Dashboard - ROI Analysis SQL Queries
-- =============================================================================
-- Database: DuckDB (chosen for excellent CSV handling and modern SQL support)
-- Input: analysis/cleaned_campaigns.csv
-- 
-- Why DuckDB over SQLite:
--   1. Native CSV reading without import steps
--   2. Modern SQL:2016 syntax (window functions, CTEs)
--   3. Columnar storage optimized for analytics
--   4. Faster aggregations on large datasets
-- =============================================================================

-- =============================================================================
-- SECTION A: Table Creation / Data Loading
-- =============================================================================

-- Create a view from the cleaned CSV (DuckDB reads CSV directly)
CREATE OR REPLACE VIEW campaigns AS 
SELECT * FROM read_csv_auto('analysis/cleaned_campaigns.csv');

-- Verify the data loaded correctly
SELECT COUNT(*) as total_campaigns FROM campaigns;

-- Preview the data
SELECT * FROM campaigns LIMIT 10;

-- =============================================================================
-- SECTION B: ROI Analysis by Segmentation Dimensions
-- =============================================================================

-- -----------------------------------------------------------------------------
-- B1: ROI by Campaign Type
-- -----------------------------------------------------------------------------
SELECT 
    campaign_type,
    COUNT(*) as campaign_count,
    ROUND(AVG(roi), 2) as avg_roi,
    ROUND(MIN(roi), 2) as min_roi,
    ROUND(MAX(roi), 2) as max_roi,
    ROUND(STDDEV(roi), 2) as stddev_roi,
    ROUND(AVG(ctr), 4) as avg_ctr,
    ROUND(AVG(conversion_rate), 4) as avg_conversion_rate,
    SUM(clicks) as total_clicks,
    SUM(impressions) as total_impressions
FROM campaigns
GROUP BY campaign_type
ORDER BY avg_roi DESC;

-- -----------------------------------------------------------------------------
-- B2: ROI by Target Audience
-- -----------------------------------------------------------------------------
SELECT 
    target_audience,
    COUNT(*) as campaign_count,
    ROUND(AVG(roi), 2) as avg_roi,
    ROUND(MIN(roi), 2) as min_roi,
    ROUND(MAX(roi), 2) as max_roi,
    ROUND(AVG(ctr), 4) as avg_ctr,
    ROUND(AVG(conversion_rate), 4) as avg_conversion_rate,
    SUM(clicks) as total_clicks,
    SUM(impressions) as total_impressions
FROM campaigns
GROUP BY target_audience
ORDER BY avg_roi DESC;

-- -----------------------------------------------------------------------------
-- B3: ROI by Location
-- -----------------------------------------------------------------------------
SELECT 
    location,
    COUNT(*) as campaign_count,
    ROUND(AVG(roi), 2) as avg_roi,
    ROUND(MIN(roi), 2) as min_roi,
    ROUND(MAX(roi), 2) as max_roi,
    ROUND(AVG(ctr), 4) as avg_ctr,
    ROUND(AVG(conversion_rate), 4) as avg_conversion_rate,
    SUM(clicks) as total_clicks,
    SUM(impressions) as total_impressions
FROM campaigns
GROUP BY location
ORDER BY avg_roi DESC;

-- -----------------------------------------------------------------------------
-- B4: ROI by Customer Segment
-- -----------------------------------------------------------------------------
SELECT 
    customer_segment,
    COUNT(*) as campaign_count,
    ROUND(AVG(roi), 2) as avg_roi,
    ROUND(MIN(roi), 2) as min_roi,
    ROUND(MAX(roi), 2) as max_roi,
    ROUND(AVG(ctr), 4) as avg_ctr,
    ROUND(AVG(conversion_rate), 4) as avg_conversion_rate,
    SUM(clicks) as total_clicks,
    SUM(impressions) as total_impressions
FROM campaigns
GROUP BY customer_segment
ORDER BY avg_roi DESC;

-- -----------------------------------------------------------------------------
-- B5: ROI by Channel Used
-- -----------------------------------------------------------------------------
SELECT 
    channel_used,
    COUNT(*) as campaign_count,
    ROUND(AVG(roi), 2) as avg_roi,
    ROUND(MIN(roi), 2) as min_roi,
    ROUND(MAX(roi), 2) as max_roi,
    ROUND(AVG(ctr), 4) as avg_ctr,
    ROUND(AVG(conversion_rate), 4) as avg_conversion_rate,
    SUM(clicks) as total_clicks,
    SUM(impressions) as total_impressions
FROM campaigns
GROUP BY channel_used
ORDER BY avg_roi DESC;

-- -----------------------------------------------------------------------------
-- B6: ROI by Company
-- -----------------------------------------------------------------------------
SELECT 
    company,
    COUNT(*) as campaign_count,
    ROUND(AVG(roi), 2) as avg_roi,
    ROUND(MIN(roi), 2) as min_roi,
    ROUND(MAX(roi), 2) as max_roi,
    ROUND(AVG(ctr), 4) as avg_ctr,
    ROUND(AVG(acquisition_cost), 2) as avg_acquisition_cost,
    SUM(clicks) as total_clicks,
    SUM(impressions) as total_impressions
FROM campaigns
GROUP BY company
ORDER BY avg_roi DESC;

-- =============================================================================
-- SECTION C: Campaign Performance Rankings
-- =============================================================================

-- -----------------------------------------------------------------------------
-- C1: Top 10 Campaigns by ROI
-- -----------------------------------------------------------------------------
SELECT 
    campaign_id,
    company,
    campaign_type,
    target_audience,
    channel_used,
    location,
    ROUND(roi, 2) as roi,
    ROUND(ctr, 4) as ctr,
    ROUND(conversion_rate, 4) as conversion_rate,
    clicks,
    impressions
FROM campaigns
ORDER BY roi DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- C2: Bottom 10 Campaigns by ROI
-- -----------------------------------------------------------------------------
SELECT 
    campaign_id,
    company,
    campaign_type,
    target_audience,
    channel_used,
    location,
    ROUND(roi, 2) as roi,
    ROUND(ctr, 4) as ctr,
    ROUND(conversion_rate, 4) as conversion_rate,
    clicks,
    impressions
FROM campaigns
ORDER BY roi ASC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- C3: High CTR but Low ROI (Vanity Metrics Alert)
-- These campaigns look good on engagement but don't deliver returns
-- -----------------------------------------------------------------------------
WITH percentiles AS (
    SELECT 
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY ctr) as ctr_p75,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY roi) as roi_p25
    FROM campaigns
)
SELECT 
    c.campaign_id,
    c.company,
    c.campaign_type,
    c.target_audience,
    c.channel_used,
    ROUND(c.ctr, 4) as ctr,
    ROUND(c.roi, 2) as roi,
    'High CTR / Low ROI' as alert_type
FROM campaigns c, percentiles p
WHERE c.ctr > p.ctr_p75 AND c.roi < p.roi_p25
ORDER BY c.ctr DESC
LIMIT 20;

-- -----------------------------------------------------------------------------
-- C4: Low CTR but High ROI (Hidden Gems - Niche Efficient Segments)
-- These campaigns don't get many clicks but convert well
-- -----------------------------------------------------------------------------
WITH percentiles AS (
    SELECT 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY ctr) as ctr_p25,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY roi) as roi_p75
    FROM campaigns
)
SELECT 
    c.campaign_id,
    c.company,
    c.campaign_type,
    c.target_audience,
    c.channel_used,
    ROUND(c.ctr, 4) as ctr,
    ROUND(c.roi, 2) as roi,
    'Low CTR / High ROI' as alert_type
FROM campaigns c, percentiles p
WHERE c.ctr < p.ctr_p25 AND c.roi > p.roi_p75
ORDER BY c.roi DESC
LIMIT 20;

-- =============================================================================
-- SECTION D: Time Trends (if date exists)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- D1: Monthly ROI Trend
-- -----------------------------------------------------------------------------
SELECT 
    DATE_TRUNC('month', date) as month,
    COUNT(*) as campaign_count,
    ROUND(AVG(roi), 2) as avg_roi,
    ROUND(MIN(roi), 2) as min_roi,
    ROUND(MAX(roi), 2) as max_roi,
    ROUND(STDDEV(roi), 2) as stddev_roi
FROM campaigns
WHERE date IS NOT NULL
GROUP BY DATE_TRUNC('month', date)
ORDER BY month;

-- -----------------------------------------------------------------------------
-- D2: Monthly CTR Trend
-- -----------------------------------------------------------------------------
SELECT 
    DATE_TRUNC('month', date) as month,
    COUNT(*) as campaign_count,
    ROUND(AVG(ctr), 4) as avg_ctr,
    SUM(clicks) as total_clicks,
    SUM(impressions) as total_impressions,
    ROUND(SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0), 4) as overall_ctr
FROM campaigns
WHERE date IS NOT NULL
GROUP BY DATE_TRUNC('month', date)
ORDER BY month;

-- -----------------------------------------------------------------------------
-- D3: Monthly Performance by Campaign Type
-- -----------------------------------------------------------------------------
SELECT 
    DATE_TRUNC('month', date) as month,
    campaign_type,
    COUNT(*) as campaign_count,
    ROUND(AVG(roi), 2) as avg_roi,
    ROUND(AVG(ctr), 4) as avg_ctr
FROM campaigns
WHERE date IS NOT NULL
GROUP BY DATE_TRUNC('month', date), campaign_type
ORDER BY month, campaign_type;

-- =============================================================================
-- SECTION E: Budget Reallocation Simulation
-- =============================================================================

-- -----------------------------------------------------------------------------
-- E1: Calculate Current "Budget Proxy" by Campaign Type
-- (Using acquisition_cost as spend proxy if available, else normalized ROI)
-- -----------------------------------------------------------------------------
WITH type_performance AS (
    SELECT 
        campaign_type,
        COUNT(*) as campaign_count,
        ROUND(AVG(roi), 2) as avg_roi,
        ROUND(SUM(COALESCE(acquisition_cost, 0)), 2) as total_spend,
        ROUND(AVG(COALESCE(acquisition_cost, 0)), 2) as avg_spend_per_campaign
    FROM campaigns
    GROUP BY campaign_type
),
ranked AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (ORDER BY avg_roi DESC) as roi_rank,
        ROW_NUMBER() OVER (ORDER BY avg_roi ASC) as worst_rank
    FROM type_performance
)
SELECT 
    campaign_type,
    campaign_count,
    avg_roi,
    total_spend,
    avg_spend_per_campaign,
    roi_rank,
    CASE 
        WHEN roi_rank = 1 THEN 'TOP PERFORMER - Consider increasing budget'
        WHEN worst_rank = 1 THEN 'LOWEST PERFORMER - Consider reducing budget'
        ELSE 'AVERAGE PERFORMER'
    END as recommendation
FROM ranked
ORDER BY roi_rank;

-- -----------------------------------------------------------------------------
-- E2: Budget Reallocation Proposal
-- Shift 15% from lowest ROI campaign type to highest ROI campaign type
-- -----------------------------------------------------------------------------
WITH type_stats AS (
    SELECT 
        campaign_type,
        AVG(roi) as avg_roi,
        SUM(COALESCE(acquisition_cost, 0)) as total_spend
    FROM campaigns
    GROUP BY campaign_type
),
best_worst AS (
    SELECT 
        (SELECT campaign_type FROM type_stats ORDER BY avg_roi DESC LIMIT 1) as best_type,
        (SELECT avg_roi FROM type_stats ORDER BY avg_roi DESC LIMIT 1) as best_roi,
        (SELECT total_spend FROM type_stats ORDER BY avg_roi DESC LIMIT 1) as best_spend,
        (SELECT campaign_type FROM type_stats ORDER BY avg_roi ASC LIMIT 1) as worst_type,
        (SELECT avg_roi FROM type_stats ORDER BY avg_roi ASC LIMIT 1) as worst_roi,
        (SELECT total_spend FROM type_stats ORDER BY avg_roi ASC LIMIT 1) as worst_spend
)
SELECT 
    best_type as top_performer,
    ROUND(best_roi, 2) as top_roi,
    worst_type as bottom_performer,
    ROUND(worst_roi, 2) as bottom_roi,
    ROUND(worst_spend * 0.15, 2) as budget_to_shift,
    ROUND((best_roi - worst_roi), 2) as roi_differential,
    ROUND(worst_spend * 0.15 * (best_roi - worst_roi) / 100, 2) as expected_uplift_estimate,
    '15% budget shift from worst to best performer' as strategy
FROM best_worst;

-- -----------------------------------------------------------------------------
-- E3: Segment-Level Optimization Opportunities
-- Find underperforming segments within each dimension
-- -----------------------------------------------------------------------------
WITH segment_performance AS (
    SELECT 
        'campaign_type' as dimension,
        campaign_type as segment,
        AVG(roi) as avg_roi,
        COUNT(*) as n
    FROM campaigns
    GROUP BY campaign_type
    
    UNION ALL
    
    SELECT 
        'target_audience' as dimension,
        target_audience as segment,
        AVG(roi) as avg_roi,
        COUNT(*) as n
    FROM campaigns
    GROUP BY target_audience
    
    UNION ALL
    
    SELECT 
        'channel_used' as dimension,
        channel_used as segment,
        AVG(roi) as avg_roi,
        COUNT(*) as n
    FROM campaigns
    GROUP BY channel_used
    
    UNION ALL
    
    SELECT 
        'customer_segment' as dimension,
        customer_segment as segment,
        AVG(roi) as avg_roi,
        COUNT(*) as n
    FROM campaigns
    GROUP BY customer_segment
),
overall_avg AS (
    SELECT AVG(roi) as overall_roi FROM campaigns
)
SELECT 
    sp.dimension,
    sp.segment,
    ROUND(sp.avg_roi, 2) as segment_roi,
    ROUND(o.overall_roi, 2) as overall_roi,
    ROUND(sp.avg_roi - o.overall_roi, 2) as roi_vs_avg,
    sp.n as campaign_count,
    CASE 
        WHEN sp.avg_roi > o.overall_roi * 1.1 THEN 'OUTPERFORMER (+10%+)'
        WHEN sp.avg_roi < o.overall_roi * 0.9 THEN 'UNDERPERFORMER (-10%+)'
        ELSE 'AVERAGE'
    END as status
FROM segment_performance sp, overall_avg o
ORDER BY sp.dimension, roi_vs_avg DESC;

-- =============================================================================
-- SECTION F: Summary Statistics for Dashboard
-- =============================================================================

-- -----------------------------------------------------------------------------
-- F1: Overall KPI Summary
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(*) as total_campaigns,
    SUM(impressions) as total_impressions,
    SUM(clicks) as total_clicks,
    ROUND(SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0), 4) as overall_ctr,
    ROUND(AVG(conversion_rate), 4) as avg_conversion_rate,
    ROUND(AVG(roi), 2) as avg_roi,
    ROUND(SUM(COALESCE(acquisition_cost, 0)), 2) as total_spend,
    ROUND(AVG(engagement_score), 2) as avg_engagement_score
FROM campaigns;

-- -----------------------------------------------------------------------------
-- F2: Performance Quadrant Analysis (CTR vs ROI)
-- -----------------------------------------------------------------------------
WITH medians AS (
    SELECT 
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ctr) as median_ctr,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY roi) as median_roi
    FROM campaigns
)
SELECT 
    CASE 
        WHEN c.ctr >= m.median_ctr AND c.roi >= m.median_roi THEN 'Stars (High CTR, High ROI)'
        WHEN c.ctr >= m.median_ctr AND c.roi < m.median_roi THEN 'Vanity (High CTR, Low ROI)'
        WHEN c.ctr < m.median_ctr AND c.roi >= m.median_roi THEN 'Hidden Gems (Low CTR, High ROI)'
        ELSE 'Dogs (Low CTR, Low ROI)'
    END as quadrant,
    COUNT(*) as campaign_count,
    ROUND(AVG(c.roi), 2) as avg_roi,
    ROUND(AVG(c.ctr), 4) as avg_ctr
FROM campaigns c, medians m
GROUP BY 
    CASE 
        WHEN c.ctr >= m.median_ctr AND c.roi >= m.median_roi THEN 'Stars (High CTR, High ROI)'
        WHEN c.ctr >= m.median_ctr AND c.roi < m.median_roi THEN 'Vanity (High CTR, Low ROI)'
        WHEN c.ctr < m.median_ctr AND c.roi >= m.median_roi THEN 'Hidden Gems (Low CTR, High ROI)'
        ELSE 'Dogs (Low CTR, Low ROI)'
    END
ORDER BY avg_roi DESC;

-- =============================================================================
-- END OF ANALYSIS
-- =============================================================================
-- To run this file with DuckDB:
-- $ duckdb < analysis/roi_analysis.sql
-- 
-- Or in Python:
-- import duckdb
-- conn = duckdb.connect()
-- with open('analysis/roi_analysis.sql', 'r') as f:
--     queries = f.read()
-- conn.execute(queries)
-- =============================================================================
