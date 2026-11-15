# Portfolio 2: Query Processing and Optimisation

**Student:** Olopha Oluwafeyikemi (Student ID: 301930634)  
**Course:** MIT 8103 Advanced Database Systems  
**Case Study:** FinFlow Global Systems  
**Deliverables Covered:**
1. Advanced SQL workload queries (Window functions, CTEs, Multi-table joins, Recursive traversals, Aggregations)
2. Strategic indexing DDL (`idx_ledger_account_time`, `idx_tx_risk_status`, `idx_tx_settlement_covering`, etc.)
3. Automated benchmarking harness (`03_benchmark_runner.py`)
4. Execution plans before and after optimization (`EXPLAIN QUERY PLAN`)
5. Empirical speedup metrics and visual comparative chart (`performance_comparison.png`)

---

## Directory Contents

- **`01_workload_queries.sql`**: Production analytical and transactional query scripts representing core FinFlow business queries:
  - **Q1**: Ledger running balance audit with cumulative window frames (`ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`) and inter-transaction velocity.
  - **Q2**: High-risk AML fraud pattern detection joining transactions, accounts, customers, and compliance alert tables.
  - **Q3**: End-of-day multi-currency settlement volume and fee reconciliation grouped by currency pair and date.
  - **Q4**: Common Table Expression (CTE) computing merchant Gross Merchandise Value (GMV), net commission yield, and average ticket size.
  - **Q5**: Recursive CTE tracing multi-hop fund lineage across accounts to uncover transaction layering and circular transfers.
- **`02_indexing_strategy.sql`**: Targeted B-tree indexing scripts, composite keys, covering indexes, and partial filtered indexes.
- **`03_benchmark_runner.py`**: Python benchmarking suite that loads 50,000 transactions and 100,000 ledger rows, benchmarks unindexed queries, applies indexes, records query plans, and generates visual charts.
- **`benchmark_results.json`**: Machine-readable latency and speedup results.
- **`execution_plans.md`**: Detailed comparative execution plan breakdown showing scan reductions, B-tree search transitions, and cost improvements.
- **`performance_comparison.png`**: High-resolution chart depicting the logarithmic latency drop and speedup factors.

---

## Execution Instructions

To re-run the benchmark suite from scratch:
```bash
python 03_benchmark_runner.py
```
This automatically updates `benchmark_results.json`, `execution_plans.md`, and `performance_comparison.png`.
