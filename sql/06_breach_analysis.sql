CREATE OR REPLACE VIEW v_breach_clustering AS
WITH ordered AS (
    SELECT
        *,
        SUM(CASE WHEN breach = 0 THEN 1 ELSE 0 END) OVER (
            PARTITION BY asset, model, confidence_level, method, period
            ORDER BY target_date
        ) AS non_breach_group
    FROM breach_events
),
clusters AS (
    SELECT
        asset,
        model,
        confidence_level,
        method,
        period,
        non_breach_group,
        COUNT(*) AS cluster_length,
        MIN(target_date) AS cluster_start,
        MAX(target_date) AS cluster_end
    FROM ordered
    WHERE breach = 1
    GROUP BY asset, model, confidence_level, method, period, non_breach_group
)
SELECT
    asset,
    model,
    confidence_level,
    method,
    period,
    COUNT(*) AS breach_clusters,
    COALESCE(MAX(cluster_length), 0) AS max_cluster_length,
    AVG(cluster_length) AS avg_cluster_length
FROM clusters
GROUP BY asset, model, confidence_level, method, period;
