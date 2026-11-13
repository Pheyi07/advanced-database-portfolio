"""
MIT 8103 Advanced Database Systems - Portfolio 4
Case Study: FinFlow Global Systems

05_column_family_demo.py — Wide-Column / Column-Family Model Demonstration
Simulates a Cassandra/HBase-style column-family store using sparse column groups.
Use case: Time-series transaction event logging and activity feeds.
"""

import sqlite3
import json
import os
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finflow_columnfamily.db")


def setup_column_family_schema(conn):
    """
    Simulate a wide-column store.
    In Cassandra/HBase, each row has a partition key and can have an arbitrary
    number of columns per column family. We simulate this with:
      - A partition key (row_key)
      - A clustering key (column_name) for column ordering within a partition
      - A value column storing the cell data
    This is the canonical relational encoding of a wide-column store.
    """
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS column_family_events;

        -- Column Family: transaction_events
        -- Partition Key: customer_id (data locality per customer)
        -- Clustering Key: event_timestamp DESC (most recent events first)
        CREATE TABLE column_family_events (
            partition_key   TEXT NOT NULL,         -- e.g., 'cust-001'
            clustering_key  TEXT NOT NULL,         -- e.g., '2026-11-13T10:30:00Z'
            column_name     TEXT NOT NULL,         -- e.g., 'amount', 'currency', 'status'
            column_value    TEXT,                  -- Cell value (sparse - may be NULL)
            ttl_expires_at  TIMESTAMP,             -- Optional TTL for column expiry
            PRIMARY KEY (partition_key, clustering_key, column_name)
        );

        -- Simulate Cassandra's partition-aware query optimization
        CREATE INDEX idx_cf_partition ON column_family_events(partition_key);
    """)
    conn.commit()
    print("[COLUMN-FAMILY] Schema created: column_family_events (wide-column simulation).")


def insert_wide_row(conn, partition_key, clustering_key, columns, ttl_seconds=None):
    """Insert a wide row with arbitrary columns (simulates Cassandra INSERT)."""
    cur = conn.cursor()
    ttl_ts = None
    if ttl_seconds:
        ttl_ts = (datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).isoformat()

    for col_name, col_value in columns.items():
        cur.execute(
            "INSERT OR REPLACE INTO column_family_events VALUES (?, ?, ?, ?, ?)",
            (partition_key, clustering_key, col_name, str(col_value) if col_value is not None else None, ttl_ts)
        )
    conn.commit()


def seed_column_family_data(conn):
    """Seed time-series transaction events in wide-column format."""
    # Customer cust-001 events
    insert_wide_row(conn, "cust-001", "2026-11-13T09:00:00Z", {
        "event_type": "P2P_TRANSFER",
        "amount": "5000.00",
        "currency": "USD",
        "destination": "acc-003-usd",
        "status": "COMPLETED",
        "risk_score": "12.5",
        "ip_address": "105.112.45.67",
    })
    insert_wide_row(conn, "cust-001", "2026-11-13T09:15:00Z", {
        "event_type": "CURRENCY_EXCHANGE",
        "source_amount": "2000.00",
        "source_currency": "USD",
        "target_amount": "1840.00",
        "target_currency": "EUR",
        "exchange_rate": "0.92",
        "status": "COMPLETED",
    })
    insert_wide_row(conn, "cust-001", "2026-11-13T10:30:00Z", {
        "event_type": "LOGIN",
        "device": "iPhone 15 Pro",
        "biometric_method": "FaceID",
        "location": "Lagos, Nigeria",
    })

    # Customer cust-002 events (different column set — schema-free)
    insert_wide_row(conn, "cust-002", "2026-11-13T08:45:00Z", {
        "event_type": "MERCHANT_PAYMENT",
        "amount": "250.00",
        "currency": "EUR",
        "merchant_name": "TechMart Berlin",
        "mcc": "5411",
        "card_last4": "7823",
        "3ds_verified": "true",
    })
    insert_wide_row(conn, "cust-002", "2026-11-13T11:00:00Z", {
        "event_type": "AML_ALERT",
        "alert_severity": "HIGH",
        "rule_code": "VELOCITY_24H",
        "flagged_amount": "15000.00",
        "investigator_assigned": "Officer K. Mueller",
    })

    print("[COLUMN-FAMILY] Seeded 5 wide rows across 2 customer partitions.")


def query_1_partition_scan(conn):
    """Retrieve all events for a customer partition (Cassandra partition scan)."""
    print("\n--- COLUMN-FAMILY QUERY 1: Partition Scan (All Events for cust-001) ---")
    cur = conn.cursor()
    cur.execute("""
        SELECT clustering_key, column_name, column_value
        FROM column_family_events
        WHERE partition_key = 'cust-001'
        ORDER BY clustering_key DESC, column_name
    """)
    current_ts = None
    for row in cur.fetchall():
        if row[0] != current_ts:
            current_ts = row[0]
            print(f"\n  Event @ {current_ts}:")
        print(f"    {row[1]}: {row[2]}")


def query_2_sparse_column_retrieval(conn):
    """Retrieve specific columns from wide rows (column projection)."""
    print("\n--- COLUMN-FAMILY QUERY 2: Column Projection (amount + currency columns only) ---")
    cur = conn.cursor()
    cur.execute("""
        SELECT partition_key, clustering_key, column_name, column_value
        FROM column_family_events
        WHERE column_name IN ('amount', 'currency', 'source_amount', 'source_currency')
        ORDER BY partition_key, clustering_key
    """)
    for row in cur.fetchall():
        print(f"  [{row[0]}] {row[1]} | {row[2]} = {row[3]}")


def query_3_time_range_slice(conn):
    """Time-range scan within a partition (Cassandra clustering key range query)."""
    print("\n--- COLUMN-FAMILY QUERY 3: Time-Range Slice (cust-001 events after 09:10) ---")
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT clustering_key,
               GROUP_CONCAT(column_name || '=' || COALESCE(column_value, 'NULL'), '; ')
        FROM column_family_events
        WHERE partition_key = 'cust-001'
          AND clustering_key > '2026-11-13T09:10:00Z'
        GROUP BY clustering_key
        ORDER BY clustering_key
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")


def query_4_schema_free_demonstration(conn):
    """Show that different partitions have different columns (schema-free property)."""
    print("\n--- COLUMN-FAMILY QUERY 4: Schema-Free Column Diversity ---")
    cur = conn.cursor()
    cur.execute("""
        SELECT partition_key,
               COUNT(DISTINCT column_name) AS unique_columns,
               GROUP_CONCAT(DISTINCT column_name) AS columns_present
        FROM column_family_events
        GROUP BY partition_key
    """)
    for row in cur.fetchall():
        print(f"  [{row[0]}] {row[1]} unique columns: {row[2]}")


def main():
    print("=" * 70)
    print("PORTFOLIO 4: COLUMN-FAMILY (WIDE-COLUMN) MODEL DEMONSTRATION")
    print("Case Study: FinFlow Global Payment Systems")
    print("=" * 70)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    setup_column_family_schema(conn)
    seed_column_family_data(conn)
    query_1_partition_scan(conn)
    query_2_sparse_column_retrieval(conn)
    query_3_time_range_slice(conn)
    query_4_schema_free_demonstration(conn)

    conn.close()
    print("\n[COLUMN-FAMILY COMPLETE] All wide-column queries executed successfully.")


if __name__ == "__main__":
    main()
