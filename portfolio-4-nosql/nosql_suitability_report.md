# Portfolio 4: NoSQL and Advanced Data Models Suitability Analysis

**Student:** Olopha Oluwafeyikemi (Student ID: 301930634)  
**Course:** MIT 8103 Advanced Database Systems  
**Case Study:** FinFlow Global Systems  
**Architecture Paradigm:** Enterprise Polyglot Persistence  

---

## 1. Context & Motivation

FinFlow Global Systems operates at the intersection of high-frequency cross-border transactions, multi-currency accounting, and machine-learning-driven fraud detection. 

While the core financial ledger requires **strict ACID transactions** and normalized relational guarantees (as implemented in Portfolios 1–3), modern payment platforms face critical data access patterns that relational database management systems (RDBMS) cannot satisfy efficiently:

1. **Polymorphic Ingestion:** Payment gateways (Visa, Mastercard, SWIFT, SEPA, NIBSS, Open Banking APIs) return heterogeneous, deeply nested JSON payloads that evolve continuously.
2. **Device & Security Telemetry:** Every API request carries client telemetry (biometrics, device fingerprints, jailbreak detection flags, IP geolocations, velocity vectors) with varying attributes.
3. **Sub-Millisecond Idempotency Caching:** Distributed payment requests require sub-millisecond duplicate checks using transient keys with time-to-live (TTL) expiration.
4. **Schema Evolution Costs:** Executing relational `ALTER TABLE` DDL statements across tables with 100+ million records introduces catalog lock contention and operational downtime.

To solve these challenges, FinFlow employs a **Polyglot Persistence Architecture**.

---

## 2. Deep Comparative Model Evaluation

| Feature / Dimension | Relational (RDBMS) | Document Store (e.g., MongoDB) | Key-Value Store (e.g., Redis) | Graph Database (e.g., Neo4j) |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Data Model** | Relations (Tables, Rows, Foreign Keys) | Hierarchical JSON / BSON Documents | Key-Indexed Values (Strings, Hashes, Sets) | Nodes, Directed Relationships, Properties |
| **Schema Paradigm** | Schema-on-Write (Rigid DDL, Normalized) | Schema-on-Read (Dynamic, Polymorphic) | Schema-Free (Opaque Binary or JSON Strings) | Flexible Graph Schema |
| **ACID vs. BASE** | Full ACID (Strict Serializability) | Tunable Consistency (Single-doc ACID, BASE) | In-Memory Atomicity, Eventual Persistence | ACID-compliant Graph Transactions |
| **Query Mechanism** | Declarative SQL (Joins, CTEs, Windows) | Aggregation Pipelines, JSON path selectors | Direct Hash Lookups ($O(1)$ by Key) | Path Traversals (Cypher, Gremlin) |
| **Primary FinFlow Role** | Double-Entry General Ledger & Accounts | Transaction Telemetry, Webhooks, Fraud Features | Idempotency Tokens, Rate Limiting, FX Cache | Fraud Syndicate & Money Laundering Rings |

---

## 3. Practical Implementation Architecture in FinFlow

### 3.1 Document Store: Real-Time Transaction Telemetry & Fraud Store
The document collection `transaction_telemetry` stores multi-layered event footprints. As demonstrated in `01_nosql_document_store.py` and `03_nosql_queries_and_aggregations.py`:
- **Nested Attributes:** The document preserves natural entity hierarchies (customer metadata, card BIN details, client device telemetry, and risk rule outputs) in a single coherent unit.
- **Atomic Single-Document Writes:** Updating risk scoring flags or pushing new verification stages into the `audit_trail` array occurs atomically without multi-table joins.
- **Functional B-Tree Indexing:** Functional secondary indexes on `json_extract(data, '$.risk_signals.fraud_score')` and `json_extract(data, '$.device_telemetry.is_jailbroken')` allow rapid querying of suspicious transactions without scanning the collection.

### 3.2 Key-Value Store: Distributed Idempotency Token Engine
Network timeouts during payment calls can cause client retries. To prevent duplicate charges:
- Incoming requests present an `Idempotency-Key` header.
- FinFlow checks the in-memory Key-Value collection (`idempotency_cache`) in $< 1\text{ ms}$.
- If present, the previous response payload is returned immediately without re-executing ledger debits.
- Each token has an automatic Time-To-Live (TTL = 86,400s), eliminating manual table housekeeping.

### 3.3 Dynamic Schema Evolution Demonstration
When FinFlow introduced biometric verification (e.g., Apple FaceID vs Android Fingerprint) and investigator manual clearance overrides:
- In an RDBMS, this required multiple schema modifications:
  ```sql
  ALTER TABLE transactions ADD COLUMN biometrics_type VARCHAR(20);
  ALTER TABLE transactions ADD COLUMN investigator_notes TEXT;
  ```
- In the Document Store, new attributes are ingested immediately into `doc-evt-00102` using `json_set` without schema locking, downtime, or backward-compatibility breakage.

### 3.4 Graph Database: Fraud Syndicate and Money Laundering Ring Detection
As implemented in `04_graph_model_demo.py`, the graph model encodes FinFlow's transaction network as a **Property Graph** with:
- **Nodes:** Customers, Accounts, and Merchants with JSON property blobs.
- **Edges:** Directed relationships (`OWNS`, `TRANSFERRED_TO`, `PAID`) with transfer amounts and transaction IDs as edge properties.
- **Graph Traversal Queries:**
  1. **1-Hop Neighbor Discovery:** Identifies all direct transfer recipients from a given account.
  2. **Circular Transfer Detection (3-Hop Cycle):** Detects closed money loops (A → B → C → A) that indicate potential layering — a core AML red flag. The demo successfully detects a \$5,000 → \$4,800 → \$4,500 circular flow with \$500 net leakage per cycle.
  3. **Recursive Multi-Hop Reachability:** Uses a recursive CTE to trace all accounts reachable from a starting node, revealing the full blast radius of a compromised account.

**Why Graph over RDBMS for Fraud Detection?** Relational multi-hop joins degrade exponentially with path depth ($O(n^k)$ for $k$-hop joins across $n$ rows). Graph databases execute Cypher/Gremlin traversals in $O(k \cdot d)$ where $d$ is the average degree, making real-time fraud ring detection feasible at scale.

### 3.5 Column-Family (Wide-Column) Store: Time-Series Transaction Event Feeds
As implemented in `05_column_family_demo.py`, the column-family model simulates a Cassandra/HBase-style wide-column store for FinFlow's customer activity feed:
- **Partition Key:** `customer_id` — ensures all events for a single customer are co-located on the same physical node, enabling ultra-fast partition scans.
- **Clustering Key:** `event_timestamp` (descending) — maintains chronological ordering within each partition for efficient time-range queries.
- **Sparse Columns:** Each event type has a different column set (a P2P transfer has `amount`, `currency`, `destination`; a login event has `device`, `biometric_method`, `location`). Columns not present simply don't exist in that row — there are no NULL penalties.
- **Column-Level TTL:** Supports per-column expiration (e.g., session tokens expire after 24 hours), matching Cassandra's native TTL semantics.

**Why Column-Family for Activity Feeds?** Write-optimized LSM-tree storage engines (Cassandra, HBase) deliver $O(1)$ partition writes regardless of table width, making them ideal for high-velocity event ingestion at hundreds of thousands of writes per second.

---

## 4. Academic Conclusion: Why Polyglot Persistence Wins

No single database engine satisfies all enterprise computing dimensions:
- Using an RDBMS for high-volume unstructured webhook ingestion creates bloated tables, null columns, and severe schema migration risks.
- Using a Document Store for the double-entry accounting ledger risks ledger imbalances and concurrency double-spending due to weaker cross-document transactional isolation.

FinFlow combines the best of both paradigms: **Relational ACID for the Money, NoSQL Documents for the Context, and Key-Value for Velocity.**
