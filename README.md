# Advanced Database Systems Portfolio (MIT 8103)
**Institution:** School of Postgraduate Studies, MIVA Open University  
**Degree Programme:** Master of Information Technology (M.Sc. IT)  
**Academic Session:** 2026/2027 Academic Session | First Semester Continuous Assessment  
**Total Assessment Marks:** 40 Marks  
**Submission Platform:** LMS + GitHub  
**Author / Student:** Postgraduate Researcher (MIVA MIT Candidate)  

---

## 1. Database Case Study Statement

* **Organisation Name:** FinFlow Global Payment Systems (FinFlow Technologies Ltd)
* **Nature of Business / System:** Cloud-Native Multi-Currency Cross-Border Digital Banking, Merchant Settlement Gateway, and Automated AML Compliance Platform.
* **Database Users:**
  1. *Retail & Corporate Account Holders:* Execute atomic international remittances, currency conversions, wallet debits/credits, and view real-time balances.
  2. *Merchants & Payment Gateways:* Ingest automated e-commerce checkouts, generate dynamic QR codes, settle revenues, and receive webhook notifications.
  3. *AML & Compliance Investigators:* Scrutinize flagged transactions, monitor structuring and velocity patterns, and audit double-entry ledger trails.
  4. *FinTech Operations Engineers:* Supervise liquidity pools, manage inter-shard routing, monitor replication lag, and orchestrate automated failover.
* **Major Data Stored:**
  - Customer identity profiles (KYC Tiers 1–3, biometric markers, country jurisdictions).
  - Multi-currency digital accounts/wallets (USD, EUR, GBP, NGN, KES, CAD) with available, locked, and reserve balances.
  - Historical and real-time Foreign Exchange (FX) matrices.
  - Transactions with unique idempotency keys, payment methods, fees, and lifecycle states.
  - Immutable double-entry general ledger entries (`DEBIT` and `CREDIT` pairs) ensuring absolute conservation of funds.
  - Compliance risk alerts and rules engine triggers.
  - Polymorphic semi-structured JSON client telemetry (device fingerprints, jailbreak detection, IP geolocations, webhook callbacks).
* **Key Operations Supported:**
  - High-throughput atomic multi-currency transfers under strict ACID isolation.
  - Distributed idempotency checks with sub-millisecond in-memory TTL token lookups.
  - Analytical ledger auditing with window functions (`OVER PARTITION BY`) and recursive multi-hop transfer lineage tracing.
  - Horizontal hash-based database sharding and cross-shard Two-Phase Commit (2PC) consensus.
  - Multi-region primary-replica log streaming with automated quorum leader election and zero data loss failover.

---

## 2. Repository Structure

```
advanced-database-portfolio/
│
├── portfolio-1-database-design/
│   ├── 01_schema_ddl.sql               # Production ANSI SQL DDL creating 8 normalized tables
│   ├── 02_seed_data.sql                # Comprehensive seed dataset (currencies, accounts, transactions)
│   ├── generate_erd.py                 # Script generating high-resolution ER diagram
│   ├── schema_diagram.png              # High-resolution Entity-Relationship Diagram graphic
│   ├── normalization_report.md         # Academic analysis validating 1NF, 2NF, 3NF, BCNF & anomalies
│   ├── verify_portfolio_1.py           # Automated schema and constraint validation test suite
│   └── README.md                       # Activity documentation and design decisions
│
├── portfolio-2-query-optimisation/
│   ├── 01_workload_queries.sql         # 5 complex analytical & operational workloads (Window, CTE, Joins)
│   ├── 02_indexing_strategy.sql        # Strategic B-Tree, composite, covering, and partial index DDL
│   ├── 03_benchmark_runner.py          # 50,000-row automated benchmark harness with EXPLAIN plans
│   ├── benchmark_results.json          # Machine-readable query latencies and speedup ratios
│   ├── execution_plans.md              # Detailed query plan analysis before and after indexing
│   ├── performance_comparison.png      # High-resolution benchmark comparison chart
│   └── README.md                       # Optimization takeaways and selectivity tipping point analysis
│
├── portfolio-3-transactions-concurrency/
│   ├── 01_acid_transactions.sql        # Atomic transfer, constraint violation rollback, and savepoints
│   ├── 02_concurrency_race_condition.py# Multi-threaded harness demonstrating lost update, OCC, and locks
│   ├── 03_isolation_levels_demo.py     # ANSI SQL isolation level anomalies (Non-repeatable reads, phantoms)
│   ├── 04_deadlock_and_locking.py      # Deadlock cycle generator & deadlock prevention via lock ordering
│   ├── concurrency_test_logs.md        # Verified console execution logs and thread timeline traces
│   └── README.md                       # Deep explanation of ACID, MVCC, and Two-Phase Locking (2PL)
│
├── portfolio-4-nosql/
│   ├── finflow_nosql.py                # NoSQL document engine & key-value TTL store implementation
│   ├── 01_nosql_document_store.py      # Document collection manager with functional B-tree JSON indexes
│   ├── 02_sample_documents.json        # Rich polymorphic payment webhook & device telemetry documents
│   ├── 03_nosql_queries_and_aggregations.py # Nested JSON filtering, platform aggregations, and in-place updates
│   ├── 04_graph_model_demo.py          # Property Graph model: adjacency tables, 1-hop traversals & fraud ring detection
│   ├── 05_column_family_demo.py        # Wide-Column store: sparse schema, partition scans, clustering keys & TTL
│   ├── nosql_suitability_report.md     # Comparative model evaluation & Polyglot Persistence justification
│   └── README.md                       # Activity guide and schema-free evolution overview
│
├── portfolio-5-distributed-cloud/
│   ├── 01_sharding_simulation.py       # Hash-partitioned horizontal sharding & cross-shard 2PC coordinator
│   ├── 02_replication_failover_simulation.py # Primary-replica log streaming & automated quorum failover
│   ├── generate_architecture_diagram.py# Script generating cloud architecture topology diagram
│   ├── architecture_diagram.png        # High-resolution multi-region distributed cloud topology blueprint
│   ├── distributed_architecture_design.md # In-depth analysis of sharding, failover, CAP, and PACELC proofs
│   └── README.md                       # Distributed systems engineering documentation
│
├── reports/
│   ├── FinFlow_Database_Portfolio_Report.md   # Complete 12-page comprehensive master technical report
│   ├── FinFlow_Database_Portfolio_Report.docx # Formatted Word submission report (LMS ready)
│   └── FinFlow_Database_Portfolio_Report.pdf  # Publication-grade PDF submission document (LMS ready)
│
├── run_all_experiments.py              # Master test runner executing all 5 portfolio suites end-to-end
└── README.md                           # Master repository documentation (this file)
```

---

## 3. Portfolio Summary & Key Findings

| Component | Marks | Key Practical Evidence | Highlighted Metric / Result |
| :--- | :---: | :--- | :--- |
| **Portfolio 1: Database Design** | 7 | 8 normalized tables in BCNF, constraints, seed dataset, high-res ERD graphic | Zero redundancy; eliminates insertion, update & deletion anomalies |
| **Portfolio 2: Query Optimisation** | 7 | 50,000 transactions, 65,000+ ledger entries benchmarked across 5 queries | **Up to 1,000x query speedup**; table scans eliminated via covering B-trees |
| **Portfolio 3: Transactions & Concurrency** | 7 | Multi-threaded race condition tests, OCC version validation, deadlock ordering | **Lost update double-spend prevented**; strict balance invariants preserved |
| **Portfolio 4: NoSQL & Advanced Models** | 7 | Document, Key-Value, Column-Family, and Graph models with empirical queries | Sub-millisecond idempotency lookup; circular fraud ring detection; schema-free event telemetry |
| **Portfolio 5: Distributed & Cloud** | 6 | Horizontal sharding by customer hash, 2PC consensus, replica failover simulation | **RTO < 3.0 seconds, RPO = 0**; formal CAP (CP) & PACELC (PC/EC) validation |
| **Final Documentation & Reflection** | 6 | 2–3 page summary report, comprehensive reflection, references, AI declaration | LMS-ready PDF & DOCX reports adhering to academic rubric |
| **Total** | **40** | **Complete Practical Evidence** | **100% Production-Tested & Verified** |

---

## 4. How to Execute the Entire Portfolio

To execute all tests, benchmarks, simulations, and diagram generators in a single pass:

```bash
# Clone the repository
git clone https://github.com/Pheyi07/advanced-database-portfolio.git
cd advanced-database-portfolio

# Run the master automated execution runner
python run_all_experiments.py
```

---

## 5. Technical Reflection & AI Use Declaration

### 5.1 Technical Reflection
Developing this practical portfolio underscored the reality that no single database engine or paradigm is universally optimal. In designing FinFlow:
1. **The Primacy of Mathematical Invariants:** The double-entry general ledger demands strict relational normalization (3NF/BCNF) and serializable transactions. Using NoSQL for financial balance bookkeeping would invite race conditions and double-spending under high concurrency.
2. **The Power and Limits of Indexing:** While targeted B-tree indexes produced up to 1,000x speedups on selective queries, low-cardinality filters demonstrated the "selectivity tipping point", where index seeks cost more than sequential page scans.
3. **Polyglot Persistence as the Industry Standard:** Combining an RDBMS for ACID ledgers, a Document Store for heterogeneous device telemetry, and an In-Memory Key-Value store for idempotency tokens represents the true state-of-the-art in scalable fintech engineering.
4. **Distributed Trade-Offs:** The CAP and PACELC theorems are not abstract theories but daily engineering trade-offs. For core ledgers, FinFlow correctly trades regional availability during partitions to guarantee absolute financial consistency.

### 5.2 Academic Integrity & AI Use Declaration
* **AI Tools Utilized:** Antigravity AI Assistant (Google DeepMind Gemini 3.8 Flash).
* **Specific Role of AI:** Used as an intelligent pair programmer and technical sounding board to brainstorm architectural scenarios, generate high-volume synthetic mock datasets, scaffold initial SQL schemas, and format publication-style matplotlib visualization scripts.
* **Student Review, Correction & Verification:**
  - All SQL DDL scripts were manually reviewed for relational constraint validity (`ON DELETE RESTRICT`, `CHECK` bounds).
  - The multi-threaded concurrency scripts were executed, debugged, and validated to ensure live thread contention reproduces authentic race conditions and deadlock exceptions.
  - Benchmark query plans (`EXPLAIN QUERY PLAN`) were verified against SQLite query planner internals to confirm index scans versus table scans.
  - All documentation, reflections, and analyses were rigorously scrutinized for technical accuracy and adherence to MIVA Open University academic standards.
