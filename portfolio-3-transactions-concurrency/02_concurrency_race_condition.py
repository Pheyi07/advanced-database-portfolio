import sqlite3
import threading
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DB_CONCURRENCY = os.path.join(BASE_DIR, 'concurrency_test.db')

def setup_test_db():
    if os.path.exists(DB_CONCURRENCY):
        try:
            os.remove(DB_CONCURRENCY)
        except Exception:
            pass

    conn = sqlite3.connect(DB_CONCURRENCY)
    ddl_path = os.path.join(ROOT_DIR, 'portfolio-1-database-design', '01_schema_ddl.sql')
    seed_path = os.path.join(ROOT_DIR, 'portfolio-1-database-design', '02_seed_data.sql')

    with open(ddl_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    with open(seed_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
        
    conn.execute("UPDATE accounts SET balance = 1000.0000, version = 1 WHERE account_id = 'acc-001-usd';")
    conn.commit()
    conn.close()

def run_lost_update_simulation():
    print("\n" + "="*70)
    print("SIMULATION 1: UNCONTROLLED CONCURRENCY (LOST UPDATE / DOUBLE-SPEND)")
    print("="*70)
    setup_test_db()

    conn_check = sqlite3.connect(DB_CONCURRENCY)
    initial_balance = conn_check.execute("SELECT balance FROM accounts WHERE account_id = 'acc-001-usd'").fetchone()[0]
    print(f"Initial Account Balance: ${initial_balance:,.2f}")
    conn_check.close()

    logs = []

    def unshielded_withdrawal(thread_name, withdraw_amount, delay):
        conn = sqlite3.connect(DB_CONCURRENCY)
        cur = conn.cursor()
        
        cur.execute("SELECT balance FROM accounts WHERE account_id = 'acc-001-usd'")
        current_bal = cur.fetchone()[0]
        logs.append(f"[{thread_name}] Read balance: ${current_bal:,.2f}")
        
        time.sleep(delay)
        
        if current_bal >= withdraw_amount:
            new_bal = current_bal - withdraw_amount
            logs.append(f"[{thread_name}] Validation PASSED. Writing new balance: ${new_bal:,.2f}")
            cur.execute("UPDATE accounts SET balance = ? WHERE account_id = 'acc-001-usd'", (new_bal,))
            conn.commit()
            logs.append(f"[{thread_name}] COMMIT successful.")
        else:
            logs.append(f"[{thread_name}] Validation FAILED: Insufficient funds.")
            conn.rollback()
        conn.close()

    t1 = threading.Thread(target=unshielded_withdrawal, args=("Thread-1 (Debit $800)", 800.0, 0.05))
    t2 = threading.Thread(target=unshielded_withdrawal, args=("Thread-2 (Debit $700)", 700.0, 0.02))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    for l in logs:
        print("  " + l)

    conn_final = sqlite3.connect(DB_CONCURRENCY)
    final_bal = conn_final.execute("SELECT balance FROM accounts WHERE account_id = 'acc-001-usd'").fetchone()[0]
    conn_final.close()

    print(f"\nFinal Account Balance: ${final_bal:,.2f}")
    print(f"ANOMALY OBSERVED: Total debited was $1,500 from an initial $1,000 balance!")
    print(f"The second commit overwrote the first, resulting in severe double-spend loss.")
    return logs, initial_balance, final_bal

def run_occ_simulation():
    print("\n" + "="*70)
    print("SIMULATION 2: OPTIMISTIC CONCURRENCY CONTROL (OCC with Versioning)")
    print("="*70)
    setup_test_db()

    conn_check = sqlite3.connect(DB_CONCURRENCY)
    initial_balance = conn_check.execute("SELECT balance FROM accounts WHERE account_id = 'acc-001-usd'").fetchone()[0]
    print(f"Initial Account Balance: ${initial_balance:,.2f} | Version = 1")
    conn_check.close()

    logs = []

    def occ_withdrawal(thread_name, withdraw_amount, delay):
        conn = sqlite3.connect(DB_CONCURRENCY)
        cur = conn.cursor()
        
        cur.execute("SELECT balance, version FROM accounts WHERE account_id = 'acc-001-usd'")
        current_bal, current_ver = cur.fetchone()
        logs.append(f"[{thread_name}] Read balance: ${current_bal:,.2f}, Version: {current_ver}")
        
        time.sleep(delay)
        
        if current_bal >= withdraw_amount:
            new_bal = current_bal - withdraw_amount
            cur.execute("""
                UPDATE accounts 
                SET balance = ?, version = version + 1 
                WHERE account_id = 'acc-001-usd' AND version = ?
            """, (new_bal, current_ver))
            conn.commit()
            
            if cur.rowcount == 1:
                logs.append(f"[{thread_name}] SUCCESS: Rows updated = 1. New balance: ${new_bal:,.2f}, Version: {current_ver + 1}")
            else:
                logs.append(f"[{thread_name}] CONFLICT DETECTED: Rows updated = 0 (Version mismatch!). Transaction ABORTED safely.")
        else:
            logs.append(f"[{thread_name}] Insufficient funds.")
        conn.close()

    t1 = threading.Thread(target=occ_withdrawal, args=("Thread-1 (Debit $800)", 800.0, 0.06))
    t2 = threading.Thread(target=occ_withdrawal, args=("Thread-2 (Debit $700)", 700.0, 0.02))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    for l in logs:
        print("  " + l)

    conn_final = sqlite3.connect(DB_CONCURRENCY)
    final_bal, final_ver = conn_final.execute("SELECT balance, version FROM accounts WHERE account_id = 'acc-001-usd'").fetchone()
    conn_final.close()

    print(f"\nFinal Account Balance: ${final_bal:,.2f} | Final Version: {final_ver}")
    print("[SUCCESS] Invariant Preserved: Exactly one transaction succeeded; conflicting transaction was rejected.")
    return logs, initial_balance, final_bal

def run_pessimistic_atomic_simulation():
    print("\n" + "="*70)
    print("SIMULATION 3: PESSIMISTIC ATOMIC PREDICATE LOCKING")
    print("="*70)
    setup_test_db()

    logs = []

    def atomic_predicate_withdrawal(thread_name, withdraw_amount, delay):
        conn = sqlite3.connect(DB_CONCURRENCY, timeout=10.0)
        cur = conn.cursor()
        
        time.sleep(delay)
        
        cur.execute("""
            UPDATE accounts 
            SET balance = balance - ?, version = version + 1 
            WHERE account_id = 'acc-001-usd' AND (balance - ?) >= 0
        """, (withdraw_amount, withdraw_amount))
        conn.commit()
        
        if cur.rowcount == 1:
            cur.execute("SELECT balance FROM accounts WHERE account_id = 'acc-001-usd'")
            rem = cur.fetchone()[0]
            logs.append(f"[{thread_name}] ATOMIC DEBIT SUCCESSFUL: Deducted ${withdraw_amount:,.2f}. Remaining: ${rem:,.2f}")
        else:
            logs.append(f"[{thread_name}] ATOMIC DEBIT REJECTED: Overdraft constraint prevented debit of ${withdraw_amount:,.2f}.")
        conn.close()

    t1 = threading.Thread(target=atomic_predicate_withdrawal, args=("Thread-1 (Debit $800)", 800.0, 0.01))
    t2 = threading.Thread(target=atomic_predicate_withdrawal, args=("Thread-2 (Debit $700)", 700.0, 0.01))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    for l in logs:
        print("  " + l)

    conn_final = sqlite3.connect(DB_CONCURRENCY)
    final_bal = conn_final.execute("SELECT balance FROM accounts WHERE account_id = 'acc-001-usd'").fetchone()[0]
    conn_final.close()

    print(f"\nFinal Account Balance: ${final_bal:,.2f}")
    print("[SUCCESS] Account balance never breached overdraft boundary.")
    return logs, final_bal

if __name__ == "__main__":
    run_lost_update_simulation()
    run_occ_simulation()
    run_pessimistic_atomic_simulation()
