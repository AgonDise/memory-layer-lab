# Schema Changelog

## 2025-10-01: Hybrid LTM Schema Update

### Summary

Updated Long-Term Memory (LTM) schema to support hybrid architecture combining VectorDB and Knowledge Graph.

### Files Modified

1. **`utils/schema/ltm.json`** - JSON Schema definition
2. **`schema.yaml`** - Example data with documentation
3. **`utils/schema/HYBRID_LTM_SCHEMA.md`** (new) - Comprehensive documentation

### Changes to `ltm.json`

#### Added Fields

1. **`metadata.graph_entity_id`** (string)
   - Links VectorDB entry to Knowledge Graph node
   - Bidirectional reference for hybrid queries
   
2. **`metadata.line_start`** (integer)
   - Starting line number for code entities
   
3. **`metadata.line_end`** (integer)
   - Ending line number for code entities
   
4. **`metadata.tags`** (string array)
   - Flexible tagging system for categorization
   
5. **`metadata.graph_links[].properties`** (object)
   - Optional properties for graph relationships
   
6. **`metadata.vector_db_metadata`** (object)
   - VectorDB-specific configuration
   - Fields: `index_name`, `distance_metric`
   
7. **`metadata.graph_db_metadata`** (object)
   - Knowledge Graph-specific configuration
   - Fields: `node_label`, `additional_labels`, `indexed_properties`

#### Enhanced Descriptions

- Added comprehensive descriptions to all fields
- Documented bidirectional linking mechanism
- Specified supported relationship types
- Added dimensionality notes for embeddings (384 or 768)

#### Schema Validation

- Added `additionalProperties: false` for stricter validation
- Maintained backward compatibility with existing data
- All new fields are optional

### Changes to `schema.yaml`

#### Restructured LTM Section

**Before:**
- Simple flat structure
- Separate graph and vector examples
- Limited documentation

**After:**
- Clear hybrid architecture explanation
- Bidirectional links demonstrated with arrows
- Query strategy overview
- Real-world examples with full metadata
- Comprehensive inline documentation
- Visual hybrid query flow examples

#### Added Sections

1. **Hybrid Architecture Overview**
   - Design philosophy
   - Query strategies (5 types)
   
2. **Knowledge Graph Component**
   - Node examples with `vector_id`
   - Edge examples with properties
   - Relationship types documented
   
3. **Vector Database Component**
   - Full entry examples with `graph_entity_id`
   - Complete metadata structure
   - Demonstrates `graph_links` usage
   
4. **Hybrid Query Examples**
   - Vector First strategy walkthrough
   - Graph First strategy walkthrough
   - Parallel strategy walkthrough

### Backward Compatibility

✅ **Fully backward compatible**

- Existing LTM entries continue to work
- New fields are optional
- Hybrid features can be adopted gradually
- No breaking changes to required fields

### Migration Path

#### Phase 1: Schema Update (Complete)
- ✅ Update JSON schema definition
- ✅ Update YAML examples
- ✅ Create documentation

#### Phase 2: Optional - Enable Hybrid Mode
- Set up Neo4j Knowledge Graph database
- Add `graph_entity_id` to new entries
- Use `HybridLTM` class for ingestion
- Configure `graph_links` for relationships

#### Phase 3: Optional - Backfill Existing Data
- Add `graph_entity_id` to existing entries
- Create corresponding graph nodes
- Establish relationships from historical data

### Usage Examples

#### Old Way (Still Works)
```python
ltm_entry = {
    "id": "ltm_001",
    "content": "Function description",
    "project_id": "demo",
    "metadata": {
        "category": "function",
        "embedding": [0.1, 0.2, ...]
    }
}
```

#### New Way (Hybrid)
```python
from ltm.hybrid_ltm import HybridLTM

ltm = HybridLTM(vector_db=vec_db, graph_db=neo4j)

result = ltm.add(
    content="Function description",
    metadata={
        'category': 'function',
        'function_name': 'computeMetrics',
        'graph_links': [
            {'type': 'BELONGS_TO', 'target': 'module_analytics'}
        ]
    }
)
# Returns: {'vector_id': '...', 'graph_entity_id': '...'}
```

### Benefits of Hybrid Schema

1. **Semantic + Structural Search**
   - Find similar content (VectorDB)
   - Traverse relationships (Graph)

2. **Rich Context**
   - Full content in vectors
   - Relationships in graph

3. **Flexible Queries**
   - 5 different query strategies
   - Choose based on use case

4. **Better Insights**
   - Impact analysis via graph traversal
   - Similar code via semantic search
   - Combined: "Show similar functions and their callers"

### Performance Notes

- Hybrid queries are slightly slower than single-DB queries
- Use appropriate strategy for use case:
  - **Vector Only**: Fastest semantic search
  - **Graph Only**: Fastest structural query
  - **Vector First**: Good balance for broad queries
  - **Graph First**: Good balance for precise queries
  - **Parallel**: Most comprehensive for complex queries

### Related Documentation

- [`HYBRID_LTM_SCHEMA.md`](./HYBRID_LTM_SCHEMA.md) - Detailed schema documentation
- [`../../docs/LTM_WORKFLOW.md`](../../docs/LTM_WORKFLOW.md) - Visual workflows
- [`../../ltm/hybrid_ltm.py`](../../ltm/hybrid_ltm.py) - Implementation
- [`../../examples/hybrid_ltm_demo.py`](../../examples/hybrid_ltm_demo.py) - Examples

### Testing

To validate the schema:

```bash
# Test JSON schema validation
python -c "import json; print(json.load(open('utils/schema/ltm.json')))"

# Test YAML syntax
python -c "import yaml; print(yaml.safe_load(open('schema.yaml')))"

# Run hybrid LTM demo
python examples/hybrid_ltm_demo.py
```

### Questions?

See [`HYBRID_LTM_SCHEMA.md`](./HYBRID_LTM_SCHEMA.md) for comprehensive documentation.
