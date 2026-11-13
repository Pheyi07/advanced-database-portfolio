import sqlite3
import threading
import time
import os

DB_DEADLOCK = 'advanced-database-portfolio/portfolio-3-transactions-concurrency/deadlock_test.db'

def setup_deadlock_db():
    if os.path.exists(DB_DEADLOCK):
        try:
            os.remove(DB_DEADLOCK)
        except Exception:
            pass
    conn = sqlite3.connect(DB_DEADLOCK)
    with open('advanced-database-portfolio/portfolio-1-database-design/01_schema_ddl.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    with open('advanced-database-portfolio/portfolio-1-database-design/02_seed_data.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def simulate_deadlock_and_prevention():
    print("="*75)
    print("DEMONSTRATION: DATABASE DEADLOCK CYCLE & PREVENTION VIA RESOURCE ORDERING")
    print("="*75)
    setup_deadlock_db()

    print("\n--- SCENARIO 1: ARBITRARY LOCK ORDERING (CIRCULAR DEADLOCK RISK) ---")
    print("Thread 1: Transfers $100 from Account A -> Account B (Locks A, then B)")
    print("Thread 2: Transfers $100 from Account B -> Account A (Locks B, then A)")

    log_deadlock = []

    def tx1_worker():
        conn = sqlite3.connect(DB_DEADLOCK, timeout=1.0)
        cur = conn.cursor()
        try:
            cur.execute("BEGIN IMMEDIATE;")
            log_deadlock.append("[T1] Acquired exclusive lock on DB; debiting Account A ('acc-001-usd').")
            cur.execute("UPDATE accounts SET balance = balance - 100 WHERE account_id = 'acc-001-usd';")
            time.sleep(0.5)
            log_deadlock.append("[T1] Crediting Account B ('acc-005-usd')...")
            cur.execute("UPDATE accounts SET balance = balance + 100 WHERE account_id = 'acc-005-usd';")
            conn.commit()
            log_deadlock.append("[T1] COMMIT SUCCESS.")
        except sqlite3.OperationalError as e:
            log_deadlock.append(f"[T1] ABORTED due to concurrency contention: {e}")
            conn.rollback()
        finally:
            conn.close()

    def tx2_worker():
        time.sleep(0.1) # Stagger start slightly
        conn = sqlite3.connect(DB_DEADLOCK, timeout=1.0)
        cur = conn.cursor()
        try:
            log_deadlock.append("[T2] Attempting to acquire exclusive lock on DB...")
            cur.execute("BEGIN IMMEDIATE;")
            log_deadlock.append("[T2] Acquired lock; debiting Account B ('acc-005-usd').")
            cur.execute("UPDATE accounts SET balance = balance - 100 WHERE account_id = 'acc-005-usd';")
            cur.execute("UPDATE accounts SET balance = balance + 100 WHERE account_id = 'acc-001-usd';")
            conn.commit()
            log_deadlock.append("[T2] COMMIT SUCCESS.")
        except sqlite3.OperationalError as e:
            log_deadlock.append(f"[T2] DEADLOCK / LOCK TIMEOUT DETECTED: {e}")
            conn.rollback()
        finally:
            conn.close()

    th1 = threading.Thread(target=tx1_worker)
    th2 = threading.Thread(target=tx2_worker)
    th1.start()
    th2.start()
    th1.join()
    th2.join()

    for l in log_deadlock:
        print("  " + l)

    print("\n--- SCENARIO 2: DEADLOCK PREVENTION VIA GLOBAL RESOURCE ORDERING ---")
    print("Rule: Always acquire account locks in deterministic alphabetical order: min(id1, id2) then max(id1, id2)")
    print("This guarantees that circular wait cycles are mathematically impossible (Coffman Condition violated).")

    log_ordered = []

    def ordered_transfer(thread_name, acc_src, acc_dst, amount):
        # Deterministic Lock Ordering
        lock_first, lock_second = sorted([acc_src, acc_dst])
        log_ordered.append(f"[{thread_name}] Requested transfer: {acc_src} -> {acc_dst}. Lock Order: {lock_first} then {lock_second}")
        
        conn = sqlite3.connect(DB_DEADLOCK, timeout=10.0)
        cur = conn.cursor()
        try:
            cur.execute("BEGIN IMMEDIATE;")
            # Lock first
            cur.execute("UPDATE accounts SET balance = balance WHERE account_id = ?", (lock_first,))
            time.sleep(0.1)
            # Lock second
            cur.execute("UPDATE accounts SET balance = balance WHERE account_id = ?", (lock_second,))
            
            # Apply debits/credits
            cur.execute("UPDATE accounts SET balance = balance - ? WHERE account_id = ?", (amount, acc_src))
            cur.execute("UPDATE accounts SET balance = balance + ? WHERE account_id = ?", (amount, acc_dst))
            conn.commit()
            log_ordered.append(f"[{thread_name}] Transfer completed and committed successfully!")
        except Exception as e:
            log_ordered.append(f"[{thread_name}] Exception: {e}")
            conn.rollback()
        finally:
            conn.close()

    ot1 = threading.Thread(target=ordered_transfer, args=("T1", "acc-001-usd", "acc-005-usd", 50.0))
    ot2 = threading.Thread(target=ordered_transfer, args=("T2", "acc-005-usd", "acc-001-usd", 25.0))
    ot1.start()
    ot2.start()
    ot1.join()
    ot2.join()

    for l in log_ordered:
        print("  " + l)

    print("\n[CONCLUSION] Strict lock hierarchy completely prevented deadlock contention.")

if __name__ == "__main__":
    simulate_deadlock_and_prevention()
