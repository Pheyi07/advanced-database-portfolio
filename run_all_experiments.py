#!/usr/bin/env python3
"""
MIT 8103 Advanced Database Systems - Master Execution Harness
Runs all 5 portfolio experiments end-to-end, validating database schemas,
query optimizations, ACID transaction harnesses, NoSQL models, and distributed simulations.
"""

import subprocess
import sys
import os
import time

def run_step(step_name, command_args):
    print("\n" + "="*80)
    print(f"RUNNING: {step_name}")
    print("="*80)
    t0 = time.time()
    res = subprocess.run(command_args, capture_output=True, text=True)
    t1 = time.time()
    
    if res.stdout:
        print(res.stdout.strip())
    if res.returncode != 0:
        print(f"[ERROR] {step_name} failed with exit code {res.returncode}")
        if res.stderr:
            print(res.stderr.strip())
        return False
    print(f"\n[PASS] {step_name} completed successfully in {t1 - t0:.2f} seconds.")
    return True

def main():
    print("""
    ========================================================================
     MIVA OPEN UNIVERSITY - SCHOOL OF POSTGRADUATE STUDIES
     MIT 8103: Advanced Database Systems (Continuous Assessment Portfolio)
     Case Study: FinFlow Global Payment Systems (40 Marks)
     Master Execution Harness
    ========================================================================
    """)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    steps = [
        ("Portfolio 1: Relational Schema DDL & Seed Data Verification", 
         [sys.executable, os.path.join(base_dir, "portfolio-1-database-design", "verify_portfolio_1.py")]),
        
        ("Portfolio 1: ER Diagram Graphic Generation", 
         [sys.executable, os.path.join(base_dir, "portfolio-1-database-design", "generate_erd.py")]),
        
        ("Portfolio 2: Query Workload & Indexing Optimization Benchmark", 
         [sys.executable, os.path.join(base_dir, "portfolio-2-query-optimisation", "03_benchmark_runner.py")]),
        
        ("Portfolio 3: ACID Transactions & Concurrency Race Condition Harness", 
         [sys.executable, os.path.join(base_dir, "portfolio-3-transactions-concurrency", "02_concurrency_race_condition.py")]),
        
        ("Portfolio 3: ANSI SQL Isolation Levels & Anomalies", 
         [sys.executable, os.path.join(base_dir, "portfolio-3-transactions-concurrency", "03_isolation_levels_demo.py")]),
        
        ("Portfolio 3: Deadlock Detection & Deterministic Lock Ordering", 
         [sys.executable, os.path.join(base_dir, "portfolio-3-transactions-concurrency", "04_deadlock_and_locking.py")]),
        
        ("Portfolio 4: NoSQL Document Store & Key-Value TTL Caching", 
         [sys.executable, os.path.join(base_dir, "portfolio-4-nosql", "finflow_nosql.py")]),
        
        ("Portfolio 4: NoSQL JSON Aggregations & Schema Mutation Queries", 
         [sys.executable, os.path.join(base_dir, "portfolio-4-nosql", "03_nosql_queries_and_aggregations.py")]),
        
        ("Portfolio 4: Graph Database Model — Fraud Ring Detection", 
         [sys.executable, os.path.join(base_dir, "portfolio-4-nosql", "04_graph_model_demo.py")]),
        
        ("Portfolio 4: Column-Family (Wide-Column) Time-Series Events", 
         [sys.executable, os.path.join(base_dir, "portfolio-4-nosql", "05_column_family_demo.py")]),
        
        ("Portfolio 5: Distributed Sharding & Cross-Shard 2PC Consensus", 
         [sys.executable, os.path.join(base_dir, "portfolio-5-distributed-cloud", "01_sharding_simulation.py")]),
        
        ("Portfolio 5: Primary-Replica Log Streaming & Disaster Failover", 
         [sys.executable, os.path.join(base_dir, "portfolio-5-distributed-cloud", "02_replication_failover_simulation.py")]),
        
        ("Portfolio 5: Multi-Region Cloud Architecture Diagram Generation", 
         [sys.executable, os.path.join(base_dir, "portfolio-5-distributed-cloud", "generate_architecture_diagram.py")])
    ]

    passed = 0
    total = len(steps)

    for name, cmd in steps:
        if run_step(name, cmd):
            passed += 1
        else:
            print(f"[FATAL] Aborting execution due to failure in {name}")
            sys.exit(1)

    print("\n" + "#"*80)
    print(f" ALL {passed}/{total} PORTFOLIO EXPERIMENTS EXECUTED AND VERIFIED CLEANLY!")
    print("#"*80)

if __name__ == "__main__":
    main()
