import sqlite3
import json
import os
from datetime import datetime, timezone, timedelta

NOSQL_DB = 'advanced-database-portfolio/portfolio-4-nosql/finflow_nosql.db'

class FinFlowDocumentStore:
    def __init__(self, db_path=NOSQL_DB):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 1. Document Collection: transaction_telemetry
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transaction_telemetry (
                doc_id TEXT PRIMARY KEY,
                transaction_id TEXT NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                timestamp TEXT NOT NULL,
                data JSON NOT NULL
            );
        """)

        # 2. Key-Value / TTL Collection: idempotency_cache
        cur.execute("""
            CREATE TABLE IF NOT EXISTS idempotency_cache (
                cache_key TEXT PRIMARY KEY,
                status VARCHAR(20) NOT NULL,
                response_payload JSON NOT NULL,
                expires_at TEXT NOT NULL
            );
        """)

        # 3. Create Functional B-Tree Indexes on nested JSON attributes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_json_fraud_score 
            ON transaction_telemetry (json_extract(data, '$.risk_signals.fraud_score'));
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_json_device_fingerprint 
            ON transaction_telemetry (json_extract(data, '$.device_telemetry.device_fingerprint'));
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_json_jailbroken 
            ON transaction_telemetry (json_extract(data, '$.device_telemetry.is_jailbroken'));
        """)

        conn.commit()
        conn.close()

    def insert_document(self, doc):
        """Inserts a semi-structured JSON document with schema validation."""
        required = ["_id", "event_type", "transaction_id", "timestamp"]
        for field in required:
            if field not in doc:
                raise ValueError(f"Document missing required top-level field: {field}")

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO transaction_telemetry (doc_id, transaction_id, event_type, timestamp, data)
            VALUES (?, ?, ?, ?, ?)
        """, (doc["_id"], doc["transaction_id"], doc["event_type"], doc["timestamp"], json.dumps(doc)))
        conn.commit()
        conn.close()

    def set_idempotency_token(self, token, payload, ttl_seconds=86400):
        """Key-Value store operation simulating Redis SETEX key ttl value."""
        exp = (datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).isoformat()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO idempotency_cache (cache_key, status, response_payload, expires_at)
            VALUES (?, 'ACTIVE', ?, ?)
        """, (f"idemp:{token}", json.dumps(payload), exp))
        conn.commit()
        conn.close()

    def get_idempotency_token(self, token):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cur.execute("""
            SELECT response_payload FROM idempotency_cache 
            WHERE cache_key = ? AND expires_at > ?
        """, (f"idemp:{token}", now))
        row = cur.fetchone()
        conn.close()
        return json.loads(row[0]) if row else None

def seed_sample_documents():
    if os.path.exists(NOSQL_DB):
        try:
            os.remove(NOSQL_DB)
        except Exception:
            pass

    store = FinFlowDocumentStore()
    with open('advanced-database-portfolio/portfolio-4-nosql/02_sample_documents.json', 'r', encoding='utf-8') as f:
        docs = json.load(f)

    for doc in docs:
        store.insert_document(doc)

    store.set_idempotency_token(
        "idemp-20261101-001",
        {"status": "SUCCESS", "tx_id": "tx-10001", "settled_amount": 150000.0, "currency": "NGN"}
    )
    print(f"Successfully seeded {len(docs)} JSON documents and Key-Value tokens into NoSQL store.")

if __name__ == "__main__":
    seed_sample_documents()
