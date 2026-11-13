-- ============================================================================
-- MIT 8103 Advanced Database Systems - Continuous Assessment Portfolio
-- Case Study: FinFlow Global Systems
-- Portfolio 2: Query Processing & Workload Queries (Optimized Workloads)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Window Function - Account Ledger Running Balance & Audit Flow
-- Computes cumulative running balances and inter-transaction velocity.
-- ----------------------------------------------------------------------------
SELECT 
    l.entry_id,
    l.account_id,
    a.currency_code,
    l.entry_type,
    l.amount,
    l.balance_after,
    SUM(CASE WHEN l.entry_type = 'CREDIT' THEN l.amount ELSE -l.amount END) 
        OVER (
            PARTITION BY l.account_id 
            ORDER BY l.entry_timestamp, l.entry_id 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS computed_running_flow
FROM ledger_entries l
JOIN accounts a ON l.account_id = a.account_id
WHERE l.account_id = 'acc-001-ngn'
ORDER BY l.entry_timestamp DESC
LIMIT 50;

-- ----------------------------------------------------------------------------
-- QUERY 2: Multi-Table Join & Filter - High-Risk Critical AML Investigations
-- Joins transactions, accounts, customers, and open AML risk alerts
-- for critical/high severity compliance scrutiny.
-- ----------------------------------------------------------------------------
SELECT 
    t.transaction_id,
    t.initiated_at,
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.kyc_tier,
    t.source_currency,
    t.source_amount,
    t.risk_score,
    a.rule_code,
    a.severity,
    a.status AS alert_status
FROM aml_risk_alerts a
JOIN transactions t ON a.transaction_id = t.transaction_id
JOIN accounts acc ON t.source_account_id = acc.account_id
JOIN customers c ON acc.customer_id = c.customer_id
WHERE a.severity IN ('HIGH', 'CRITICAL')
  AND a.status IN ('OPEN', 'INVESTIGATING')
ORDER BY t.risk_score DESC
LIMIT 50;

-- ----------------------------------------------------------------------------
-- QUERY 3: Range Filter & Multi-Currency Settlement Reconciliation
-- Reconciles completed settlements across currency pairs for a 7-day audit window.
-- ----------------------------------------------------------------------------
SELECT 
    DATE(t.initiated_at) AS settlement_date,
    t.source_currency,
    t.destination_currency,
    COUNT(t.transaction_id) AS total_tx_count,
    ROUND(SUM(t.source_amount), 2) AS total_source_volume,
    ROUND(SUM(t.destination_amount), 2) AS total_settled_volume,
    ROUND(SUM(t.transaction_fee), 2) AS total_fee_revenue
FROM transactions t
WHERE t.status = 'COMPLETED'
  AND t.initiated_at >= '2026-10-15 00:00:00' 
  AND t.initiated_at < '2026-10-22 00:00:00'
GROUP BY DATE(t.initiated_at), t.source_currency, t.destination_currency
ORDER BY settlement_date ASC, total_source_volume DESC;

-- ----------------------------------------------------------------------------
-- QUERY 4: CTE - Dedicated Merchant GMV & Fee Yield Audit
-- Analyzes checkout volume, platform commission, and ticket distribution 
-- for a designated high-throughput merchant.
-- ----------------------------------------------------------------------------
WITH DedicatedMerchantTx AS (
    SELECT 
        m.merchant_id,
        m.business_name,
        m.commission_rate,
        t.transaction_id,
        t.source_amount,
        (t.source_amount * m.commission_rate) AS fee_earned
    FROM merchants m
    JOIN transactions t ON m.merchant_id = t.merchant_id
    WHERE m.merchant_id = 'merch-001'
      AND t.status = 'COMPLETED'
)
SELECT 
    merchant_id,
    business_name,
    COUNT(transaction_id) AS total_orders,
    ROUND(SUM(source_amount), 2) AS gross_merchandise_volume,
    ROUND(SUM(fee_earned), 2) AS net_platform_commission,
    ROUND(AVG(source_amount), 2) AS avg_order_ticket
FROM DedicatedMerchantTx
GROUP BY merchant_id, business_name;

-- ----------------------------------------------------------------------------
-- QUERY 5: Directed Graph Lineage - Outbound Transfer Fan-Out Traversal
-- Traces 2-hop fund disbursements from a primary treasury account to downstream nodes.
-- ----------------------------------------------------------------------------
WITH Hop1 AS (
    SELECT 
        t1.transaction_id AS hop1_tx,
        t1.source_account_id AS root_account,
        t1.destination_account_id AS intermediary_account,
        t1.source_amount AS hop1_amount,
        t1.initiated_at AS hop1_time
    FROM transactions t1
    WHERE t1.source_account_id = 'acc-001-ngn'
      AND t1.status = 'COMPLETED'
)
SELECT 
    h1.root_account,
    h1.intermediary_account,
    h1.hop1_amount,
    t2.transaction_id AS hop2_tx,
    t2.destination_account_id AS terminal_account,
    t2.source_amount AS hop2_amount,
    t2.initiated_at AS hop2_time
FROM Hop1 h1
JOIN transactions t2 ON h1.intermediary_account = t2.source_account_id
WHERE t2.initiated_at >= h1.hop1_time
  AND t2.status = 'COMPLETED'
LIMIT 50;
