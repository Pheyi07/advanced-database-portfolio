# Portfolio 3: Transactions and Concurrency

**Course:** MIT 8103 Advanced Database Systems  
**Case Study:** FinFlow Global Systems  
**Deliverables Covered:**
1. Transaction examples illustrating COMMIT, ROLLBACK, and SAVEPOINTS (`01_acid_transactions.sql`)
2. Multi-threaded race condition and double-spend test harness (`02_concurrency_race_condition.py`)
3. Optimistic Concurrency Control (OCC with version column) implementation
4. ANSI SQL isolation levels and anomaly demonstration (Non-Repeatable Read, Phantom Read) (`03_isolation_levels_demo.py`)
5. Deadlock cycle simulation and deadlock prevention via global resource ordering (`04_deadlock_and_locking.py`)
6. Comprehensive execution output logs (`concurrency_test_logs.md`)

---

## Directory Contents

- **`01_acid_transactions.sql`**: Production SQL scripts showcasing atomic double-entry bookkeeping commits, automatic rollback upon constraint breach, and savepoint rollbacks.
- **`02_concurrency_race_condition.py`**: Multi-threaded concurrency simulation exhibiting the lost update / double-spend anomaly and contrasting it with OCC version validation and atomic predicate locking.
- **`03_isolation_levels_demo.py`**: Practical demonstration of ANSI SQL isolation levels and concurrency phenomena (dirty reads, non-repeatable reads, phantom reads).
- **`04_deadlock_and_locking.py`**: Deadlock cycle generator and deadlock prevention via deterministic lexicographical lock ordering (`min(id1, id2)` then `max(id1, id2)`).
- **`concurrency_test_logs.md`**: Verified execution logs capturing console traces, thread interleavings, and balance state changes.

---

## How to Run Tests

Run the complete suite of concurrency and transaction experiments:
```bash
python 02_concurrency_race_condition.py
python 03_isolation_levels_demo.py
python 04_deadlock_and_locking.py
```
