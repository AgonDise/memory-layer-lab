# 🧩 Workflow Memory Layer Lab (Updated)

## Tổng quan Workflow

```mermaid
flowchart TD
    A[User Query] --> B[Input Preprocessor]
    B --> C[Short-term Memory]
    B --> D[Mid-term Memory]
    B --> E[Long-term Memory]

    D --> D1[Neo4j Temporal Graph]
    D --> D2[Neo4j Knowledge Graph]

    E --> E1[Neo4j Knowledge Graph (long-term)]
    E --> E2[Vector DB (semantic search)]

    C --> F[Memory Aggregator]
    D1 --> F
    D2 --> F
    E1 --> F
    E2 --> F

    F --> G[Context Compressor]
    G --> H[Reasoner / LLM]
    H --> I[Response Synthesizer]
    I --> J[Final Output]
```

---

## 🔹 Các Module & Vai trò

### 1. Input Preprocessor
- **Input**: user query (string, code snippet, command).
- **Nhiệm vụ**:
  - Chuẩn hóa input (lowercase, remove noise).
  - Xác định intent (search code, hỏi bug, tài liệu, commit log).
  - Tạo embedding vector (giả lập hoặc model thật).
- **Output**: structured query object:
```json
{
  "raw_text": "Find bug in checkpoints.rs",
  "embedding": [0.123, -0.456, ...],
  "intent": "code_search"
}
```

### 2. Short-term Memory (STM)
- **Input**: Query object.
- **Nhiệm vụ**: Lưu giữ ngữ cảnh gần (5–20 turn chat gần nhất, code buffer).
- **Output**: small context chunk (tokens < 1k).
```json
{
  "stm_context": "last 10 user queries and responses"
}
```

### 3. Mid-term Memory (MTM)
#### a. Temporal Graph (Neo4j)
- **Mục đích**: lưu **dòng thời gian** commit, checkpoints, thay đổi code.  
- **Node types**: `Commit`, `Checkpoint`  
- **Edges**: `NEXT`, `AFFECTS`  

**Output Example**:
```json
{
  "temporal_graph": [
    {"commit": "abc123", "time": "2025-09-30T10:00", "affects": ["checkpoints.rs"]}
  ]
}
```

#### b. Knowledge Graph (Neo4j)
- **Mục đích**: lưu **quan hệ ngữ nghĩa** giữa function, class, module.  
- **Node types**: `Function`, `Class`, `Module`, `Concept`  
- **Edges**: `CALLS`, `BELONGS_TO`, `RELATED_TO`  

**Output Example**:
```json
{
  "knowledge_graph": [
    {"function": "apply_patch", "calls": ["validate_status"], "module": "git.rs"}
  ]
}
```

---

### 4. Long-term Memory (LTM)
#### a. Knowledge Graph (Neo4j)
- Lưu **kiến thức bền vững**: design docs, module relationship, domain knowledge.  
- **Ví dụ Output**:
```json
{
  "ltm_knowledge_graph": "Design doc v0.3 relations between AST and Parser"
}
```

#### b. Vector DB (Semantic Search)
- Lưu **embedding vectors** của docs, commit logs, spec.  
- Cho phép semantic retrieval theo cosine similarity / ANN.  

**Output Example**:
```json
{
  "ltm_vecdb": [
    {"chunk": "Bug report: drop(status) not defined", "score": 0.92}
  ]
}
```

---

### 5. Memory Aggregator
- **Input**: STM, MTM, LTM contexts.
- **Nhiệm vụ**: Merge + deduplicate + ranking theo relevance score.
- **Output**: unified context (multi-layer).
```json
{
  "aggregated_context": "...merged stm+mtm+ltm..."
}
```

### 6. Context Compressor
- **Input**: Aggregated context.
- **Nhiệm vụ**: Nén để fit LLM (token budgeting).  
- **Output**: compressed context (500–2k tokens).

### 7. Reasoner / LLM
- **Input**: user query + compressed context.  
- **Output**: raw answer.

### 8. Response Synthesizer
- **Input**: LLM output.  
- **Output**: final formatted answer.

---

## 🏗️ Build Neo4j Server

Bạn đã có runner host, các bước chuẩn để chạy Neo4j:

```bash
# 1. Pull Neo4j image
docker pull neo4j:5.25

# 2. Run Neo4j container
docker run \
  --name neo4j-lab \
  -p 7474:7474 -p 7687:7687 \
  -d \
  -e NEO4J_AUTH=neo4j/test123 \
  -v $HOME/neo4j/data:/data \
  neo4j:5.25

# 3. Truy cập UI
http://localhost:7474

# 4. Query ví dụ
MATCH (c:Commit)-[:AFFECTS]->(f:File {name:"checkpoints.rs"})
RETURN c LIMIT 10;
```

Bạn có thể chạy **2 database trong 1 instance Neo4j**:  
- `temporal_kg` → cho commit timeline (MTM)  
- `longterm_kg` → cho knowledge graph (LTM)  

Thêm một **Vector DB** (Weaviate, Qdrant, Milvus, hoặc SQLite FAISS) để giữ semantic search.

---

## 📂 Cấu trúc file Lab

```
memory_layer_lab/
│
├── main.py
├── preprocessor.py
├── stm.py
├── mtm/
│   ├── __init__.py
│   ├── temporal_graph.py
│   ├── knowledge_graph.py
│   └── query.py
├── ltm/
│   ├── __init__.py
│   ├── knowledge_graph.py
│   ├── vecdb.py
│   └── query.py
├── aggregator.py
├── compressor.py
├── reasoner.py
└── synthesizer.py
```

---

## 🏁 Input / Output chuẩn của Lab

- **Input Lab**:  
  - User Query (string)  
  - Fake Embedding Vector (random float[], dim=128/384/512)  
  - Context Logs (JSON)

- **Output Lab**:  
  - Aggregated context (JSON)  
  - Compressed context (JSON/tokens)  
  - Final Reasoned Answer (string/JSON)
