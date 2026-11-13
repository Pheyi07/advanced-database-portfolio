-- ============================================================================
-- MIT 8103 Advanced Database Systems - Continuous Assessment Portfolio
-- Case Study: FinFlow Global Systems
-- Portfolio 1: Seed Data for Core Relational Model
-- ============================================================================

-- 1. Currencies
INSERT INTO currency_registry (currency_code, currency_name, symbol, decimal_precision) VALUES
('USD', 'United States Dollar', '$', 2),
('EUR', 'Euro', '€', 2),
('GBP', 'British Pound', '£', 2),
('NGN', 'Nigerian Naira', '₦', 2),
('KES', 'Kenyan Shilling', 'KSh', 2),
('CAD', 'Canadian Dollar', 'CA$', 2);

-- 2. Exchange Rates
INSERT INTO exchange_rates (base_currency, target_currency, rate, effective_timestamp) VALUES
('USD', 'NGN', 1580.500000, '2026-11-01 00:00:00'),
('EUR', 'USD', 1.085000, '2026-11-01 00:00:00'),
('GBP', 'USD', 1.295000, '2026-11-01 00:00:00'),
('USD', 'KES', 130.250000, '2026-11-01 00:00:00'),
('USD', 'CAD', 1.392000, '2026-11-01 00:00:00');

-- 3. Customers
INSERT INTO customers (customer_id, first_name, last_name, email, phone_number, kyc_tier, country_code, status, created_at) VALUES
('cust-001', 'Adaeze', 'Okonkwo', 'adaeze.o@finflow.io', '+2348031234567', 3, 'NGA', 'ACTIVE', '2026-01-10 09:15:00'),
('cust-002', 'Emeka', 'Adeyemi', 'emeka.a@finflow.io', '+2348098765432', 2, 'NGA', 'ACTIVE', '2026-02-14 11:30:00'),
('cust-003', 'Sarah', 'Jenkins', 's.jenkins@londontech.co.uk', '+447911123456', 3, 'GBR', 'ACTIVE', '2026-03-01 14:00:00'),
('cust-004', 'Jean-Luc', 'Dubois', 'jl.dubois@parisfinance.fr', '+33612345678', 3, 'FRA', 'ACTIVE', '2026-03-15 08:45:00'),
('cust-005', 'Marcus', 'Vance', 'marcus.v@nycapitol.com', '+12125550198', 3, 'USA', 'ACTIVE', '2026-04-02 16:20:00'),
('cust-006', 'Amina', 'Kamau', 'amina.k@nairobibiz.ke', '+254712345678', 2, 'KEN', 'ACTIVE', '2026-05-18 10:10:00'),
('cust-007', 'Chinedu', 'Eze', 'chinedu.eze@lagosretail.ng', '+2348123334455', 2, 'NGA', 'ACTIVE', '2026-06-01 12:00:00'),
('cust-008', 'David', 'Miller', 'dmiller@torontoconsult.ca', '+14165550143', 3, 'CAN', 'ACTIVE', '2026-06-20 15:40:00');

-- 4. Accounts / Wallets
INSERT INTO accounts (account_id, customer_id, account_number, account_type, currency_code, balance, locked_balance, daily_transfer_limit, status, version) VALUES
('acc-001-ngn', 'cust-001', '0100200301', 'SAVINGS', 'NGN', 4500000.0000, 0.0000, 2000000.0000, 'ACTIVE', 1),
('acc-001-usd', 'cust-001', '0100200302', 'CHECKING', 'USD', 12500.0000, 0.0000, 50000.0000, 'ACTIVE', 1),
('acc-002-ngn', 'cust-002', '0100200303', 'CHECKING', 'NGN', 850000.0000, 0.0000, 1000000.0000, 'ACTIVE', 1),
('acc-003-gbp', 'cust-003', '0200300401', 'CHECKING', 'GBP', 28000.0000, 0.0000, 100000.0000, 'ACTIVE', 1),
('acc-003-usd', 'cust-003', '0200300402', 'SAVINGS', 'USD', 45000.0000, 0.0000, 100000.0000, 'ACTIVE', 1),
('acc-004-eur', 'cust-004', '0300400501', 'CHECKING', 'EUR', 32000.0000, 0.0000, 80000.0000, 'ACTIVE', 1),
('acc-005-usd', 'cust-005', '0400500601', 'CHECKING', 'USD', 95000.0000, 0.0000, 200000.0000, 'ACTIVE', 1),
('acc-006-kes', 'cust-006', '0500600701', 'CHECKING', 'KES', 750000.0000, 0.0000, 500000.0000, 'ACTIVE', 1),
('acc-007-ngn', 'cust-007', '0600700801', 'MERCHANT_SETTLEMENT', 'NGN', 15200000.0000, 0.0000, 10000000.0000, 'ACTIVE', 1),
('acc-008-cad', 'cust-008', '0700800901', 'CHECKING', 'CAD', 18500.0000, 0.0000, 50000.0000, 'ACTIVE', 1),
('acc-treasury-usd', 'cust-005', '9990000001', 'TREASURY_RESERVE', 'USD', 5000000.0000, 0.0000, 10000000.0000, 'ACTIVE', 1);

-- 5. Merchants
INSERT INTO merchants (merchant_id, customer_id, business_name, merchant_category_code, settlement_account_id, api_key_hash, commission_rate, status) VALUES
('merch-001', 'cust-007', 'Lagos E-Marketplace Direct', '5311', 'acc-007-ngn', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 0.0125, 'ACTIVE');

-- 6. Sample Transactions
INSERT INTO transactions (
    transaction_id, idempotency_key, source_account_id, destination_account_id, 
    merchant_id, transaction_type, source_currency, source_amount, 
    destination_currency, destination_amount, exchange_rate_applied, 
    transaction_fee, status, risk_score, description, initiated_at, completed_at
) VALUES
('tx-10001', 'idemp-20261101-001', 'acc-001-ngn', 'acc-002-ngn', NULL, 'P2P_TRANSFER', 'NGN', 150000.0000, 'NGN', 150000.0000, 1.000000, 150.0000, 'COMPLETED', 12.50, 'Payment for contract freelancing', '2026-11-01 10:00:00', '2026-11-01 10:00:01'),
('tx-10002', 'idemp-20261101-002', 'acc-003-usd', 'acc-001-usd', NULL, 'P2P_TRANSFER', 'USD', 2500.0000, 'USD', 2500.0000, 1.000000, 15.0000, 'COMPLETED', 8.00, 'Remote software consulting fee', '2026-11-01 11:25:00', '2026-11-01 11:25:02'),
('tx-10003', 'idemp-20261102-003', 'acc-005-usd', 'acc-001-ngn', NULL, 'CURRENCY_EXCHANGE', 'USD', 1000.0000, 'NGN', 1580500.0000, 1580.500000, 25.0000, 'COMPLETED', 15.00, 'Cross-border remittance', '2026-11-02 14:10:00', '2026-11-02 14:10:04'),
('tx-10004', 'idemp-20261102-004', 'acc-002-ngn', 'acc-007-ngn', 'merch-001', 'MERCHANT_PAYMENT', 'NGN', 45000.0000, 'NGN', 45000.0000, 1.000000, 562.5000, 'COMPLETED', 5.00, 'Online electronics purchase', '2026-11-02 16:45:00', '2026-11-02 16:45:01'),
('tx-10005', 'idemp-20261103-005', 'acc-005-usd', 'acc-004-eur', NULL, 'CURRENCY_EXCHANGE', 'USD', 50000.0000, 'EUR', 46082.9500, 0.921659, 120.0000, 'COMPLETED', 82.50, 'Large liquidity rebalancing', '2026-11-03 08:30:00', '2026-11-03 08:30:03');

-- 7. Double-Entry General Ledger Postings
INSERT INTO ledger_entries (transaction_id, account_id, entry_type, amount, currency_code, balance_after, entry_timestamp) VALUES
('tx-10001', 'acc-001-ngn', 'DEBIT', 150150.0000, 'NGN', 4349850.0000, '2026-11-01 10:00:01'),
('tx-10001', 'acc-002-ngn', 'CREDIT', 150000.0000, 'NGN', 1000000.0000, '2026-11-01 10:00:01'),
('tx-10002', 'acc-003-usd', 'DEBIT', 2515.0000, 'USD', 42485.0000, '2026-11-01 11:25:02'),
('tx-10002', 'acc-001-usd', 'CREDIT', 2500.0000, 'USD', 15000.0000, '2026-11-01 11:25:02'),
('tx-10003', 'acc-005-usd', 'DEBIT', 1025.0000, 'USD', 93975.0000, '2026-11-02 14:10:04'),
('tx-10003', 'acc-001-ngn', 'CREDIT', 1580500.0000, 'NGN', 5930350.0000, '2026-11-02 14:10:04'),
('tx-10004', 'acc-002-ngn', 'DEBIT', 45000.0000, 'NGN', 955000.0000, '2026-11-02 16:45:01'),
('tx-10004', 'acc-007-ngn', 'CREDIT', 44437.5000, 'NGN', 15244437.5000, '2026-11-02 16:45:01'),
('tx-10005', 'acc-005-usd', 'DEBIT', 50120.0000, 'USD', 43855.0000, '2026-11-03 08:30:03'),
('tx-10005', 'acc-004-eur', 'CREDIT', 46082.9500, 'EUR', 78082.9500, '2026-11-03 08:30:03');

-- 8. AML Risk Alerts
INSERT INTO aml_risk_alerts (transaction_id, rule_code, severity, flagged_amount, flagged_at, status, investigator_notes) VALUES
('tx-10005', 'RULE_LARGE_CROSS_BORDER_EXCHANGE', 'HIGH', 50000.0000, '2026-11-03 08:30:01', 'INVESTIGATING', 'High value transaction exceeding $25,000 threshold. Tier 3 KYC verified; awaiting proof of funds invoice.');
