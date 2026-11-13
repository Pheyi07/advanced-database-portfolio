# Portfolio 3: Transactions and Concurrency Analysis Report

**Course:** MIT 8103 Advanced Database Systems  
**Case Study:** FinFlow Global Systems  
**Core Assessment Focus:** ACID Guarantees, Isolation Levels, Lost Updates, Optimistic Concurrency Control (OCC), Deadlock Dynamics  

---

## 1. Executive Overview

Financial ledger systems must enforce strict mathematical invariants: money cannot be created or destroyed, accounts cannot be concurrently double-spent, and parallel transactions must not observe partial or uncommitted states.

This portfolio documents empirical test results demonstrating transactional atomicity, concurrency anomalies, and modern concurrency control mechanisms.

---

## 2. Practical Evidence: Multi-Threaded Concurrency Testing

### Test Suite 1: Uncontrolled Concurrency vs. Optimistic & Pessimistic Concurrency Control

#### Case A: Uncontrolled Concurrency (The Double-Spend / Lost Update Anomaly)
```text
======================================================================
SIMULATION 1: UNCONTROLLED CONCURRENCY (LOST UPDATE / DOUBLE-SPEND)
======================================================================
Initial Account Balance: $1,000.00
  [Thread-1 (Debit $800)] Read balance: $1,000.00
  [Thread-2 (Debit $700)] Read balance: $1,000.00
  [Thread-2 (Debit $700)] Validation PASSED. Writing new balance: $300.00
  [Thread-2 (Debit $700)] COMMIT successful.
  [Thread-1 (Debit $800)] Validation PASSED. Writing new balance: $200.00
  [Thread-1 (Debit $800)] COMMIT successful.

Final Account Balance: $200.00
ANOMALY OBSERVED: Total debited was $1,500 from an initial $1,000 balance!
The second commit overwrote the first, resulting in severe double-spend loss.
```
**Technical Assessment:** Both threads read the same initial state concurrently. Because neither row-level locks nor version predicates were enforced, Thread 1 blindly overwrote Thread 2's commit. The bank lost \$500.00.

---

#### Case B: Concurrency Control via Optimistic Concurrency Control (OCC)
```text
======================================================================
SIMULATION 2: OPTIMISTIC CONCURRENCY CONTROL (OCC with Versioning)
======================================================================
Initial Account Balance: $1,000.00 | Version = 1
  [Thread-1 (Debit $800)] Read balance: $1,000.00, Version: 1
  [Thread-2 (Debit $700)] Read balance: $1,000.00, Version: 1
  [Thread-2 (Debit $700)] SUCCESS: Rows updated = 1. New balance: $300.00, Version: 2
  [Thread-1 (Debit $800)] CONFLICT DETECTED: Rows updated = 0 (Version mismatch!). Transaction ABORTED safely.

Final Account Balance: $300.00 | Final Version: 2
[SUCCESS] Invariant Preserved: Exactly one transaction succeeded; conflicting transaction was rejected.
```
**Technical Assessment:** By enforcing `WHERE account_id = 'acc-001-usd' AND version = 1` during the update statement, Thread 2 succeeded and bumped `version` to 2. When Thread 1 attempted to write, the rowcount returned 0. The conflict was trapped, preserving database consistency without locking overhead.

---

#### Case C: Pessimistic Atomic Predicate Protection
```text
======================================================================
SIMULATION 3: PESSIMISTIC ATOMIC PREDICATE LOCKING
======================================================================
  [Thread-2 (Debit $700)] ATOMIC DEBIT SUCCESSFUL: Deducted $700.00. Remaining: $300.00
  [Thread-1 (Debit $800)] ATOMIC DEBIT REJECTED: Overdraft constraint prevented debit of $800.00.

Final Account Balance: $300.00
[SUCCESS] Account balance never breached overdraft boundary.
```

---

## 3. Transaction Isolation Level Phenomena

```text
===========================================================================
DEMONSTRATION: TRANSACTION ISOLATION LEVELS & CONCURRENCY ANOMALIES
===========================================================================

--- PHENOMENON 1: NON-REPEATABLE READ ---
Definition: Transaction T1 reads a row, T2 modifies and commits, T1 re-reads and observes different data.
Step 1: [T1] First Read of acc-001-usd balance: $12,500.00
Step 2: [T2] Updated acc-001-usd balance to $15,000.00 and committed.
Step 3: [T1] Second Read of acc-001-usd balance: $15,000.00
  -> RESULT: Non-repeatable read observed under standard read-committed mode ($12,500 != $15,000).
  -> MITIGATION: In REPEATABLE READ / SERIALIZABLE (or MVCC snapshot), T1 reads from a point-in-time snapshot.

--- PHENOMENON 2: PHANTOM READ ---
Definition: T1 queries a predicate range, T2 inserts a matching row, T1 re-queries and sees 'phantom' rows.
Step 1: [T1] Count of VIP accounts (balance >= $50,000): 6
Step 2: [T2] Inserted new VIP account (acc-phantom-01, balance = $75,000.00) and committed.
Step 3: [T1] Count of VIP accounts after T2 insertion: 7
  -> RESULT: Phantom read observed. The predicate range expanded dynamically during concurrent insertion.
  -> MITIGATION: SERIALIZABLE isolation (predicate locking / index range locks) prevents insertions into scanned ranges.
```

---

## 4. Deadlock Detection & Global Resource Ordering

```text
===========================================================================
DEMONSTRATION: DATABASE DEADLOCK CYCLE & PREVENTION VIA RESOURCE ORDERING
===========================================================================

--- SCENARIO 2: DEADLOCK PREVENTION VIA GLOBAL RESOURCE ORDERING ---
Rule: Always acquire account locks in deterministic alphabetical order: min(id1, id2) then max(id1, id2)
This guarantees that circular wait cycles are mathematically impossible (Coffman Condition violated).
  [T1] Requested transfer: acc-001-usd -> acc-005-usd. Lock Order: acc-001-usd then acc-005-usd
  [T2] Requested transfer: acc-005-usd -> acc-001-usd. Lock Order: acc-001-usd then acc-005-usd
  [T1] Transfer completed and committed successfully!
  [T2] Transfer completed and committed successfully!

[CONCLUSION] Strict lock hierarchy completely prevented deadlock contention.
```

---

## 5. Architectural Comparison of Concurrency Control Approaches

| Concurrency Model | Read Overhead | Write Overhead | Throughput Under Contention | Best Fit in FinFlow |
| :--- | :--- | :--- | :--- | :--- |
| **Pessimistic 2PL (Two-Phase Locking)** | Shared read locks block writers | Exclusive write locks block readers & writers | High lock contention, potential deadlocks | High-risk multi-currency ledger transfers |
| **Optimistic Concurrency Control (OCC)** | Zero locks on read | Validates version number at commit | High throughput under low-to-medium contention; aborts spike under hot spots | Customer profile & account setting updates |
| **Multi-Version Concurrency Control (MVCC)** | Readers never block writers | Writers create new tuple versions; periodic vacuum required | Very high read throughput; non-blocking analytics | Analytical reporting, AML screening, and user balance queries |
