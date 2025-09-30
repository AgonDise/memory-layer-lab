# Guide: Populate Data from Schema

## 📖 Tổng quan

File này hướng dẫn cách:
1. Tạo embeddings giả lập cho testing
2. Load data từ `schema.yaml`
3. Populate vào các memory layers
4. Test queries

---

## 🎯 Embeddings Giả Lập

### Cách hoạt động

**EmbeddingGenerator** tạo embeddings deterministic (nhất quán) từ text:

```python
class EmbeddingGenerator:
    def generate(self, text: str) -> List[float]:
        # 1. Hash text để tạo seed
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        
        # 2. Seed random generator (reproducible)
        np.random.seed(seed)
        
        # 3. Generate random vector
        embedding = np.random.randn(self.embedding_dim)
        
        # 4. Normalize to unit length
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tolist()
```

**Ưu điểm:**
- ✅ Cùng text → cùng embedding (reproducible)
- ✅ Different text → different embedding
- ✅ Normalized vector (good for cosine similarity)
- ✅ Không cần model thật

**So sánh với real embeddings:**
```python
# Fake embedding (deterministic)
emb1 = embedder.generate("login_user function")
emb2 = embedder.generate("login_user function")
assert emb1 == emb2  # ✅ Same

# Real embedding (from sentence-transformers)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
real_emb = model.encode("login_user function")
```

---

## 📝 Schema Format

### Short-term Memory

```yaml
short_term:
  - id: "msg_001"
    role: "user"           # user | assistant | system
    content: "Hãy phân tích hàm login_user"
    token_count: 12        # optional
    timestamp: "2025-09-27T10:00:00Z"
```

**Được populate vào:**
- `ShortTermMemory.messages[]`
- Tự động generate embedding từ `content`

### Mid-term Memory

```yaml
mid_term:
  - id: "conv_001"
    text: "File auth_service.py có commit gần đây sửa login_user."
    embedding: [0.12, 0.33, -0.11, ...]   # optional, auto-generate if missing
    metadata:
      file: "auth_service.py"
      function: "login_user"
      commit: "abc123"                     # optional
      timestamp: "2025-09-20T10:15:00Z"
```

**Được populate vào:**
- `MidTermMemory.chunks[]` - Local storage
- `TemporalGraph` (Neo4j) - Nếu có `commit` trong metadata
- `KnowledgeGraph` (Neo4j) - Nếu có `function` trong metadata

### Long-term Memory - Graph

```yaml
long_term:
  graph:
    nodes:
      - id: "f1"
        label: "Function"        # Function | Class | Commit | Doc
        name: "login_user"
      - id: "c1"
        label: "Commit"
        hash: "abc123"
        message: "Fix bug"
        timestamp: "2025-09-18T08:30:00Z"
    
    edges:
      - from: "c1"
        to: "f1"
        type: "MODIFIES"         # HAS_FUNCTION | MODIFIES | IMPORTS
```

**Được populate vào:**
- `LTMKnowledgeGraph` (Neo4j mock mode)

### Long-term Memory - Vector

```yaml
long_term:
  vector:
    - id: "kb_001"
      text: "Spec của Innocody Engine: Short-term dùng sliding buffer..."
      embedding: [0.12, 0.88, ...]   # optional
      metadata:
        source: "documentation"
        topic: "memory_layer"
```

**Được populate vào:**
- `VectorDatabase` (FAISS/simple backend)

---

## 🚀 Cách Sử Dụng

### Bước 1: Cài đặt dependencies

```bash
pip install pyyaml numpy
```

### Bước 2: Chỉnh sửa schema.yaml

Thêm data mẫu của bạn:

```yaml
short_term:
  - id: "msg_003"
    role: "user"
    content: "Your custom message here"
    timestamp: "2025-09-30T10:00:00Z"

mid_term:
  - id: "conv_002"
    text: "Your summary here"
    metadata:
      file: "your_file.py"
      function: "your_function"
```

### Bước 3: Chạy populate script

```bash
python populate_from_schema.py
```

**Output:**
```
============================================================
Populating Short-term Memory
============================================================
✓ Added [user]: Hãy phân tích hàm login_user trong file auth_serv...
✓ Added [assistant]: Hàm login_user xử lý xác thực, tạo JWT token...

Total messages in STM: 2

============================================================
Populating Mid-term Memory
============================================================
✓ Added chunk: File auth_service.py có commit gần đây sửa login_...
  → Added to temporal graph: abc123
  → Added to knowledge graph: auth_service.login_user

Total chunks in MTM: 1

============================================================
DEMO: Querying Memory Layers
============================================================

--- Query: 'login_user function' ---

  STM Results (2):
    1. [user] Hãy phân tích hàm login_user trong file auth_service.py
       Score: 0.856
    2. [assistant] Hàm login_user xử lý xác thực, tạo JWT token...
       Score: 0.743
```

---

## 🔍 Testing Queries

### Query các memory layers

```python
from populate_from_schema import EmbeddingGenerator

embedder = EmbeddingGenerator(embedding_dim=384)
query_embedding = embedder.generate("your query here")

# Query STM
stm_results = stm.search_by_embedding(query_embedding, top_k=5)

# Query MTM
mtm_results = mtm.search_by_embedding(query_embedding, top_k=5)

# Query LTM
ltm_results = ltm.vector_db.search(query_embedding, top_k=5)
```

### Xem kết quả

```python
for result in stm_results:
    print(f"Role: {result['role']}")
    print(f"Content: {result['content']}")
    print(f"Score: {result['relevance_score']:.3f}")
```

---

## 🛠️ Customization

### Thay đổi embedding dimension

```python
# In populate_from_schema.py
embedding_dim = 768  # Default: 384
embedder = EmbeddingGenerator(embedding_dim=embedding_dim)
```

### Thêm queries mới

```python
# In populate_from_schema.py, function demo_queries()
queries = [
    "your custom query 1",
    "your custom query 2",
    # ...
]
```

### Sử dụng real embeddings

```python
# Install sentence-transformers
pip install sentence-transformers

# Replace EmbeddingGenerator
from sentence_transformers import SentenceTransformer

class RealEmbeddingGenerator:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def generate(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
```

---

## 📊 Example Data Scenarios

### Scenario 1: Code Review

```yaml
short_term:
  - role: "user"
    content: "Review the login_user function"
  - role: "assistant"
    content: "The function has 3 issues..."

mid_term:
  - text: "login_user was reviewed, found 3 issues"
    metadata:
      file: "auth.py"
      function: "login_user"

long_term:
  vector:
    - text: "Best practices for authentication functions"
      metadata:
        source: "documentation"
```

### Scenario 2: Bug Tracking

```yaml
mid_term:
  - text: "Bug in checkout_user: undefined variable status"
    metadata:
      file: "checkpoints.rs"
      function: "checkout_user"
      commit: "xyz789"

long_term:
  graph:
    nodes:
      - label: "Commit"
        hash: "xyz789"
        message: "Fix undefined variable bug"
```

---

## ⚡ Performance Tips

1. **Batch generation**: Generate embeddings cho nhiều texts cùng lúc
2. **Cache embeddings**: Lưu embeddings đã generate
3. **Use FAISS**: Nhanh hơn simple backend cho large datasets
4. **Normalize vectors**: Luôn normalize cho cosine similarity

---

## 🐛 Troubleshooting

### Error: "schema.yaml not found"
```bash
# Ensure you're in project root
cd /Users/innotech/memory-layer-lab
python populate_from_schema.py
```

### Error: "No module named 'yaml'"
```bash
pip install pyyaml
```

### Embeddings không consistent
```python
# Check if using same text
emb1 = embedder.generate("test")
emb2 = embedder.generate("test")
assert emb1 == emb2  # Should be True
```

### Low similarity scores
- Fake embeddings không semantic như real embeddings
- Text phải giống nhau nhiều mới có score cao
- Consider using real embeddings for better quality

---

## 📚 Next Steps

1. ✅ Populate data từ schema.yaml
2. ✅ Test queries
3. ⏭️ Integrate với orchestrator
4. ⏭️ Test với Neo4j real (optional)
5. ⏭️ Replace với real embeddings (optional)

---

## 🔗 Related Files

- `schema.yaml` - Data schema
- `populate_from_schema.py` - Main script
- `core/preprocessor.py` - Real embedding generation
- `demo_workflow.py` - End-to-end demo
- `demo_neo4j.py` - Neo4j specific demo
