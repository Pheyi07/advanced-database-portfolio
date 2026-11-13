# Portfolio 4: NoSQL and Advanced Data Models

**Course:** MIT 8103 Advanced Database Systems  
**Case Study:** FinFlow Global Systems  
**Deliverables Covered:**
1. NoSQL data model designed for the same case study — all four NoSQL paradigms: **Document, Key-Value, Column-Family, and Graph**
2. Production JSON sample documents featuring polymorphic payment webhooks, device telemetry, and fraud risk feature vectors (`02_sample_documents.json`)
3. Executable Document Store implementation with functional B-tree JSON path indexes (`01_nosql_document_store.py` / `finflow_nosql.py`)
4. Document query and aggregation pipeline demonstration (`03_nosql_queries_and_aggregations.py`)
5. Graph database model for fraud ring detection with adjacency-based traversals (`04_graph_model_demo.py`)
6. Wide-column (column-family) model for time-series event logging (`05_column_family_demo.py`)
7. In-depth technical report on NoSQL suitability and Polyglot Persistence (`nosql_suitability_report.md`)

---

## Directory Contents

- **`finflow_nosql.py`**: Python implementation of a document store engine featuring collection management, nested JSON schema validation, functional B-tree indexing on JSON keys, and key-value TTL caching.
- **`02_sample_documents.json`**: Rich enterprise JSON documents showcasing heterogeneous payment methods (Card, Virtual Account, Open Banking), biometric device telemetry, and nested audit trails.
- **`03_nosql_queries_and_aggregations.py`**: Query suite executing nested field predicate filtering, multi-platform aggregation pipelines, polymorphic grouping, array element inspection, and schema-free in-place document mutations.
- **`nosql_suitability_report.md`**: Exhaustive comparative evaluation contrasting Relational, Document, Key-Value, and Graph models, detailing FinFlow's Polyglot Persistence strategy and CAP/BASE implications.

---

## How to Run

```bash
# Initialize and seed the document collection
python finflow_nosql.py

# Run document query workflows and aggregation pipelines
python 03_nosql_queries_and_aggregations.py

# Run graph database fraud ring detection
python 04_graph_model_demo.py

# Run column-family (wide-column) time-series event model
python 05_column_family_demo.py
```
