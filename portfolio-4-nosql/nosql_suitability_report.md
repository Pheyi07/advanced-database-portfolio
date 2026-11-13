# Portfolio 4: NoSQL and Advanced Data Models Suitability Analysis

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

---

## 4. Academic Conclusion: Why Polyglot Persistence Wins

No single database engine satisfies all enterprise computing dimensions:
- Using an RDBMS for high-volume unstructured webhook ingestion creates bloated tables, null columns, and severe schema migration risks.
- Using a Document Store for the double-entry accounting ledger risks ledger imbalances and concurrency double-spending due to weaker cross-document transactional isolation.

FinFlow combines the best of both paradigms: **Relational ACID for the Money, NoSQL Documents for the Context, and Key-Value for Velocity.**
