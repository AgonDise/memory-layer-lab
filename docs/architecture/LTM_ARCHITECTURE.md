# 🏗️ LTM Architecture: VectorDB + Knowledge Graph

**Dual-Database Design for Long-Term Memory**

---

## 🎯 Why Both VectorDB AND Knowledge Graph?

### VectorDB (Semantic Search)
**Purpose:** Find similar content by meaning  
**Strength:** Fuzzy matching, semantic similarity  
**Use Case:** "Find functions related to error handling"

### Knowledge Graph (Structured Relations)
**Purpose:** Store explicit relationships  
**Strength:** Precise queries, graph traversal  
**Use Case:** "Show all commits that modified this function"

### Why Both?
```
Query: "How was the divide-by-zero bug fixed?"

VectorDB:
  ✅ Finds semantically similar content
  ✅ Returns: bug reports, discussions, similar issues
  ❌ Doesn't know commit→function→file relationships

Knowledge Graph:
  ✅ Knows exact relationships: commit→fixes→bug
  ✅ Can traverse: bug→function→file→dependencies
  ❌ Can't do fuzzy "similar bugs" search

Together:
  🎯 VectorDB finds candidates
  🎯 Graph enriches with relationships
  🎯 Best of both worlds!
```

---

## 🏛️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      LONG-TERM MEMORY (LTM)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐         ┌──────────────────────────┐ │
│  │   VectorDB (FAISS)   │         │  Knowledge Graph (Neo4j) │ │
│  │                      │         │                          │ │
│  │  • Embeddings        │◄───────►│  • Entities (nodes)      │ │
│  │  • Similarity search │         │  • Relationships (edges) │ │
│  │  • Fast retrieval    │         │  • Graph queries         │ │
│  │  • Semantic meaning  │         │  • Traversal             │ │
│  └──────────────────────┘         └──────────────────────────┘ │
│           ▲                                  ▲                  │
│           │                                  │                  │
│           └──────────────┬───────────────────┘                  │
│                          │                                      │
│                   ┌──────▼──────┐                              │
│                   │  LTM Query  │                              │
│                   │  Coordinator │                              │
│                   └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Model

### VectorDB Schema

```json
{
  "id": "ltm_abc123",
  "content": "computeMetrics calculates mean, median, std",
  "embedding": [0.123, 0.456, ...],  // 384 dimensions
  "metadata": {
    "category": "function",
    "entity_id": "func_computeMetrics",  // Link to Graph
    "importance": "critical",
    "tags": ["analytics", "metrics"]
  }
}
```

**Purpose:** Fast semantic search

### Knowledge Graph Schema

```cypher
// Nodes (Entities)
(:Function {
  id: "func_computeMetrics",
  name: "computeMetrics",
  file_path: "analytics/stats.py",
  description: "Calculates statistical metrics"
})

(:Commit {
  id: "commit_abc123",
  hash: "abc123",
  message: "Fix division by zero",
  author: "John Doe",
  date: "2023-09-10"
})

(:Bug {
  id: "bug_242",
  title: "Division by zero in computeMetrics",
  severity: "critical",
  status: "fixed"
})

(:Module {
  id: "module_analytics",
  name: "Analytics",
  path: "analytics/"
})

// Relationships (Edges)
(:Commit)-[:FIXES]->(:Bug)
(:Commit)-[:MODIFIES]->(:Function)
(:Function)-[:BELONGS_TO]->(:Module)
(:Function)-[:CALLS]->(:Function)
(:Bug)-[:AFFECTS]->(:Function)
```

**Purpose:** Structured relationships, graph traversal

---

## 🔄 Complete Pipeline

### 1. Data Ingestion

```
New Code Event (Commit, Bug, Discussion)
        │
        ├──► Extract Text Content
        │         │
        │         ├──► Generate Embedding (OpenAI/Sentence-BERT)
        │         │         │
        │         │         └──► Store in VectorDB
        │         │              {id, content, embedding, metadata}
        │         │
        │         └──► Extract Entities & Relations
        │                   │
        │                   └──► Store in Knowledge Graph
        │                        CREATE (c:Commit)-[:FIXES]->(b:Bug)
        │
        └──► Link Both DBs
                metadata.entity_id = graph_node_id
```

### 2. Query Flow

```
User Query: "How was divide-by-zero fixed?"
        │
        ▼
┌───────────────────┐
│  Query Analyzer   │
│  - Extract intent │
│  - Route to DBs   │
└─────────┬─────────┘
          │
    ┌─────┴──────┐
    │            │
    ▼            ▼
┌────────┐  ┌────────────┐
│VectorDB│  │ Graph DB   │
│Search  │  │ Query      │
└───┬────┘  └─────┬──────┘
    │             │
    │  Semantic   │  Structural
    │  Results    │  Relations
    │             │
    └─────┬───────┘
          ▼
   ┌──────────────┐
   │   Combine    │
   │   Results    │
   └──────┬───────┘
          ▼
   Enriched Answer
```

### 3. Hybrid Query Example

**Query:** "Functions related to divide-by-zero bug"

**Step 1: VectorDB** (Semantic)
```python
# Find similar content
embedding = embed("divide-by-zero bug")
results = vector_db.search(embedding, top_k=5)

# Returns:
# - computeMetrics function
# - calculateAverage function  
# - Bug #242 description
# - Related discussions
```

**Step 2: Knowledge Graph** (Structural)
```cypher
// Get all related entities
MATCH (b:Bug {id: "bug_242"})
MATCH (b)<-[:FIXES]-(c:Commit)
MATCH (c)-[:MODIFIES]->(f:Function)
MATCH (f)-[:CALLS]->(dep:Function)
RETURN b, c, f, dep
```

**Step 3: Combine**
```python
# Merge results
results = {
    'semantic_matches': vector_results,      # Similar content
    'graph_relations': graph_results,        # Exact relationships
    'enriched_context': merge(vector, graph) # Combined insights
}
```

---

## 🔀 Workflow Between DBs

### Pattern 1: Vector → Graph (Expand)

```
User: "Find functions about validation"
    │
    ▼
VectorDB: Search "validation" 
    │
    └──► Returns: [func1, func2, func3]
         │
         ▼
Graph: Expand relationships
         │
         └──► MATCH (f:Function) WHERE f.id IN [...]
              MATCH (f)-[:CALLS]->(dep)
              MATCH (f)<-[:MODIFIED_BY]-(c:Commit)
              RETURN f, dep, c
```

**Use Case:** Start broad (semantic), then get precise (graph)

### Pattern 2: Graph → Vector (Enrich)

```
User: "Show commits by John Doe"
    │
    ▼
Graph: Find commits
    │
    └──► MATCH (c:Commit {author: "John Doe"})
         RETURN c
         │
         ▼
VectorDB: Get full context
         │
         └──► For each commit.id:
              SELECT * FROM vectors
              WHERE metadata.entity_id = commit.id
```

**Use Case:** Start precise (graph), then enrich (vector)

### Pattern 3: Parallel Query (Best Results)

```
User: "Explain computeMetrics bug"
    │
    ├──────────────┬──────────────┐
    ▼              ▼              ▼
VectorDB:     Graph:         LLM:
Similar       Relations      Generate
content       path           explanation
    │              │              │
    └──────┬───────┴──────────────┘
           ▼
    Combined Context → Final Answer
```

**Use Case:** Complex queries needing both approaches

---

## 💾 Updated LTM Schema

### Unified Schema (Both DBs)

```json
{
  "id": "ltm_abc123",
  "content": "Long text content for semantic search",
  "project_id": "innocody-demo",
  
  "metadata": {
    "category": "function",
    
    // VectorDB fields
    "embedding": [0.1, 0.2, ...],
    "importance": "critical",
    "tags": ["analytics", "validation"],
    
    // Knowledge Graph links
    "graph_entity_id": "func_computeMetrics",
    "graph_entity_type": "Function",
    "graph_links": [
      {
        "type": "BELONGS_TO",
        "target": "module_analytics"
      },
      {
        "type": "CALLS",
        "target": "func_calculateAverage"
      }
    ],
    
    // Common fields (both DBs)
    "file_path": "analytics/stats.py",
    "function_name": "computeMetrics",
    "git_commit": "abc123",
    "created_at": "2023-09-10",
    "last_accessed": "2023-10-01"
  }
}
```

### Knowledge Graph Entities

```cypher
// Function node
CREATE (f:Function {
  id: "func_computeMetrics",
  name: "computeMetrics",
  file_path: "analytics/stats.py",
  line_start: 42,
  line_end: 58,
  description: "Calculates mean, median, std",
  vector_id: "ltm_abc123"  // Link back to VectorDB
})

// Bug node
CREATE (b:Bug {
  id: "bug_242",
  title: "Division by zero",
  severity: "critical",
  status: "fixed",
  vector_id: "ltm_def456"
})

// Commit node
CREATE (c:Commit {
  id: "commit_abc123",
  hash: "abc123",
  message: "Fix division by zero",
  author: "John Doe",
  date: "2023-09-10",
  vector_id: "ltm_ghi789"
})

// Relationships
CREATE (c)-[:FIXES {date: "2023-09-10"}]->(b)
CREATE (c)-[:MODIFIES {lines_added: 2}]->(f)
CREATE (b)-[:AFFECTS]->(f)
```

---

## 🎯 Query Patterns

### Pattern 1: Semantic Search + Graph Expansion

```python
def hybrid_search(query: str, expand_graph: bool = True):
    # 1. Vector search
    embedding = embed(query)
    vector_results = vector_db.search(embedding, top_k=5)
    
    if not expand_graph:
        return vector_results
    
    # 2. Extract entity IDs
    entity_ids = [r['metadata']['graph_entity_id'] 
                  for r in vector_results]
    
    # 3. Graph expansion
    cypher = """
    MATCH (n) WHERE n.id IN $ids
    OPTIONAL MATCH (n)-[r]-(m)
    RETURN n, r, m
    LIMIT 50
    """
    graph_results = neo4j.execute(cypher, ids=entity_ids)
    
    # 4. Combine
    return {
        'semantic': vector_results,
        'graph': graph_results
    }
```

### Pattern 2: Graph Query + Vector Enrichment

```python
def graph_with_context(entity_id: str):
    # 1. Graph query
    cypher = """
    MATCH (n {id: $id})-[r]-(m)
    RETURN n, r, m
    """
    graph_results = neo4j.execute(cypher, id=entity_id)
    
    # 2. Get vector content for each node
    enriched = []
    for node in graph_results:
        vector_id = node['vector_id']
        content = vector_db.get_by_id(vector_id)
        enriched.append({
            'node': node,
            'content': content['content'],
            'embedding': content['embedding']
        })
    
    return enriched
```

### Pattern 3: Bidirectional Sync

```python
def add_to_ltm(content: str, metadata: dict):
    # 1. Generate embedding
    embedding = embed(content)
    
    # 2. Create graph entity
    entity_id = create_graph_entity(metadata)
    
    # 3. Add to VectorDB with graph link
    vector_id = vector_db.add({
        'content': content,
        'embedding': embedding,
        'metadata': {
            **metadata,
            'graph_entity_id': entity_id
        }
    })
    
    # 4. Update graph with vector link
    neo4j.execute("""
        MATCH (n {id: $id})
        SET n.vector_id = $vector_id
    """, id=entity_id, vector_id=vector_id)
    
    return {
        'vector_id': vector_id,
        'graph_entity_id': entity_id
    }
```

---

## 🔄 Data Flow Examples

### Example 1: New Commit Added

```
1. Commit Event
   {
     hash: "abc123",
     message: "Fix division by zero",
     files: ["analytics/stats.py"],
     author: "John Doe"
   }
        ↓
2. Process Content
   - Extract: commit message + diff
   - Generate embedding
        ↓
3. Store in VectorDB
   {
     id: "ltm_commit_abc123",
     content: "Fix division by zero in computeMetrics...",
     embedding: [...],
     metadata: {
       category: "commit_log",
       graph_entity_id: "commit_abc123"
     }
   }
        ↓
4. Store in Graph
   CREATE (c:Commit {
     id: "commit_abc123",
     hash: "abc123",
     vector_id: "ltm_commit_abc123"
   })
   CREATE (c)-[:MODIFIES]->(f:Function)
   CREATE (c)-[:FIXES]->(b:Bug)
        ↓
5. Both DBs Synced ✅
```

### Example 2: Query Execution

```
Query: "How was the analytics bug fixed?"
        ↓
1. Analyze Query
   - Intent: Find fix for bug
   - Domain: analytics
   - Type: explanation
        ↓
2. VectorDB Search
   embedding = embed(query)
   results = search(embedding)
   
   Returns:
   - Bug #242 description
   - Commit abc123 message
   - Related functions
        ↓
3. Graph Query
   MATCH (b:Bug)-[:FIXED_BY]->(c:Commit)
   WHERE b.id IN [found_bugs]
   MATCH (c)-[:MODIFIES]->(f:Function)
   RETURN b, c, f
        ↓
4. Combine Results
   {
     bug: "Division by zero in computeMetrics",
     fix: {
       commit: "abc123",
       author: "John Doe",
       date: "2023-09-10",
       changes: "Added count != 0 check"
     },
     affected_functions: ["computeMetrics"],
     similar_bugs: [...],  // From vector
     related_commits: [...] // From graph
   }
        ↓
5. Generate Response
   "The analytics bug (Division by zero) was fixed in 
    commit abc123 by John Doe on 2023-09-10. The fix 
    involved adding a validation check in the 
    computeMetrics function..."
```

---

## 🎯 Use Cases

### Use Case 1: Code Documentation

**VectorDB:** Find similar functions  
**Graph:** Show call hierarchy

```python
# Find similar functions
similar = vector_db.search("function that calculates average")

# Get call graph
for func in similar:
    callers = graph.query("""
        MATCH (f:Function {id: $id})<-[:CALLS]-(caller)
        RETURN caller
    """, id=func.graph_entity_id)
```

### Use Case 2: Bug Analysis

**VectorDB:** Find similar bugs  
**Graph:** Trace bug → fix → affected code

```python
# Similar bugs
similar_bugs = vector_db.search("null pointer exception")

# Trace relationships
for bug in similar_bugs:
    trace = graph.query("""
        MATCH (b:Bug {id: $id})
        MATCH (b)<-[:FIXES]-(c:Commit)
        MATCH (c)-[:MODIFIES]->(f:Function)
        RETURN b, c, f
    """, id=bug.graph_entity_id)
```

### Use Case 3: Impact Analysis

**Graph:** Find dependencies (precise)  
**VectorDB:** Find semantic similarities (fuzzy)

```python
# Direct dependencies (graph)
deps = graph.query("""
    MATCH (f:Function {name: "computeMetrics"})
    MATCH (f)-[:CALLS*1..3]->(dep)
    RETURN dep
""")

# Semantic dependencies (vector)
similar = vector_db.search("functions using statistics")
```

---

## 🚀 Implementation Checklist

### Phase 1: Setup
- [ ] Install VectorDB (FAISS/ChromaDB)
- [ ] Install Neo4j
- [ ] Setup connection managers
- [ ] Create schemas in both DBs

### Phase 2: Data Pipeline
- [ ] Implement embedding generator
- [ ] Create VectorDB interface
- [ ] Create Graph interface
- [ ] Build sync mechanism

### Phase 3: Query Layer
- [ ] Implement hybrid search
- [ ] Build query coordinator
- [ ] Add result combiner
- [ ] Create API endpoints

### Phase 4: Integration
- [ ] Connect to STM/MTM
- [ ] Add to main orchestrator
- [ ] Test end-to-end
- [ ] Performance tuning

---

## 📊 Performance Considerations

### VectorDB
- **Speed:** Very fast (milliseconds)
- **Scalability:** Millions of vectors
- **Best for:** Initial retrieval

### Knowledge Graph
- **Speed:** Fast for simple queries
- **Scalability:** Millions of nodes/edges
- **Best for:** Complex traversals

### Hybrid Approach
- **Query VectorDB first** (fast filter)
- **Expand with Graph** (enrich results)
- **Cache common queries**
- **Use async for parallel queries**

---

**Summary:**
- **VectorDB** = Fuzzy search by meaning
- **Graph** = Precise relationships
- **Together** = Powerful LTM! 🚀
