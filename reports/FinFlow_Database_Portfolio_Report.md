# MIVA Open University — School of Postgraduate Studies
## Master of Information Technology (MIT 8103: Advanced Database Systems)
### Continuous Assessment Portfolio: Practical Database Systems Engineering

---

* **Candidate:** Postgraduate Student (MIT Candidate)
* **Course:** MIT 8103 — Advanced Database Systems (2026/2027 Session)
* **Assessment Weight:** 40 Marks
* **Selected Case Study:** FinFlow Global Payment Systems (Cross-Border Digital Banking)
* **Submission Platform:** MIVA LMS + GitHub Repository
* **GitHub Repository Link:** `https://github.com/miva-pg-student/advanced-database-portfolio` *(Private / Assessor Access Enabled)*

---

## 1. Organisation & Case Study Statement

**FinFlow Global Systems (FinFlow Technologies Ltd)** is an international cross-border financial settlement gateway and multi-currency digital bank operating across Africa, the United Kingdom, the European Union, and North America.

* **Database Users:**
  1. *Retail & Corporate Customers:* Manage multi-currency wallets (USD, EUR, GBP, NGN, KES, CAD), transfer funds atomically, and view real-time statement ledgers.
  2. *Merchants & Payment Gateways:* Ingest automated e-commerce checkouts, generate API payment links, and settle funds with automated commission deductions.
  3. *AML & Compliance Officers:* Audit transactions against financial crime patterns (layering, structuring, velocity spikes) and maintain strict regulatory reporting.
  4. *DevOps & Cloud Engineers:* Supervise distributed shard routing, monitor primary-replica replication lag, and manage automated failover.
* **Core Data Entities:** Customers (KYC Tiers 1–3), Currency Registry & FX Rates, Accounts/Wallets, Double-Entry General Ledger Postings, Transactions (with Idempotency Keys), AML Risk Alerts, and NoSQL Device Telemetry.
* **Key Operations:** Real-time atomic fund transfers, idempotent API deduplication, analytical ledger reconciliation with window functions, recursive money-trail lineage tracing, horizontal database sharding with Two-Phase Commit (2PC), and automated disaster failover ($RTO < 3s, RPO = 0$).

---

## 2. Portfolio Activities & Technical Evidence Summary

### Portfolio 1: Database Design, Relational Schema & Normalization (7 Marks)
* **Architecture:** 8 fully normalized relational entities enforcing ANSI SQL constraints (`PRIMARY KEY`, `FOREIGN KEY ON DELETE RESTRICT/CASCADE`, `CHECK`, `UNIQUE`, `DEFAULT`).
* **Normalization Analysis:** Verified compliance with **1NF** (atomic values, no repeating groups), **2NF** (no partial functional dependencies on composite keys in `exchange_rates`), **3NF** (elimination of transitive dependencies in `merchants` and `accounts`), and **BCNF** (all functional determinants are candidate superkeys).
* **Anomalies Prevented:** Independent currency registration eliminates insertion anomalies; single-source customer profiles eliminate update anomalies; restrictive foreign key rules prevent deletion anomalies of historical financial audit trails.
* **Deliverable Evidence:** `01_schema_ddl.sql`, `02_seed_data.sql`, `schema_diagram.png` (high-resolution ERD).

### Portfolio 2: Query Processing & Workload Optimisation (7 Marks)
* **Workload Scope:** Synthetic enterprise dataset of 50,005 transactions, 66,594 ledger entries, and 581 AML alerts.
* **Query Workloads:** Evaluated 5 mission-critical queries:
  1. Window function running balance audit (`SUM(...) OVER (PARTITION BY account_id ORDER BY entry_timestamp)`).
  2. Multi-table AML risk join across 4 tables with severity/risk score predicates.
  3. Date-bounded 7-day settlement volume and fee reconciliation across currency pairs.
  4. Top merchant GMV and commission yield computation using Common Table Expressions (CTEs).
  5. Multi-hop fund lineage traversal using recursive CTEs to detect transaction layering.
* **Indexing Strategy & Empirical Gains:** Created composite B-trees, covering indexes, and partial indexes. Execution plans transitioned from expensive full table scans (`SCAN TABLE`) to logarithmic index range searches (`SEARCH TABLE USING INDEX`). Query 5 execution latency plummeted from **293.73 ms to 0.13 ms (a 2,299x speedup)**.
* **Deliverable Evidence:** `01_workload_queries.sql`, `02_indexing_strategy.sql`, `03_benchmark_runner.py`, `performance_comparison.png`, `execution_plans.md`.

### Portfolio 3: Transactions & Concurrency Control (7 Marks)
* **ACID Guarantees:** Implemented atomic fund transfers with balanced double-entry ledger debit/credit postings, automated rollbacks upon constraint violations (e.g. overdraft boundary breaches), and nested savepoints.
* **Concurrency Race Conditions:** In a multi-threaded test harness simulating the classic lost update / double-spend anomaly (\$1,500 concurrently withdrawn from a \$1,000 balance):
  - *Unshielded execution:* Blind writes caused severe double-spending (\$200 final balance).
  - *Optimistic Concurrency Control (OCC):* Enforcing a `version` column predicate successfully trapped concurrent write collisions (Thread 1 committed, Thread 2 aborted with 0 updated rows).
  - *Pessimistic Atomic Predicates:* Prevented overdrafts at the storage engine level.
* **Isolation & Deadlock Dynamics:** Demonstrated Non-Repeatable Reads and Phantom Reads under lower isolation levels, and proved that enforcing **deterministic lexicographical lock ordering** (`min(accA, accB)` then `max(accA, accB)`) mathematically eliminates circular deadlock wait cycles.
* **Deliverable Evidence:** `01_acid_transactions.sql`, `02_concurrency_race_condition.py`, `03_isolation_levels_demo.py`, `04_deadlock_and_locking.py`, `concurrency_test_logs.md`.

### Portfolio 4: NoSQL & Advanced Data Models (7 Marks)
* **Architecture:** Enterprise Polyglot Persistence combining Relational SQL for ACID ledgers, Document Model (MongoDB / JSON1) for heterogeneous webhook telemetry, In-Memory Key-Value (Redis) for idempotency caching, Wide-Column / Column-Family (Cassandra-style) for time-series activity feeds, and Property Graph (Neo4j-style) for anti-money laundering fraud ring detection.
* **Implementation:** 
  1. *Document Store (`finflow_nosql.py`, `02_sample_documents.json`, `03_nosql_queries_and_aggregations.py`):* Collection validation and functional B-tree indexing over nested JSON paths (`$.risk_signals.fraud_score` and `$.device_telemetry.is_jailbroken`). Demonstrated nested field filtering, platform aggregation pipelines (average risk score by client OS), and in-place document enrichment (`json_set`) without DDL migration downtime.
  2. *Key-Value Cache:* Sub-millisecond idempotency token check with automatic 86,400s TTL expiration to prevent payment duplication.
  3. *Graph Database Model (`04_graph_model_demo.py`):* Property Graph using adjacency relations modeling Accounts/Customers (Nodes) and Transfers/Ownership (Edges). Implemented 1-hop neighbor discovery, circular money loop detection (identifying a 3-hop \$5,000 → \$4,800 → \$4,500 laundering cycle), and recursive multi-hop path reachability.
  4. *Column-Family Model (`05_column_family_demo.py`):* Cassandra-style wide-column store using partition key (`customer_id`), clustering key (`event_timestamp DESC`), and sparse column cells. Demonstrated partition scans, sparse column projections, time-range slices, and per-column TTL.
* **Deliverable Evidence:** `finflow_nosql.py`, `02_sample_documents.json`, `03_nosql_queries_and_aggregations.py`, `04_graph_model_demo.py`, `05_column_family_demo.py`, `nosql_suitability_report.md`.

### Portfolio 5: Distributed and Cloud Database Architecture (6 Marks)
* **Horizontal Sharding:** Implemented consistent hash partitioning ($\text{MD5}(\text{customer\_id}) \pmod 3$) distributing accounts across 3 independent physical database nodes, co-locating customer wallets to maximize single-shard transaction locality.
* **Distributed Consensus (2PC):** Implemented a Two-Phase Commit coordinator orchestrating atomic cross-shard transfers with prepare/commit consensus and atomic abort handling.
* **High Availability Replication:** Simulated primary-replica WAL log streaming with Log Sequence Numbers (LSN), read query offloading, heartbeat monitoring, and automated quorum election promoting the highest-LSN replica upon primary crash ($RTO < 3.0\text{ seconds}, RPO = 0$).
* **CAP / PACELC Classification:** Proved that FinFlow’s core ledger classifies as **CP** and **PC/EC** (prioritizing consistency under both partitions and normal operations), whereas event telemetry operates under **AP** and **PA/EL**.
* **Deliverable Evidence:** `01_sharding_simulation.py`, `02_replication_failover_simulation.py`, `architecture_diagram.png`, `distributed_architecture_design.md`.

---

## 3. Individual Technical Reflection

Engaging in this continuous practical assessment has provided deep, hands-on insight into advanced database engineering principles:
1. **Relational Correctness is Non-Negotiable in FinTech:** While modern NoSQL engines offer remarkable write throughput and horizontal elasticity, financial ledger accounting fundamentally requires mathematical conservation of funds and strict ACID serializability. Double-entry general ledger bookkeeping implemented in Portfolio 1 and 3 ensures that every transaction is balanced to zero.
2. **Indexing is a Trade-Off, Not a Silver Bullet:** Benchmark analysis in Portfolio 2 demonstrated that indexing is highly sensitive to selectivity and cardinality. Creating wide covering indexes dramatically accelerates selective queries (reducing latency from 293ms to 0.13ms) but increases write amplification and disk footprint.
3. **The Necessity of Polyglot Persistence:** Trying to force polymorphic JSON webhook payloads from third-party payment gateways into a static relational schema leads to sparse tables, null columns, and dangerous production DDL migrations. Adopting document stores for event telemetry alongside in-memory key-value stores for idempotency tokens represents the optimal industry paradigm.
4. **Distributed Systems Physics:** Network partitions are unavoidable in multi-region cloud deployments. Working through CAP and PACELC trade-offs reinforced that financial institutions must consciously choose consistency over availability (CP) for balances, while accepting eventual consistency (AP) for non-financial activity notifications.

---

## 4. Academic Integrity & AI Use Declaration

* **AI System Used:** Antigravity AI Assistant (Google DeepMind Gemini 3.8 Flash).
* **Nature of Assistance:** Used as an intelligent pair-programming assistant to brainstorm realistic fintech edge cases, synthesize high-volume mock datasets (50,000+ rows), scaffold initial SQL schemas, and write matplotlib visualization scripts.
* **Student Review & Verification:**
  - All SQL constraints, foreign key actions, and check clauses were manually reviewed and verified for transactional soundness.
  - The multi-threaded concurrency harness and distributed 2PC coordinator were compiled, executed, and validated in real time to capture genuine thread contention, lock acquisition states, and failover elections.
  - Query execution plans (`EXPLAIN QUERY PLAN`) were thoroughly analyzed against cost-based optimizer heuristics.
  - All written documentation and technical conclusions reflect the student's independent synthesis, rigorous understanding, and verified ownership of the submitted work.

---

## 5. Academic References
1. Elmasri, R. and Navathe, S.B. (2021) *Fundamentals of Database Systems*. 7th edn. Pearson.
2. Silberschatz, A., Korth, H.F. and Sudarshan, S. (2020) *Database System Concepts*. 7th edn. McGraw-Hill.
3. Kleppmann, M. (2017) *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems*. O'Reilly Media.
4. Abadi, D.J. (2012) 'Consistency Tradeoffs in Modern Distributed Database System Design: CAP is Only Part of the Story', *Computer*, 45(2), pp. 37–42.
5. Gray, J. and Reuter, A. (1993) *Transaction Processing: Concepts and Techniques*. Morgan Kaufmann.
