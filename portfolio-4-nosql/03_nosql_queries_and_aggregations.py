import sqlite3
import json
from finflow_nosql import FinFlowDocumentStore, NOSQL_DB

def run_nosql_operations():
    store = FinFlowDocumentStore()
    conn = sqlite3.connect(NOSQL_DB)
    cur = conn.cursor()

    print("="*75)
    print("FINFLOW NoSQL DOCUMENT STORE & KEY-VALUE QUERY OPERATIONS")
    print("="*75)

    # 1. Deep Nested Path Filter (Security Fraud Rules)
    print("\n[QUERY 1: Nested Field Predicate Filtering]")
    print("Filter: device_telemetry.is_jailbroken = TRUE OR risk_signals.fraud_score >= 50.0")
    
    cur.execute("""
        SELECT 
            doc_id,
            transaction_id,
            json_extract(data, '$.customer.customer_id') AS customer_id,
            json_extract(data, '$.device_telemetry.os') AS client_os,
            json_extract(data, '$.device_telemetry.is_jailbroken') AS is_jailbroken,
            json_extract(data, '$.risk_signals.fraud_score') AS fraud_score,
            json_extract(data, '$.risk_signals.rules_triggered') AS triggered_rules
        FROM transaction_telemetry
        WHERE json_extract(data, '$.device_telemetry.is_jailbroken') = 1
           OR json_extract(data, '$.risk_signals.fraud_score') >= 50.0;
    """)
    rows = cur.fetchall()
    for r in rows:
        print(f"  - Document ID: {r[0]} | Tx: {r[1]} | Customer: {r[2]} | OS: {r[3]} | Jailbroken: {bool(r[4])} | Risk Score: {r[5]}")
        print(f"    Triggered Rules: {r[6]}")

    # 2. Aggregation Pipeline: Average Fraud Score & Event Count by Operating System
    print("\n[QUERY 2: Document Aggregation Pipeline by Client Platform]")
    cur.execute("""
        SELECT 
            json_extract(data, '$.device_telemetry.os') AS platform_os,
            COUNT(*) AS event_count,
            ROUND(AVG(json_extract(data, '$.risk_signals.fraud_score')), 2) AS avg_fraud_risk,
            MAX(json_extract(data, '$.risk_signals.fraud_score')) AS max_risk_score
        FROM transaction_telemetry
        GROUP BY platform_os
        ORDER BY avg_fraud_risk DESC;
    """)
    agg_rows = cur.fetchall()
    print(f"  {'Platform OS':<15} | {'Count':<7} | {'Avg Risk Score':<15} | {'Max Risk':<10}")
    print("  " + "-"*55)
    for a in agg_rows:
        print(f"  {a[0]:<15} | {a[1]:<7} | {a[2]:<15} | {a[3]:<10}")

    # 3. Polymorphic Payment Method Distribution
    print("\n[QUERY 3: Polymorphic Payment Method Breakdown]")
    cur.execute("""
        SELECT 
            json_extract(data, '$.payment_method.type') AS payment_type,
            json_extract(data, '$.payment_method.network') AS payment_network,
            COUNT(*) AS total_volume
        FROM transaction_telemetry
        GROUP BY payment_type, payment_network;
    """)
    method_rows = cur.fetchall()
    for m in method_rows:
        print(f"  - Payment Type: {m[0]:<18} | Network: {m[1]:<22} | Events: {m[2]}")

    # 4. JSON Array Inspection: Audit Trail Inspection
    print("\n[QUERY 4: Array Element Inspection ($elemMatch equivalent)]")
    cur.execute("""
        SELECT 
            doc_id,
            transaction_id,
            json_extract(data, '$.audit_trail') AS full_audit_trail
        FROM transaction_telemetry
        WHERE json_extract(data, '$.audit_trail') LIKE '%3DS_VERIFICATION%';
    """)
    audit_rows = cur.fetchall()
    for ar in audit_rows:
        stages = [s["stage"] for s in json.loads(ar[2])]
        print(f"  - Doc: {ar[0]} | Tx: {ar[1]} | Pipeline Stages Traversed: {' -> '.join(stages)}")

    # 5. Key-Value Store Operations (Simulating Redis Idempotency Cache)
    print("\n[QUERY 5: Key-Value Store Retrieval (Idempotency Token)]")
    cached = store.get_idempotency_token("idemp-20261101-001")
    print(f"  - Retrieved Token 'idemp-20261101-001': {json.dumps(cached, indent=4)}")

    # 6. Dynamic Schema Mutation (Adding a new nested field without DDL migration)
    print("\n[QUERY 6: Schema-Free In-Place Mutation ($set & $push)]")
    cur.execute("""
        UPDATE transaction_telemetry
        SET data = json_set(
            data, 
            '$.risk_signals.investigator_override', 'CLEARED_BY_MANUAL_REVIEW',
            '$.risk_signals.cleared_at', datetime('now')
        )
        WHERE doc_id = 'doc-evt-00102';
    """)
    conn.commit()

    cur.execute("SELECT json_extract(data, '$.risk_signals') FROM transaction_telemetry WHERE doc_id = 'doc-evt-00102'")
    updated_signals = json.loads(cur.fetchone()[0])
    print(f"  - Updated Risk Signals for doc-evt-00102 without altering database table schema:")
    print(f"    {json.dumps(updated_signals, indent=4)}")

    conn.close()
    print("\n[SUCCESS] NoSQL document modeling and query suite completed cleanly.")

if __name__ == "__main__":
    run_nosql_operations()
