# Portfolio 1: Database Design and Modelling

**Course:** MIT 8103 Advanced Database Systems  
**Case Study:** FinFlow Global Systems (Fintech / Cross-Border Digital Banking)  
**Deliverables Covered:**
1. Chosen case study description & system requirements
2. Entity-Relationship (ER) diagram (`schema_diagram.png` & Mermaid models)
3. Relational schema (DDL scripts with primary keys, foreign keys, CHECK & UNIQUE constraints)
4. Comprehensive normalization analysis (1NF, 2NF, 3NF, BCNF) and anomaly prevention
5. Seed dataset and verification scripts

---

## Directory Contents

- **`01_schema_ddl.sql`**: Production-ready ANSI-compliant SQL DDL creating 8 normalized relations with complete constraints (`CHECK`, `DEFAULT`, `UNIQUE`, `FOREIGN KEY ON DELETE RESTRICT/CASCADE`).
- **`02_seed_data.sql`**: Comprehensive seed dataset featuring multi-currency holdings, FX rate matrices, customer profiles, merchant accounts, transaction histories, double-entry ledger postings, and AML alert tickets.
- **`schema_diagram.png`**: High-resolution rendered graphical Entity-Relationship Diagram illustrating all tables, data types, primary/foreign keys, and cardinalities.
- **`normalization_report.md`**: Academic decomposition analysis walking through 1NF, 2NF, 3NF, and BCNF validation, functional dependencies, and operational anomaly protections.
- **`verify_portfolio_1.py`**: Automated verification test suite validating table creation, constraints, and row assertions.

---

## How to Execute & Verify

Run the Python verification test:
```bash
python verify_portfolio_1.py
```

To regenerate the high-resolution ERD graphic:
```bash
python generate_erd.py
```
