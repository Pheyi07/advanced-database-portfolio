-- ============================================================================
-- MIT 8103 Advanced Database Systems - Continuous Assessment Portfolio
-- Case Study: FinFlow Global Systems
-- Portfolio 2: Indexing Architecture & Optimisation DDL
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Index 1: Composite B-Tree for Account Ledger & Chronological Pagination
-- Optimizes Query 1 (Window function running balance)
-- Transforms O(N) scan across entire ledger into O(log M) index range seek.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_ledger_account_time 
ON ledger_entries (account_id, entry_timestamp, entry_id);

-- ----------------------------------------------------------------------------
-- Index 2: Composite Filter Index for AML Compliance Alerts
-- Optimizes Query 2 (High-risk compliance investigations)
-- Directly filters severity and status before joining to parent transactions.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_aml_alert_status_sev 
ON aml_risk_alerts (severity, status, transaction_id);

-- ----------------------------------------------------------------------------
-- Index 3: Composite Covering Index for Date-Bounded Settlement Reconciliations
-- Optimizes Query 3 (Daily multi-currency settlement aggregations)
-- Satisfies the query completely from the B-tree leaf pages (Index-Only Scan).
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_tx_status_time_curr 
ON transactions (status, initiated_at, source_currency, destination_currency, source_amount, destination_amount, transaction_fee);

-- ----------------------------------------------------------------------------
-- Index 4: Composite Index for Merchant Transaction Audits
-- Optimizes Query 4 (Merchant checkout metrics & GMV computation)
-- Eliminates table scans for merchant lookups and enables index aggregation.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_tx_merchant_status_amt 
ON transactions (merchant_id, status, source_amount);

-- ----------------------------------------------------------------------------
-- Index 5: Composite Covering Index for Multi-Hop Transfer Traversal
-- Optimizes Query 5 (Graph lineage & transfer fan-out)
-- Accelerates the secondary join on intermediate accounts.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_tx_source_status_time 
ON transactions (source_account_id, status, initiated_at, destination_account_id, source_amount);
