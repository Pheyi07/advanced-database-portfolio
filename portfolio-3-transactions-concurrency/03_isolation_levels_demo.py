import sqlite3
import threading
import time
import os

DB_ISOLATION = 'advanced-database-portfolio/portfolio-3-transactions-concurrency/isolation_test.db'

def setup_iso_db():
    if os.path.exists(DB_ISOLATION):
        try:
            os.remove(DB_ISOLATION)
        except Exception:
            pass
    conn = sqlite3.connect(DB_ISOLATION)
    with open('advanced-database-portfolio/portfolio-1-database-design/01_schema_ddl.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    with open('advanced-database-portfolio/portfolio-1-database-design/02_seed_data.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def demonstrate_isolation_phenomena():
    print("="*75)
    print("DEMONSTRATION: TRANSACTION ISOLATION LEVELS & CONCURRENCY ANOMALIES")
    print("="*75)
    setup_iso_db()

    # 1. Non-Repeatable Read Analysis
    print("\n--- PHENOMENON 1: NON-REPEATABLE READ ---")
    print("Definition: Transaction T1 reads a row, T2 modifies and commits, T1 re-reads and observes different data.")
    
    conn1 = sqlite3.connect(DB_ISOLATION, isolation_level=None)
    conn2 = sqlite3.connect(DB_ISOLATION, isolation_level=None)

    # T1 reads initial balance
    cur1 = conn1.cursor()
    cur1.execute("SELECT balance FROM accounts WHERE account_id = 'acc-001-usd'")
    b1 = cur1.fetchone()[0]
    print(f"Step 1: [T1] First Read of acc-001-usd balance: ${b1:,.2f}")

    # T2 updates balance and commits
    cur2 = conn2.cursor()
    cur2.execute("UPDATE accounts SET balance = 15000.0000 WHERE account_id = 'acc-001-usd'")
    print("Step 2: [T2] Updated acc-001-usd balance to $15,000.00 and committed.")

    # T1 re-reads in the same operational context
    cur1.execute("SELECT balance FROM accounts WHERE account_id = 'acc-001-usd'")
    b2 = cur1.fetchone()[0]
    print(f"Step 3: [T1] Second Read of acc-001-usd balance: ${b2:,.2f}")

    if b1 != b2:
        print("  -> RESULT: Non-repeatable read observed under standard read-committed mode ($12,500 != $15,000).")
        print("  -> MITIGATION: In REPEATABLE READ / SERIALIZABLE (or MVCC snapshot), T1 reads from a point-in-time snapshot.")

    # 2. Phantom Read Analysis
    print("\n--- PHENOMENON 2: PHANTOM READ ---")
    print("Definition: T1 queries a predicate range, T2 inserts a matching row, T1 re-queries and sees 'phantom' rows.")

    cur1.execute("SELECT count(*) FROM accounts WHERE balance >= 50000.0000")
    c1 = cur1.fetchone()[0]
    print(f"Step 1: [T1] Count of VIP accounts (balance >= $50,000): {c1}")

    # T2 inserts a new VIP account
    cur2.execute("""
        INSERT INTO accounts (account_id, customer_id, account_number, account_type, currency_code, balance, locked_balance, daily_transfer_limit, status, version)
        VALUES ('acc-phantom-01', 'cust-005', '9991234567', 'CHECKING', 'USD', 75000.0000, 0.0, 50000.0, 'ACTIVE', 1)
    """)
    print("Step 2: [T2] Inserted new VIP account (acc-phantom-01, balance = $75,000.00) and committed.")

    cur1.execute("SELECT count(*) FROM accounts WHERE balance >= 50000.0000")
    c2 = cur1.fetchone()[0]
    print(f"Step 3: [T1] Count of VIP accounts after T2 insertion: {c2}")

    if c2 > c1:
        print("  -> RESULT: Phantom read observed. The predicate range expanded dynamically during concurrent insertion.")
        print("  -> MITIGATION: SERIALIZABLE isolation (predicate locking / index range locks) prevents insertions into scanned ranges.")

    conn1.close()
    conn2.close()

if __name__ == "__main__":
    demonstrate_isolation_phenomena()
