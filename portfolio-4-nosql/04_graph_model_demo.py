"""
MIT 8103 Advanced Database Systems - Portfolio 4
Case Study: FinFlow Global Systems

04_graph_model_demo.py — Graph Database Model Demonstration
Simulates a Property Graph for fraud ring detection using adjacency tables.
Models: Nodes (accounts/customers) and Edges (fund transfers) with properties.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finflow_graph.db")


def setup_graph_schema(conn):
    """Create a Property Graph schema using adjacency tables."""
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS graph_edges;
        DROP TABLE IF EXISTS graph_nodes;

        -- NODES: Represent accounts, customers, merchants in the graph
        CREATE TABLE graph_nodes (
            node_id     TEXT PRIMARY KEY,
            node_type   TEXT NOT NULL CHECK (node_type IN ('CUSTOMER', 'ACCOUNT', 'MERCHANT')),
            properties  TEXT NOT NULL  -- JSON properties blob
        );

        -- EDGES: Represent directed relationships (transfers, ownership)
        CREATE TABLE graph_edges (
            edge_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            source_node_id  TEXT NOT NULL REFERENCES graph_nodes(node_id),
            target_node_id  TEXT NOT NULL REFERENCES graph_nodes(node_id),
            edge_type       TEXT NOT NULL CHECK (edge_type IN ('OWNS', 'TRANSFERRED_TO', 'PAID')),
            properties      TEXT NOT NULL DEFAULT '{}',  -- JSON edge properties
            created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX idx_edges_source ON graph_edges(source_node_id, edge_type);
        CREATE INDEX idx_edges_target ON graph_edges(target_node_id, edge_type);
    """)
    conn.commit()
    print("[GRAPH MODEL] Schema created: graph_nodes, graph_edges with adjacency indexes.")


def seed_graph_data(conn):
    """Seed a transaction network graph for fraud analysis."""
    cur = conn.cursor()

    # Insert customer and account nodes
    nodes = [
        ("cust-001", "CUSTOMER", '{"name": "Adebayo Okonkwo", "kyc_tier": 3, "country": "NGA"}'),
        ("cust-002", "CUSTOMER", '{"name": "Maria Schmidt", "kyc_tier": 2, "country": "DEU"}'),
        ("cust-003", "CUSTOMER", '{"name": "James Okafor", "kyc_tier": 1, "country": "NGA"}'),
        ("cust-004", "CUSTOMER", '{"name": "Shell Company LLC", "kyc_tier": 1, "country": "VGB"}'),
        ("acc-001",  "ACCOUNT",  '{"currency": "USD", "balance": 45000.00}'),
        ("acc-002",  "ACCOUNT",  '{"currency": "EUR", "balance": 12000.00}'),
        ("acc-003",  "ACCOUNT",  '{"currency": "USD", "balance": 8500.00}'),
        ("acc-004",  "ACCOUNT",  '{"currency": "USD", "balance": 95000.00}'),
        ("merch-01", "MERCHANT", '{"business": "TechMart Lagos", "mcc": "5411"}'),
    ]
    cur.executemany("INSERT INTO graph_nodes VALUES (?, ?, ?)", nodes)

    # Insert edges: ownership and transfers
    edges = [
        ("cust-001", "acc-001", "OWNS",           '{}'),
        ("cust-002", "acc-002", "OWNS",           '{}'),
        ("cust-003", "acc-003", "OWNS",           '{}'),
        ("cust-004", "acc-004", "OWNS",           '{}'),
        # Transfer chain: cust-001 -> cust-003 -> cust-004 (potential layering)
        ("acc-001",  "acc-003", "TRANSFERRED_TO", '{"amount": 5000, "currency": "USD", "tx_id": "tx-g-001"}'),
        ("acc-003",  "acc-004", "TRANSFERRED_TO", '{"amount": 4800, "currency": "USD", "tx_id": "tx-g-002"}'),
        # Circular transfer: cust-004 -> cust-001 (suspicious loop)
        ("acc-004",  "acc-001", "TRANSFERRED_TO", '{"amount": 4500, "currency": "USD", "tx_id": "tx-g-003"}'),
        # Merchant payment
        ("acc-002",  "merch-01", "PAID",          '{"amount": 250, "currency": "EUR", "tx_id": "tx-g-004"}'),
    ]
    cur.executemany(
        "INSERT INTO graph_edges (source_node_id, target_node_id, edge_type, properties) VALUES (?, ?, ?, ?)",
        edges
    )
    conn.commit()
    print(f"[GRAPH MODEL] Seeded {len(nodes)} nodes and {len(edges)} edges.")


def query_1_direct_neighbors(conn):
    """Find all direct outgoing transfers from a given account (1-hop traversal)."""
    print("\n--- GRAPH QUERY 1: Direct Neighbors (1-Hop Outgoing Transfers from acc-001) ---")
    cur = conn.cursor()
    cur.execute("""
        SELECT e.target_node_id,
               json_extract(e.properties, '$.amount') AS amount,
               json_extract(e.properties, '$.currency') AS currency,
               json_extract(n.properties, '$.name') AS recipient_owner
        FROM graph_edges e
        JOIN graph_edges ownership ON ownership.target_node_id = e.target_node_id
                                   AND ownership.edge_type = 'OWNS'
        JOIN graph_nodes n ON n.node_id = ownership.source_node_id
        WHERE e.source_node_id = 'acc-001'
          AND e.edge_type = 'TRANSFERRED_TO'
    """)
    # Fallback: simpler query if ownership edges point customer->account
    cur.execute("""
        SELECT e.target_node_id,
               json_extract(e.properties, '$.amount') AS amount,
               json_extract(e.properties, '$.currency') AS currency
        FROM graph_edges e
        WHERE e.source_node_id = 'acc-001'
          AND e.edge_type = 'TRANSFERRED_TO'
    """)
    for row in cur.fetchall():
        print(f"  -> {row[0]} | Amount: ${row[1]} {row[2]}")


def query_2_circular_transfer_detection(conn):
    """Detect circular money flows (potential money laundering rings)."""
    print("\n--- GRAPH QUERY 2: Circular Transfer Detection (Fraud Ring Analysis) ---")
    cur = conn.cursor()
    # Find 3-hop cycles: A -> B -> C -> A
    cur.execute("""
        SELECT e1.source_node_id AS hop1_from,
               e1.target_node_id AS hop2_from,
               e2.target_node_id AS hop3_from,
               e3.target_node_id AS returns_to,
               json_extract(e1.properties, '$.amount') AS amount_1,
               json_extract(e2.properties, '$.amount') AS amount_2,
               json_extract(e3.properties, '$.amount') AS amount_3
        FROM graph_edges e1
        JOIN graph_edges e2 ON e2.source_node_id = e1.target_node_id
                            AND e2.edge_type = 'TRANSFERRED_TO'
        JOIN graph_edges e3 ON e3.source_node_id = e2.target_node_id
                            AND e3.edge_type = 'TRANSFERRED_TO'
        WHERE e1.edge_type = 'TRANSFERRED_TO'
          AND e3.target_node_id = e1.source_node_id
    """)
    cycles = cur.fetchall()
    if cycles:
        for c in cycles:
            print(f"  [ALERT] Circular flow detected: {c[0]} -> {c[1]} -> {c[2]} -> {c[3]}")
            print(f"          Amounts: ${c[4]} -> ${c[5]} -> ${c[6]}")
            total_leakage = (float(c[4]) - float(c[6]))
            print(f"          Net leakage per cycle: ${total_leakage:.2f}")
    else:
        print("  No circular transfers detected.")


def query_3_multi_hop_path(conn):
    """Recursive CTE to find all reachable accounts from a starting node."""
    print("\n--- GRAPH QUERY 3: Multi-Hop Reachability (All Accounts Reachable from acc-001) ---")
    cur = conn.cursor()
    cur.execute("""
        WITH RECURSIVE reachable(node_id, depth, path) AS (
            SELECT 'acc-001', 0, 'acc-001'
            UNION ALL
            SELECT e.target_node_id, r.depth + 1, r.path || ' -> ' || e.target_node_id
            FROM reachable r
            JOIN graph_edges e ON e.source_node_id = r.node_id
            WHERE e.edge_type = 'TRANSFERRED_TO'
              AND r.depth < 5
              AND r.path NOT LIKE '%' || e.target_node_id || '%'
        )
        SELECT node_id, depth, path
        FROM reachable
        WHERE depth > 0
        ORDER BY depth
    """)
    for row in cur.fetchall():
        print(f"  Depth {row[1]}: {row[2]}")


def main():
    print("=" * 70)
    print("PORTFOLIO 4: GRAPH DATABASE MODEL — FRAUD RING DETECTION")
    print("Case Study: FinFlow Global Payment Systems")
    print("=" * 70)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    setup_graph_schema(conn)
    seed_graph_data(conn)
    query_1_direct_neighbors(conn)
    query_2_circular_transfer_detection(conn)
    query_3_multi_hop_path(conn)

    conn.close()
    print("\n[GRAPH MODEL COMPLETE] All graph traversal queries executed successfully.")


if __name__ == "__main__":
    main()
