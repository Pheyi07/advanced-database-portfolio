import sqlite3
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHARD_DIR = os.path.join(BASE_DIR, 'shards')

class DistributedShardRouter:
    def __init__(self, num_shards=3):
        self.num_shards = num_shards
        self.shard_paths = [os.path.join(SHARD_DIR, f"shard_{i}.db") for i in range(num_shards)]
        self._init_shards()

    def _init_shards(self):
        os.makedirs(SHARD_DIR, exist_ok=True)
        for path in self.shard_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
            conn = sqlite3.connect(path)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    account_number VARCHAR(20) UNIQUE NOT NULL,
                    currency_code CHAR(3) NOT NULL,
                    balance DECIMAL(18, 4) NOT NULL CHECK (balance >= 0.0),
                    status VARCHAR(20) DEFAULT 'ACTIVE'
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS shard_transactions (
                    tx_id TEXT PRIMARY KEY,
                    source_account_id TEXT NOT NULL,
                    destination_account_id TEXT NOT NULL,
                    amount DECIMAL(18, 4) NOT NULL,
                    status VARCHAR(20) NOT NULL
                );
            """)
            conn.commit()
            conn.close()

    def get_shard_id(self, key):
        digest = hashlib.md5(key.encode('utf-8')).hexdigest()
        return int(digest, 16) % self.num_shards

    def insert_account(self, account_id, customer_id, account_number, currency, initial_balance):
        shard_id = self.get_shard_id(customer_id)
        path = self.shard_paths[shard_id]
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO accounts (account_id, customer_id, account_number, currency_code, balance)
            VALUES (?, ?, ?, ?, ?)
        """, (account_id, customer_id, account_number, currency, initial_balance))
        conn.commit()
        conn.close()
        return shard_id

    def get_account(self, customer_id, account_id):
        shard_id = self.get_shard_id(customer_id)
        path = self.shard_paths[shard_id]
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("SELECT account_id, customer_id, currency_code, balance FROM accounts WHERE account_id = ?", (account_id,))
        row = cur.fetchone()
        conn.close()
        return shard_id, row

    def execute_cross_shard_2pc(self, tx_id, src_cust, src_acc, dst_cust, dst_acc, amount):
        src_shard = self.get_shard_id(src_cust)
        dst_shard = self.get_shard_id(dst_cust)

        print(f"\n[2PC COORDINATOR] Initiating Cross-Shard Transfer '{tx_id}': ${amount:,.2f}")
        print(f"  Source: {src_acc} (Customer: {src_cust} -> Shard {src_shard})")
        print(f"  Destination: {dst_acc} (Customer: {dst_cust} -> Shard {dst_shard})")

        conn_src = sqlite3.connect(self.shard_paths[src_shard])
        conn_dst = sqlite3.connect(self.shard_paths[dst_shard])

        print("  --- PHASE 1: PREPARE PHASE ---")
        src_vote = "VOTE_ABORT"
        dst_vote = "VOTE_ABORT"

        cur_src = conn_src.cursor()
        cur_src.execute("SELECT balance FROM accounts WHERE account_id = ?", (src_acc,))
        s_row = cur_src.fetchone()
        if s_row and s_row[0] >= amount:
            src_vote = "VOTE_COMMIT"
            print(f"  [Shard {src_shard}] Balance verified (${s_row[0]:,.2f} >= ${amount:,.2f}). Responded: VOTE_COMMIT")
        else:
            print(f"  [Shard {src_shard}] Insufficient funds or account not found! Responded: VOTE_ABORT")

        cur_dst = conn_dst.cursor()
        cur_dst.execute("SELECT balance FROM accounts WHERE account_id = ?", (dst_acc,))
        d_row = cur_dst.fetchone()
        if d_row:
            dst_vote = "VOTE_COMMIT"
            print(f"  [Shard {dst_shard}] Destination account verified active. Responded: VOTE_COMMIT")
        else:
            print(f"  [Shard {dst_shard}] Destination account missing! Responded: VOTE_ABORT")

        print("  --- PHASE 2: COMMIT / ABORT PHASE ---")
        if src_vote == "VOTE_COMMIT" and dst_vote == "VOTE_COMMIT":
            print("  [COORDINATOR] Consensus achieved: All participants voted COMMIT. Executing global commit...")
            
            cur_src.execute("UPDATE accounts SET balance = balance - ? WHERE account_id = ?", (amount, src_acc))
            cur_src.execute("""
                INSERT INTO shard_transactions (tx_id, source_account_id, destination_account_id, amount, status)
                VALUES (?, ?, ?, ?, 'COMMITTED')
            """, (tx_id, src_acc, dst_acc, amount))
            conn_src.commit()

            cur_dst.execute("UPDATE accounts SET balance = balance + ? WHERE account_id = ?", (amount, dst_acc))
            cur_dst.execute("""
                INSERT INTO shard_transactions (tx_id, source_account_id, destination_account_id, amount, status)
                VALUES (?, ?, ?, ?, 'COMMITTED')
            """, (tx_id, src_acc, dst_acc, amount))
            conn_dst.commit()

            status = "GLOBAL_COMMIT_SUCCESS"
            print(f"  [COORDINATOR] Transfer {tx_id} completed successfully across Shard {src_shard} and Shard {dst_shard}!")
        else:
            print("  [COORDINATOR] Abort condition met. Rolling back all participating shards.")
            conn_src.rollback()
            conn_dst.rollback()
            status = "GLOBAL_ABORT"

        conn_src.close()
        conn_dst.close()
        return status

def run_sharding_demo():
    print("="*75)
    print("DISTRIBUTED DATABASE SHARDING & CROSS-SHARD 2PC COORDINATION")
    print("="*75)
    
    router = DistributedShardRouter(num_shards=3)

    accounts = [
        ("acc-cust001-usd", "cust-001", "ACC-101", "USD", 50000.0),
        ("acc-cust002-usd", "cust-002", "ACC-102", "USD", 12000.0),
        ("acc-cust003-usd", "cust-003", "ACC-103", "USD", 8500.0),
        ("acc-cust004-usd", "cust-004", "ACC-104", "USD", 34000.0),
        ("acc-cust005-usd", "cust-005", "ACC-105", "USD", 95000.0)
    ]

    print("\n[Step 1: Hash-Partitioned Account Distribution]")
    for acc in accounts:
        s_id = router.insert_account(*acc)
        print(f"  - Account: {acc[0]} | Customer: {acc[1]} -> Routed to Node: Shard {s_id}")

    for i in range(3):
        conn = sqlite3.connect(router.shard_paths[i])
        cnt = conn.execute("SELECT count(*) FROM accounts;").fetchone()[0]
        conn.close()
        print(f"  * Node Shard {i} hosting {cnt} active accounts.")

    print("\n[Step 2: Executing Successful Cross-Shard Transaction]")
    res1 = router.execute_cross_shard_2pc(
        "tx-2pc-001", "cust-001", "acc-cust001-usd", "cust-002", "acc-cust002-usd", 5000.0
    )

    print("\n[Step 3: Executing Cross-Shard Transaction with Insufficient Funds (Abort)]")
    res2 = router.execute_cross_shard_2pc(
        "tx-2pc-002", "cust-003", "acc-cust003-usd", "cust-004", "acc-cust004-usd", 999999.0
    )

    print("\n[Step 4: Post-Transaction Balances across Physical Shards]")
    s1, r1 = router.get_account("cust-001", "acc-cust001-usd")
    s2, r2 = router.get_account("cust-002", "acc-cust002-usd")
    s3, r3 = router.get_account("cust-003", "acc-cust003-usd")
    print(f"  - Shard {s1} | acc-cust001-usd Balance: ${r1[3]:,.2f} (Expected: $45,000.00)")
    print(f"  - Shard {s2} | acc-cust002-usd Balance: ${r2[3]:,.2f} (Expected: $17,000.00)")
    print(f"  - Shard {s3} | acc-cust003-usd Balance: ${r3[3]:,.2f} (Expected: $8,500.00 - Unchanged)")

if __name__ == "__main__":
    run_sharding_demo()
