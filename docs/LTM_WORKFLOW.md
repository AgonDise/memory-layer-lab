# 🔄 LTM Workflow: VectorDB ↔ Knowledge Graph

Visual workflows cho từng use case.

---

## 📥 Workflow 1: Data Ingestion (Add to LTM)

```
┌─────────────────────────────────────────────────────────────────┐
│                     NEW CODE EVENT                               │
│  (Commit, Bug Report, Function, Discussion)                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │    Extract Information        │
            │  • Text content               │
            │  • Metadata (author, date...) │
            │  • Entities (function, file)  │
            │  • Relationships              │
            └──────────────┬────────────────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
    ┌────────────────────┐  ┌───────────────────┐
    │  Generate Embedding│  │  Extract Entities │
    │  (OpenAI/S-BERT)   │  │  & Relations      │
    └─────────┬──────────┘  └─────────┬─────────┘
              │                       │
              ▼                       ▼
    ┌────────────────────┐  ┌───────────────────┐
    │   VECTORDB         │  │  KNOWLEDGE GRAPH  │
    │                    │  │                   │
    │  Store:            │  │  Create:          │
    │  • Content         │  │  • Nodes          │
    │  • Embedding       │  │  • Relationships  │
    │  • Metadata        │  │  • Properties     │
    │  • graph_entity_id │◄─┤  • vector_id      │
    └────────────────────┘  └───────────────────┘
              │                       │
              └───────────┬───────────┘
                          ▼
                   ┌──────────────┐
                   │  Both Synced │
                   │      ✅       │
                   └──────────────┘
```

### Code Example:

```python
from ltm.hybrid_ltm import HybridLTM

ltm = HybridLTM(vector_db=vec_db, graph_db=neo4j)

# Add new commit
result = ltm.add(
    content="Fixed division by zero in computeMetrics",
    metadata={
        'category': 'commit_log',
        'git_commit': 'abc123',
        'author': 'John Doe',
        'file_path': 'analytics/stats.py',
        'graph_links': [
            {'type': 'FIXES', 'target': 'bug_242'},
            {'type': 'MODIFIES', 'target': 'func_computeMetrics'}
        ]
    }
)

# Returns:
# {
#   'vector_id': 'vec_abc123',
#   'graph_entity_id': 'commit_abc123'
# }
```

---

## 🔍 Workflow 2: Vector-First Query (Semantic → Structural)

**Use Case:** "Find functions related to error handling"

```
┌──────────────────────────────────────┐
│  USER QUERY                          │
│  "Functions related to error handling"│
└────────────────┬─────────────────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │  1. Generate Embedding │
     │     (query → vector)   │
     └───────────┬────────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │  2. VECTORDB Search    │
     │     Semantic similarity │
     └───────────┬────────────┘
                 │
                 ▼
     ┌────────────────────────┐
     │  Results (Top 5):      │
     │  • handleError()       │
     │  • validateInput()     │
     │  • tryExecute()        │
     │  + graph_entity_ids    │
     └──────────┬─────────────┘
                │
                ▼
     ┌───────────────────────────┐
     │  3. Extract Entity IDs     │
     │     [func_123, func_456...] │
     └──────────┬────────────────┘
                │
                ▼
     ┌──────────────────────────────┐
     │  4. GRAPH Expansion          │
     │     MATCH (f:Function)       │
     │     WHERE f.id IN [ids]      │
     │     MATCH (f)-[r]-(related)  │
     │     RETURN f, r, related     │
     └──────────┬───────────────────┘
                │
                ▼
     ┌────────────────────────────────┐
     │  Graph Results:                │
     │  • Functions                   │
     │  • → Called by (callers)       │
     │  • → Calls (dependencies)      │
     │  • → Modified by (commits)     │
     │  • → Belongs to (modules)      │
     └──────────┬─────────────────────┘
                │
                ▼
     ┌────────────────────────────┐
     │  5. Combine Results        │
     │  • Semantic matches        │
     │  • + Structural context    │
     │  • = Rich answer           │
     └────────────┬───────────────┘
                  │
                  ▼
        ┌──────────────────────┐
        │  Return to User:     │
        │  • 5 functions       │
        │  • Call graphs       │
        │  • Related commits   │
        │  • Module context    │
        └──────────────────────┘
```

### Code Example:

```python
from ltm.hybrid_ltm import HybridLTM, QueryStrategy

ltm = HybridLTM(vector_db, graph_db)

# Vector-first query
result = ltm.query(
    query="functions related to error handling",
    strategy=QueryStrategy.VECTOR_FIRST,
    top_k=5,
    expand_graph=True
)

# Result structure:
# {
#   'semantic_matches': [
#     {'content': 'handleError()...', 'score': 0.92},
#     {'content': 'validateInput()...', 'score': 0.87},
#     ...
#   ],
#   'graph_relations': [
#     {'function': 'handleError', 'called_by': ['main', 'process']},
#     {'function': 'validateInput', 'calls': ['checkType', 'checkRange']},
#     ...
#   ]
# }
```

---

## 🔍 Workflow 3: Graph-First Query (Structural → Semantic)

**Use Case:** "Show all commits by John Doe"

```
┌──────────────────────────────┐
│  USER QUERY                  │
│  "Commits by John Doe"       │
└────────────┬─────────────────┘
             │
             ▼
  ┌──────────────────────────┐
  │  1. Parse Query          │
  │     Type: Graph query    │
  │     Entity: Author       │
  └──────────┬───────────────┘
             │
             ▼
  ┌──────────────────────────────┐
  │  2. GRAPH Query              │
  │     MATCH (c:Commit)         │
  │     WHERE c.author = "John..." │
  │     RETURN c                 │
  └──────────┬───────────────────┘
             │
             ▼
  ┌───────────────────────────────┐
  │  Graph Results:               │
  │  • Commit abc123              │
  │    - hash: abc123             │
  │    - message: "Fix div/0"     │
  │    - vector_id: vec_abc       │
  │  • Commit def456              │
  │    - hash: def456             │
  │    - message: "Refactor"      │
  │    - vector_id: vec_def       │
  └──────────┬────────────────────┘
             │
             ▼
  ┌────────────────────────────────┐
  │  3. Extract Vector IDs         │
  │     [vec_abc, vec_def, ...]    │
  └──────────┬─────────────────────┘
             │
             ▼
  ┌────────────────────────────────┐
  │  4. VECTORDB Fetch             │
  │     Get full content by IDs    │
  └──────────┬─────────────────────┘
             │
             ▼
  ┌───────────────────────────────┐
  │  Vector Results:              │
  │  • Full commit messages       │
  │  • Code diffs                 │
  │  • Context                    │
  │  • Embeddings (for more       │
  │    semantic queries)          │
  └──────────┬────────────────────┘
             │
             ▼
  ┌─────────────────────────────┐
  │  5. Combine & Enrich        │
  │  • Commit metadata (graph)  │
  │  • + Full content (vector)  │
  │  • = Complete picture       │
  └──────────┬──────────────────┘
            │
            ▼
  ┌─────────────────────────┐
  │  Return to User:        │
  │  • All John's commits   │
  │  • Full messages/diffs  │
  │  • Related files        │
  │  • Impact analysis      │
  └─────────────────────────┘
```

### Code Example:

```python
result = ltm.query(
    query="commits by John Doe",
    strategy=QueryStrategy.GRAPH_FIRST,
    top_k=10
)

# Result:
# {
#   'graph_relations': [
#     {'commit': 'abc123', 'message': 'Fix...', 'date': '2023-09-10'},
#     ...
#   ],
#   'semantic_matches': [
#     {'content': 'Full commit message and diff...', 'vector_id': 'vec_abc'},
#     ...
#   ]
# }
```

---

## 🔍 Workflow 4: Parallel Query (Best of Both)

**Use Case:** "Explain how the analytics bug was fixed"

```
┌───────────────────────────────────┐
│  COMPLEX USER QUERY               │
│  "Explain analytics bug fix"      │
└────────────┬──────────────────────┘
             │
    ┌────────┴────────┐
    │  Analyze Query  │
    │  Needs both:    │
    │  • Semantic     │
    │  • Structural   │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌────────────┐  ┌──────────────┐
│ VECTORDB   │  │ GRAPH DB     │
│            │  │              │
│ Search:    │  │ Query:       │
│ "analytics │  │ MATCH        │
│  bug fix"  │  │ (b:Bug)      │
│            │  │ -[:FIXED_BY] │
│            │  │ ->(c:Commit) │
└─────┬──────┘  └──────┬───────┘
      │                │
      │ Parallel       │ Parallel
      │ Execution      │ Execution
      │                │
      ▼                ▼
┌──────────────┐  ┌─────────────────┐
│ Vector       │  │ Graph           │
│ Results:     │  │ Results:        │
│ • Bug #242   │  │ • Bug node      │
│ • Discussions│  │ • → Commit link │
│ • Similar    │  │ • → Function    │
│   issues     │  │ • → Module      │
└──────┬───────┘  └────────┬────────┘
       │                   │
       └─────────┬─────────┘
                 ▼
      ┌────────────────────┐
      │  Merge Results     │
      │  • Semantic +      │
      │  • Structural =    │
      │  • Complete answer │
      └──────────┬─────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │  LLM Generation      │
      │  (Optional)          │
      │  Use context to      │
      │  generate explanation│
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────────┐
      │  Final Answer:           │
      │  "Bug #242 (division by  │
      │   zero) was fixed in     │
      │   commit abc123 by John  │
      │   Doe. The fix added     │
      │   validation in          │
      │   computeMetrics..."     │
      └──────────────────────────┘
```

### Code Example:

```python
result = ltm.query(
    query="Explain how analytics bug was fixed",
    strategy=QueryStrategy.PARALLEL,
    top_k=5
)

# Get rich context
context = {
    'bug_description': result.semantic_matches[0],
    'fix_commit': result.graph_relations[0],
    'affected_code': result.graph_relations[1],
    'similar_issues': result.semantic_matches[1:]
}

# Optional: Generate explanation with LLM
from utils.llm_client import get_llm_client
llm = get_llm_client()

explanation = llm.generate(
    prompt=f"Explain this bug fix: {context}",
    context=context
)
```

---

## 🔗 Workflow 5: Relationship Traversal

**Use Case:** "Show impact of changing computeMetrics"

```
┌──────────────────────────────┐
│  Query: Impact Analysis      │
│  Target: computeMetrics      │
└────────────┬─────────────────┘
             │
             ▼
  ┌──────────────────────────┐
  │  1. Find Entity in Graph │
  │     entity_id =          │
  │     "func_computeMetrics"│
  └──────────┬───────────────┘
             │
             ▼
  ┌──────────────────────────────────┐
  │  2. Graph Traversal              │
  │     MATCH (f:Function {id: ...}) │
  │     MATCH (f)-[:CALLS*1..3]      │
  │           ->(dep:Function)       │
  │     MATCH (f)<-[:CALLS]-         │
  │           (caller:Function)      │
  │     MATCH (f)<-[:MODIFIES]-      │
  │           (c:Commit)             │
  │     RETURN *                     │
  └──────────┬───────────────────────┘
             │
             ▼
  ┌──────────────────────────────┐
  │  Graph Results (Network):    │
  │                              │
  │      main()                  │
  │        ↓                     │
  │   computeMetrics() ← Target  │
  │      ↓         ↓             │
  │  calcAvg()  calcStd()        │
  │                              │
  │  Modified by:                │
  │  • abc123 (fix)              │
  │  • def456 (refactor)         │
  └──────────┬───────────────────┘
             │
             ▼
  ┌────────────────────────────────┐
  │  3. Enrich with Vector Content │
  │     For each node, get:        │
  │     • Full description         │
  │     • Code snippets            │
  │     • Documentation            │
  └──────────┬─────────────────────┘
             │
             ▼
  ┌───────────────────────────────┐
  │  Impact Analysis Result:      │
  │                               │
  │  Direct Impact:               │
  │  • 2 callers: main, process   │
  │  • 2 dependencies: calcAvg,   │
  │    calcStd                    │
  │                               │
  │  Indirect Impact:             │
  │  • Module: Analytics          │
  │  • API endpoints: /metrics    │
  │  • Tests: 5 unit tests        │
  │                               │
  │  Historical Changes:          │
  │  • 2 commits in last 3 months │
  │  • 1 bug fix, 1 refactor      │
  │                               │
  │  Recommendation:              │
  │  • Test all callers           │
  │  • Review dependencies        │
  │  • Update documentation       │
  └───────────────────────────────┘
```

### Code Example:

```python
# Get all related entities
impact = ltm.get_related(
    entity_id="func_computeMetrics",
    relationship_types=['CALLS', 'CALLED_BY', 'MODIFIES'],
    max_depth=3
)

# Find path between entities
path = ltm.find_path(
    start_id="func_computeMetrics",
    end_id="api_metrics_endpoint",
    max_length=5
)
```

---

## 🎯 Decision Tree: Which Strategy?

```
                    User Query
                        │
                        ▼
          ┌─────────────────────────┐
          │  Query Type?            │
          └────────┬────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌─────────┐  ┌─────────┐  ┌──────────┐
│ Fuzzy   │  │ Precise │  │ Complex  │
│ Semantic│  │ Struct. │  │ Both     │
└────┬────┘  └────┬────┘  └────┬─────┘
     │            │            │
     ▼            ▼            ▼
 Vector      Graph First   Parallel
  First         Query        Query
     │            │            │
     │            │            │
Examples:     Examples:    Examples:
• "Similar   • "Commits   • "Explain
  functions"   by author"   bug fix"
• "Related   • "Files in  • "Impact
  to error"    module"      analysis"
• "About     • "Direct    • "How was
  metrics"     callers"     it done"
```

---

## 📊 Performance Characteristics

| Strategy | Speed | Precision | Recall | Use Case |
|----------|-------|-----------|--------|----------|
| **Vector First** | ⚡⚡ Fast | 🎯 Medium | 📊 High | Broad search |
| **Graph First** | ⚡⚡⚡ Fastest | 🎯🎯🎯 High | 📊 Medium | Precise query |
| **Parallel** | ⚡ Slower | 🎯🎯 High | 📊📊 High | Complex query |
| **Vector Only** | ⚡⚡⚡ Fastest | 🎯 Low | 📊📊📊 Highest | Fuzzy search |
| **Graph Only** | ⚡⚡ Fast | 🎯🎯🎯 Highest | 📊 Low | Exact match |

---

**Summary:**
- **VectorDB** = Fast, fuzzy, semantic
- **Graph** = Precise, structured, relational
- **Hybrid** = Best of both! 🚀

Choose strategy based on query type and requirements.
