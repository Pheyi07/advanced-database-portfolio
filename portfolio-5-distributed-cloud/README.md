# Portfolio 5: Distributed and Cloud Database Exercise

**Student:** Olopha Oluwafeyikemi (Student ID: 301930634)  
**Course:** MIT 8103 Advanced Database Systems  
**Case Study:** FinFlow Global Systems  
**Deliverables Covered:**
1. Horizontal hash-partitioned database sharding simulation (`01_sharding_simulation.py`)
2. Distributed cross-shard Two-Phase Commit (2PC) coordinator implementation
3. Primary-replica log streaming and automated disaster failover harness (`02_replication_failover_simulation.py`)
4. CAP & PACELC theorem trade-off analysis for fintech systems
5. Multi-region cloud topology diagram (`architecture_diagram.png`) and comprehensive engineering documentation (`distributed_architecture_design.md`)

---

## Directory Contents

- **`01_sharding_simulation.py`**: Python implementation of a distributed shard router routing customer records across independent physical SQLite shard nodes using MD5 hash modulo algorithms, orchestrating two-phase commit (2PC) transactions across shard boundaries.
- **`02_replication_failover_simulation.py`**: Multi-node replication cluster simulating WAL log streaming with Log Sequence Numbers (LSN), read query offloading, simulated primary crash, heartbeat failure detection, and automated leader promotion.
- **`generate_architecture_diagram.py`**: Python script generating the publication-grade multi-region cloud deployment topology.
- **`architecture_diagram.png`**: High-resolution architectural blueprint depicting Global DNS, Regional Shard Routers, Aurora Primary clusters, cross-region replication links, and in-memory Redis clusters.
- **`distributed_architecture_design.md`**: Exhaustive academic document analyzing sharding keys, cross-shard consensus, replication topologies, and CAP/PACELC formal proofs.

---

## How to Run

```bash
# Run horizontal sharding and 2PC simulation
python 01_sharding_simulation.py

# Run replication log streaming and automated failover simulation
python 02_replication_failover_simulation.py

# Regenerate cloud architecture diagram
python generate_architecture_diagram.py
```
