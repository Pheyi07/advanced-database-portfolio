-- ============================================================================
-- MIT 8103 Advanced Database Systems - Continuous Assessment Portfolio
-- Case Study: FinFlow Global Systems (Next-Gen Cross-Border Digital Banking)
-- Portfolio 1: Database Design & Relational Schema (DDL)
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- Table 1: CURRENCY REGISTRY (Lookup / Dimension Table)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS currency_registry;
CREATE TABLE currency_registry (
    currency_code       CHAR(3) PRIMARY KEY,
    currency_name       VARCHAR(50) NOT NULL,
    symbol              VARCHAR(5) NOT NULL,
    decimal_precision   INTEGER NOT NULL DEFAULT 2 CHECK (decimal_precision BETWEEN 0 AND 8),
    is_active           INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- Table 2: CUSTOMERS (Core Entity)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    customer_id         TEXT PRIMARY KEY, -- UUID v4
    first_name          VARCHAR(50) NOT NULL,
    last_name           VARCHAR(50) NOT NULL,
    email               VARCHAR(100) NOT NULL UNIQUE,
    phone_number        VARCHAR(25) NOT NULL UNIQUE,
    kyc_tier            INTEGER NOT NULL DEFAULT 1 CHECK (kyc_tier IN (1, 2, 3)),
    country_code        CHAR(3) NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' 
                        CHECK (status IN ('PENDING_VERIFICATION', 'ACTIVE', 'SUSPENDED', 'CLOSED')),
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- Table 3: ACCOUNTS / DIGITAL WALLETS
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    account_id          TEXT PRIMARY KEY, -- UUID v4
    customer_id         TEXT NOT NULL,
    account_number      VARCHAR(20) NOT NULL UNIQUE,
    account_type        VARCHAR(25) NOT NULL 
                        CHECK (account_type IN ('SAVINGS', 'CHECKING', 'MERCHANT_SETTLEMENT', 'ESCROW', 'TREASURY_RESERVE')),
    currency_code       CHAR(3) NOT NULL,
    balance             DECIMAL(18, 4) NOT NULL DEFAULT 0.0000 CHECK (balance >= 0.0000),
    locked_balance      DECIMAL(18, 4) NOT NULL DEFAULT 0.0000 CHECK (locked_balance >= 0.0000),
    daily_transfer_limit DECIMAL(18, 4) NOT NULL DEFAULT 50000.0000 CHECK (daily_transfer_limit >= 0.0000),
    status              VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' 
                        CHECK (status IN ('ACTIVE', 'FROZEN', 'DORMANT', 'CLOSED')),
    version             INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1), -- For Optimistic Concurrency Control (OCC)
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (currency_code) REFERENCES currency_registry (currency_code) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ----------------------------------------------------------------------------
-- Table 4: EXCHANGE RATES (Historical & Real-Time FX Dimension)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS exchange_rates;
CREATE TABLE exchange_rates (
    rate_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    base_currency       CHAR(3) NOT NULL,
    target_currency     CHAR(3) NOT NULL,
    rate                DECIMAL(18, 6) NOT NULL CHECK (rate > 0.000000),
    effective_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (base_currency) REFERENCES currency_registry (currency_code) ON DELETE RESTRICT,
    FOREIGN KEY (target_currency) REFERENCES currency_registry (currency_code) ON DELETE RESTRICT,
    CONSTRAINT uq_currency_pair_time UNIQUE (base_currency, target_currency, effective_timestamp)
);

-- ----------------------------------------------------------------------------
-- Table 5: MERCHANTS (Business Profiles)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS merchants;
CREATE TABLE merchants (
    merchant_id             TEXT PRIMARY KEY, -- UUID v4
    customer_id             TEXT NOT NULL,
    business_name           VARCHAR(100) NOT NULL,
    merchant_category_code  CHAR(4) NOT NULL, -- ISO 18245 MCC
    settlement_account_id   TEXT NOT NULL,
    api_key_hash            VARCHAR(64) NOT NULL,
    commission_rate         DECIMAL(5, 4) NOT NULL DEFAULT 0.0150 CHECK (commission_rate BETWEEN 0.0000 AND 0.1000),
    status                  VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' 
                            CHECK (status IN ('ACTIVE', 'SUSPENDED', 'TERMINATED')),
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (settlement_account_id) REFERENCES accounts (account_id) ON DELETE RESTRICT
);

-- ----------------------------------------------------------------------------
-- Table 6: TRANSACTIONS (Core Financial Operation / Double-Entry Header)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_id          TEXT PRIMARY KEY, -- UUID v4
    idempotency_key         VARCHAR(64) NOT NULL UNIQUE,
    source_account_id       TEXT NOT NULL,
    destination_account_id  TEXT NOT NULL,
    merchant_id             TEXT NULL,
    transaction_type        VARCHAR(25) NOT NULL 
                            CHECK (transaction_type IN ('P2P_TRANSFER', 'MERCHANT_PAYMENT', 'CURRENCY_EXCHANGE', 'DEPOSIT', 'WITHDRAWAL', 'REVERSAL')),
    source_currency         CHAR(3) NOT NULL,
    source_amount           DECIMAL(18, 4) NOT NULL CHECK (source_amount > 0.0000),
    destination_currency    CHAR(3) NOT NULL,
    destination_amount      DECIMAL(18, 4) NOT NULL CHECK (destination_amount > 0.0000),
    exchange_rate_applied   DECIMAL(18, 6) NOT NULL DEFAULT 1.000000 CHECK (exchange_rate_applied > 0),
    transaction_fee         DECIMAL(18, 4) NOT NULL DEFAULT 0.0000 CHECK (transaction_fee >= 0.0000),
    status                  VARCHAR(20) NOT NULL DEFAULT 'PENDING' 
                            CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'REVERSED')),
    risk_score              DECIMAL(5, 2) NOT NULL DEFAULT 0.00 CHECK (risk_score BETWEEN 0.00 AND 100.00),
    description             TEXT NULL,
    initiated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at            TIMESTAMP NULL,
    FOREIGN KEY (source_account_id) REFERENCES accounts (account_id) ON DELETE RESTRICT,
    FOREIGN KEY (destination_account_id) REFERENCES accounts (account_id) ON DELETE RESTRICT,
    FOREIGN KEY (merchant_id) REFERENCES merchants (merchant_id) ON DELETE SET NULL,
    FOREIGN KEY (source_currency) REFERENCES currency_registry (currency_code),
    FOREIGN KEY (destination_currency) REFERENCES currency_registry (currency_code)
);

-- ----------------------------------------------------------------------------
-- Table 7: LEDGER ENTRIES (Double-Entry General Ledger - Immutable)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS ledger_entries;
CREATE TABLE ledger_entries (
    entry_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id      TEXT NOT NULL,
    account_id          TEXT NOT NULL,
    entry_type          VARCHAR(10) NOT NULL CHECK (entry_type IN ('DEBIT', 'CREDIT')),
    amount              DECIMAL(18, 4) NOT NULL CHECK (amount > 0.0000),
    currency_code       CHAR(3) NOT NULL,
    balance_after       DECIMAL(18, 4) NOT NULL,
    entry_timestamp     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id) ON DELETE RESTRICT,
    FOREIGN KEY (account_id) REFERENCES accounts (account_id) ON DELETE RESTRICT,
    FOREIGN KEY (currency_code) REFERENCES currency_registry (currency_code)
);

-- ----------------------------------------------------------------------------
-- Table 8: AML RISK ALERTS (Compliance & Fraud Investigation)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS aml_risk_alerts;
CREATE TABLE aml_risk_alerts (
    alert_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id      TEXT NOT NULL,
    rule_code           VARCHAR(50) NOT NULL,
    severity            VARCHAR(15) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    flagged_amount      DECIMAL(18, 4) NOT NULL,
    flagged_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status              VARCHAR(20) NOT NULL DEFAULT 'OPEN' 
                        CHECK (status IN ('OPEN', 'INVESTIGATING', 'CLEARED', 'REPORTED_TO_AUTHORITY')),
    investigator_notes  TEXT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id) ON DELETE RESTRICT
);
