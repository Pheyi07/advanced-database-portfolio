-- ============================================================================
-- MIT 8103 Advanced Database Systems - Continuous Assessment Portfolio
-- Case Study: FinFlow Global Systems
-- Portfolio 3: Transactions & Concurrency Control (ACID Implementation)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TRANSACTION SCENARIO 1: Successful Atomic Transfer with COMMIT
-- Demonstrates Atomicity, Consistency, Isolation, and Durability.
-- Debit source, credit destination, record transaction, write 2 balanced ledger legs.
-- ----------------------------------------------------------------------------
BEGIN TRANSACTION;

-- 1. Deduct from source account (acc-001-usd: balance was $12,500.00)
UPDATE accounts 
SET balance = balance - 2500.0000, 
    version = version + 1
WHERE account_id = 'acc-001-usd' 
  AND balance >= 2500.0000;

-- 2. Credit destination account (acc-005-usd: balance was $95,000.00)
UPDATE accounts 
SET balance = balance + 2500.0000, 
    version = version + 1
WHERE account_id = 'acc-005-usd';

-- 3. Insert transaction record
INSERT INTO transactions (
    transaction_id, idempotency_key, source_account_id, destination_account_id,
    merchant_id, transaction_type, source_currency, source_amount,
    destination_currency, destination_amount, exchange_rate_applied,
    transaction_fee, status, risk_score, description, initiated_at, completed_at
) VALUES (
    'tx-acid-001', 'idemp-acid-success-001', 'acc-001-usd', 'acc-005-usd',
    NULL, 'P2P_TRANSFER', 'USD', 2500.0000,
    'USD', 2500.0000, 1.000000,
    0.0000, 'COMPLETED', 10.00, 'Corporate escrow transfer',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- 4. Insert balanced double-entry ledger debit leg
INSERT INTO ledger_entries (
    transaction_id, account_id, entry_type, amount, currency_code, balance_after
) VALUES (
    'tx-acid-001', 'acc-001-usd', 'DEBIT', 2500.0000, 'USD', 10000.0000
);

-- 5. Insert balanced double-entry ledger credit leg
INSERT INTO ledger_entries (
    transaction_id, account_id, entry_type, amount, currency_code, balance_after
) VALUES (
    'tx-acid-001', 'acc-005-usd', 'CREDIT', 2500.0000, 'USD', 97500.0000
);

COMMIT;


-- ----------------------------------------------------------------------------
-- TRANSACTION SCENARIO 2: Insufficient Funds Exception with Automatic ROLLBACK
-- Demonstrates atomicity preservation under constraint failure.
-- Attempting to withdraw $99,000,000 from acc-002-ngn violates CHECK (balance >= 0).
-- ----------------------------------------------------------------------------
BEGIN TRANSACTION;

-- Step 1: Attempt illegal overdraft
-- This update will fail check constraint or match 0 rows if guarded
UPDATE accounts 
SET balance = balance - 99000000.0000,
    version = version + 1
WHERE account_id = 'acc-002-ngn' 
  AND (balance - 99000000.0000) >= 0.0000;

-- In application logic, checking changes() == 0 immediately triggers ROLLBACK
-- Here we simulate the manual abort condition
ROLLBACK;


-- ----------------------------------------------------------------------------
-- TRANSACTION SCENARIO 3: Savepoints & Partial Rollback
-- Demonstrates nested transaction control using SAVEPOINTS.
-- ----------------------------------------------------------------------------
BEGIN TRANSACTION;

-- Base transfer operation
UPDATE accounts SET balance = balance - 100.0000 WHERE account_id = 'acc-001-usd';

SAVEPOINT fee_calculation_stage;

-- Attempt an optional partner promotional credit
INSERT INTO ledger_entries (
    transaction_id, account_id, entry_type, amount, currency_code, balance_after
) VALUES ('tx-promo-temp', 'acc-001-usd', 'CREDIT', 50.0000, 'USD', 9950.0000);

-- Promotional rule expired; roll back only to savepoint without aborting main transaction
ROLLBACK TO SAVEPOINT fee_calculation_stage;

-- Release savepoint and finalize primary transfer
RELEASE SAVEPOINT fee_calculation_stage;

COMMIT;
