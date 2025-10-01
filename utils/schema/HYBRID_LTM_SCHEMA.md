# Hybrid LTM Schema Documentation

## Overview

The Long-Term Memory (LTM) has been upgraded to a **hybrid architecture** combining:
- **VectorDB** (FAISS/ChromaDB) - For semantic search via embeddings
- **Knowledge Graph** (Neo4j) - For structural relationships and precise queries

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID LTM LAYER                         │
├───────────────────────────┬─────────────────────────────────┤
│      VECTORDB             │     KNOWLEDGE GRAPH             │
│   (Semantic Search)       │   (Structural Queries)          │
├───────────────────────────┼─────────────────────────────────┤
│ • Full text content       │ • Nodes (entities)              │
│ • Vector embeddings       │ • Relationships (edges)         │
│ • Fuzzy/semantic search   │ • Precise graph traversal       │
│ • Similarity scoring      │ • Path finding                  │
│                           │                                 │
│ Fields:                   │ Fields:                         │
│ - id (vector_id)          │ - id (graph_entity_id)          │
│ - content                 │ - label (type)                  │
│ - embedding               │ - properties                    │
│ - metadata                │ - vector_id (→ link)            │
│   - graph_entity_id (→)   │                                 │
└───────────────────────────┴─────────────────────────────────┘
         ↕                              ↕
    Bidirectional links maintain data consistency
```

## Key Schema Changes

### 1. **New Field: `graph_entity_id`**

Added to VectorDB metadata to link to Knowledge Graph node:

```json
{
  "id": "vec_001",
  "content": "Function content...",
  "metadata": {
    "graph_entity_id": "func_computeMetrics",  // ← NEW: Link to graph
    "category": "function",
    ...
  }
}
```

### 2. **New Field: `vector_id`**

Added to Knowledge Graph nodes to link back to VectorDB:

```cypher
CREATE (f:Function {
  id: 'func_computeMetrics',
  name: 'computeMetrics',
  vector_id: 'vec_001'  // ← NEW: Link to vector
})
```

### 3. **Enhanced `graph_links`**

Now supports relationship properties:

```json
{
  "graph_links": [
    {
      "type": "MODIFIES",
      "target": "func_computeMetrics",
      "properties": {           // ← NEW: Optional properties
        "lines_changed": 5,
        "change_type": "bugfix"
      }
    }
  ]
}
```

### 4. **New Metadata Sections**

**For VectorDB-specific settings:**
```json
{
  "vector_db_metadata": {
    "index_name": "ltm_functions",
    "distance_metric": "cosine"
  }
}
```

**For Graph-specific settings:**
```json
{
  "graph_db_metadata": {
    "node_label": "Function",
    "additional_labels": ["Code", "Analyzable"],
    "indexed_properties": ["name", "file_path"]
  }
}
```

### 5. **Added `line_start` and `line_end`**

For precise code location tracking:

```json
{
  "metadata": {
    "line_start": 42,
    "line_end": 58,
    ...
  }
}
```

### 6. **Added `tags` Array**

For flexible categorization:

```json
{
  "metadata": {
    "tags": ["analytics", "statistics", "core"],
    ...
  }
}
```

## Data Flow

### Adding Data to Hybrid LTM

```python
from ltm.hybrid_ltm import HybridLTM

ltm = HybridLTM(vector_db=vec_db, graph_db=neo4j)

result = ltm.add(
    content="computeMetrics(data): Calculates statistics...",
    metadata={
        'category': 'function',
        'function_name': 'computeMetrics',
        'file_path': 'analytics/stats.py',
        'graph_links': [
            {'type': 'BELONGS_TO', 'target': 'module_analytics'},
            {'type': 'CALLS', 'target': 'func_calculateAverage'}
        ]
    }
)

# Returns:
# {
#   'vector_id': 'vec_abc123',
#   'graph_entity_id': 'func_computeMetrics'
# }
```

**What happens internally:**

1. Generate embedding from content
2. Create node in Knowledge Graph → get `graph_entity_id`
3. Add to VectorDB with `graph_entity_id` in metadata → get `vector_id`
4. Update graph node with `vector_id` (bidirectional link)
5. Create relationships in graph based on `graph_links`

## Query Strategies

### 1. Vector First (Semantic → Structural)

**Use case:** Broad semantic search, then get precise relationships

```python
result = ltm.query(
    query="functions related to error handling",
    strategy=QueryStrategy.VECTOR_FIRST,
    top_k=5,
    expand_graph=True
)
```

**Flow:**
1. VectorDB semantic search → finds similar content
2. Extract `graph_entity_id` from results
3. Graph traversal → expand relationships
4. Return: semantic matches + structural context

### 2. Graph First (Structural → Semantic)

**Use case:** Precise structural query, then enrich with full content

```python
result = ltm.query(
    query="commits by John Doe",
    strategy=QueryStrategy.GRAPH_FIRST,
    top_k=10
)
```

**Flow:**
1. Graph query → find nodes by property
2. Extract `vector_id` from nodes
3. VectorDB fetch → get full content
4. Return: precise matches + rich content

### 3. Parallel (Best of Both)

**Use case:** Complex queries needing both approaches

```python
result = ltm.query(
    query="how was the analytics bug fixed",
    strategy=QueryStrategy.PARALLEL,
    top_k=5
)
```

**Flow:**
1. VectorDB + Graph query in parallel
2. Merge results by matching IDs
3. Return: comprehensive results

### 4. Vector Only

Pure semantic search without graph expansion.

### 5. Graph Only

Pure structural query without vector content.

## Relationship Types

Common relationship types in the Knowledge Graph:

| Type | Description | Example |
|------|-------------|---------|
| `CALLS` | Function calls another function | `main() -[CALLS]-> computeMetrics()` |
| `CALLED_BY` | Inverse of CALLS | `computeMetrics() -[CALLED_BY]-> main()` |
| `MODIFIES` | Commit modifies code entity | `commit_abc123 -[MODIFIES]-> func_login()` |
| `BELONGS_TO` | Entity belongs to module/class | `func_login() -[BELONGS_TO]-> module_auth` |
| `FIXES` | Commit fixes a bug | `commit_abc123 -[FIXES]-> bug_242` |
| `AFFECTS` | Bug affects a function | `bug_242 -[AFFECTS]-> func_login()` |
| `HAS_METHOD` | Class has method | `UserManager -[HAS_METHOD]-> login()` |
| `DEPENDS_ON` | Module dependency | `module_A -[DEPENDS_ON]-> module_B` |

## Node Labels (Categories)

| Label | Description | VectorDB Category |
|-------|-------------|-------------------|
| `Function` | Functions/methods | `function` |
| `Class` | Classes | `module` |
| `Module` | Modules/packages | `module` |
| `Commit` | Git commits | `commit_log` |
| `Bug` | Bug reports | `guideline` |
| `Doc` | Documentation | `architecture` or `guideline` |

## Migration Notes

### Backward Compatibility

The schema is **backward compatible**. Existing LTM entries without `graph_entity_id` will:
- Continue to work in VectorDB-only mode
- Can be gradually migrated to hybrid mode

### Required Changes for Hybrid Mode

1. **Add `graph_entity_id` to existing entries** (optional but recommended)
2. **Set up Knowledge Graph database** (Neo4j)
3. **Update ingestion pipeline** to use `HybridLTM.add()`

### Optional Enhancements

- Add `tags` for better categorization
- Add `line_start`/`line_end` for code entries
- Add `graph_links` to establish relationships
- Configure `vector_db_metadata` and `graph_db_metadata`

## Performance Characteristics

| Strategy | Speed | Precision | Recall | Best For |
|----------|-------|-----------|--------|----------|
| Vector First | ⚡⚡ Fast | 🎯 Medium | 📊 High | Broad semantic queries |
| Graph First | ⚡⚡⚡ Fastest | 🎯🎯🎯 High | 📊 Medium | Precise structural queries |
| Parallel | ⚡ Slower | 🎯🎯 High | 📊📊 High | Complex queries |
| Vector Only | ⚡⚡⚡ Fastest | 🎯 Low | 📊📊📊 Highest | Fuzzy semantic search |
| Graph Only | ⚡⚡ Fast | 🎯🎯🎯 Highest | 📊 Low | Exact structural match |

## Examples

### Complete LTM Entry (Hybrid)

```json
{
  "id": "ltm_abc123",
  "content": "computeMetrics(data): Calculates mean, median, std. Raises ValueError on empty input.",
  "project_id": "innocody-demo",
  "metadata": {
    "category": "function",
    "embedding": [0.12, 0.88, ...],
    "graph_entity_id": "func_computeMetrics",
    "function_name": "computeMetrics",
    "file_path": "analytics/stats.py",
    "module": "Analytics",
    "line_start": 42,
    "line_end": 58,
    "tags": ["analytics", "statistics", "core"],
    "importance": "high",
    "created_at": "2025-08-02T14:09:20Z",
    "last_accessed": "2025-10-01T14:09:20Z",
    "graph_links": [
      {
        "type": "BELONGS_TO",
        "target": "module_analytics"
      },
      {
        "type": "CALLS",
        "target": "func_calculateAverage"
      },
      {
        "type": "CALLS",
        "target": "func_calculateStdDev"
      }
    ]
  }
}
```

### Corresponding Graph Node

```cypher
CREATE (f:Function {
  id: 'func_computeMetrics',
  name: 'computeMetrics',
  file_path: 'analytics/stats.py',
  vector_id: 'ltm_abc123',
  description: 'Calculates mean, median, std...'
})
```

## See Also

- [LTM_WORKFLOW.md](../../docs/LTM_WORKFLOW.md) - Visual workflows for hybrid queries
- [hybrid_ltm.py](../../ltm/hybrid_ltm.py) - Implementation
- [hybrid_ltm_demo.py](../../examples/hybrid_ltm_demo.py) - Usage examples
