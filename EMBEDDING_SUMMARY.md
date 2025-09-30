# Embedding & Data Population Summary

## 🎯 Vấn đề đã giải quyết

Bạn có `schema.yaml` nhưng chưa biết:
1. ✅ Cách tạo embeddings giả lập
2. ✅ Cách đưa data vào để test

## 📦 Files đã tạo

### 1. `utils/embedding_utils.py` - Embedding utilities
**Classes:**
- `FakeEmbeddingGenerator` - Tạo embeddings giả lập (deterministic)
- `RealEmbeddingGenerator` - Tạo embeddings thật (sentence-transformers)
- `EmbeddingCache` - Cache embeddings vào disk
- `get_embedder()` - Factory function

**Features:**
```python
# Fake embeddings (không cần model)
embedder = FakeEmbeddingGenerator(embedding_dim=384)
emb = embedder.generate("your text here")

# Same text → same embedding
emb1 = embedder.generate("hello")
emb2 = embedder.generate("hello")
assert emb1 == emb2  # ✅ True

# Calculate similarity
sim = embedder.cosine_similarity(emb1, emb2)
```

### 2. `populate_from_schema.py` - Data population script
**Chức năng:**
- Load data từ `schema.yaml`
- Generate embeddings tự động
- Populate vào STM, MTM, LTM
- Demo queries với kết quả

**Usage:**
```bash
python populate_from_schema.py
```

### 3. `POPULATE_DATA_GUIDE.md` - Complete guide
- Giải thích embeddings hoạt động như thế nào
- Schema format chi tiết
- Usage instructions
- Troubleshooting
- Examples

### 4. `example_embedding_usage.py` - Quick example
Ví dụ đơn giản về:
- Generate embeddings
- Add vào memory layers
- Search by embedding
- Calculate similarity

**Usage:**
```bash
python example_embedding_usage.py
```

---

## 🚀 Quick Start

### Step 1: Cài đặt
```bash
pip install pyyaml numpy
```

### Step 2: Chạy example
```bash
# Quick example
python example_embedding_usage.py

# Full data population
python populate_from_schema.py
```

### Step 3: Customize
Edit `schema.yaml` với data của bạn:

```yaml
short_term:
  - role: "user"
    content: "Your message here"

mid_term:
  - text: "Your summary here"
    metadata:
      file: "your_file.py"

long_term:
  vector:
    - text: "Your document here"
      metadata:
        source: "documentation"
```

---

## 🧪 Embedding Methods

### Method 1: Fake Embeddings (Recommended for testing)

**Pros:**
- ✅ Không cần model/API
- ✅ Fast & reproducible
- ✅ Deterministic (same text → same embedding)
- ✅ Good for unit tests

**Cons:**
- ❌ Không có semantic meaning thật
- ❌ Similarity scores không chính xác như real embeddings

**Usage:**
```python
from utils import FakeEmbeddingGenerator

embedder = FakeEmbeddingGenerator(embedding_dim=384)
emb = embedder.generate("login_user function")
```

### Method 2: Real Embeddings (For production)

**Pros:**
- ✅ True semantic similarity
- ✅ Better search quality
- ✅ Industry standard

**Cons:**
- ❌ Requires sentence-transformers
- ❌ Slower than fake
- ❌ Needs model download

**Usage:**
```python
from utils import RealEmbeddingGenerator

embedder = RealEmbeddingGenerator(model_name='all-MiniLM-L6-v2')
emb = embedder.generate("login_user function")
```

---

## 📊 Schema Format Reference

### Short-term Memory
```yaml
short_term:
  - id: "msg_001"
    role: "user"              # Required
    content: "Your message"   # Required
    token_count: 12           # Optional
    timestamp: "ISO8601"      # Optional
```

### Mid-term Memory
```yaml
mid_term:
  - id: "conv_001"
    text: "Summary text"      # Required
    embedding: [...]          # Optional (auto-generated)
    metadata:                 # Optional
      file: "file.py"
      function: "func_name"
      commit: "abc123"
      timestamp: "ISO8601"
```

### Long-term Memory - Vector
```yaml
long_term:
  vector:
    - id: "kb_001"
      text: "Document text"   # Required
      embedding: [...]        # Optional (auto-generated)
      metadata:               # Optional
        source: "doc"
        topic: "topic_name"
```

### Long-term Memory - Graph
```yaml
long_term:
  graph:
    nodes:
      - id: "node_id"
        label: "Function"     # Function|Class|Commit|Doc
        name: "func_name"
    edges:
      - from: "node_1"
        to: "node_2"
        type: "CALLS"         # Relationship type
```

---

## 🔍 Example Queries

### Query Short-term Memory
```python
from utils import FakeEmbeddingGenerator

embedder = FakeEmbeddingGenerator()
query_emb = embedder.generate("login function")

# Search
results = stm.search_by_embedding(query_emb, top_k=5)
for msg in results:
    print(f"[{msg['role']}] {msg['content']}")
    print(f"Score: {msg['relevance_score']:.3f}")
```

### Query Mid-term Memory
```python
results = mtm.search_by_embedding(query_emb, top_k=5)
for chunk in results:
    print(chunk['summary'])
    print(f"Score: {chunk['relevance_score']:.3f}")
```

### Query Long-term Vector DB
```python
results = ltm.vector_db.search(query_emb, top_k=5)
for doc in results:
    print(f"[{doc['id']}] {doc['content']}")
    print(f"Score: {doc['score']:.3f}")
```

---

## 💡 Tips & Best Practices

### 1. Embedding Dimension
- **384**: Good balance (default)
- **768**: Better quality, slower
- **128**: Faster, less accurate

### 2. Caching
```python
from utils import EmbeddingCache

cache = EmbeddingCache('my_cache.json')
if not cache.has(text):
    emb = embedder.generate(text)
    cache.put(text, emb)
    cache.save()
else:
    emb = cache.get(text)
```

### 3. Batch Processing
```python
texts = ["text1", "text2", "text3"]
embeddings = embedder.generate_batch(texts)  # Faster
```

### 4. Normalize Vectors
Always normalize for cosine similarity:
```python
emb = emb / np.linalg.norm(emb)
```

---

## 🎬 Complete Workflow

```python
# 1. Setup
from utils import FakeEmbeddingGenerator
from core import ShortTermMemory

embedder = FakeEmbeddingGenerator(384)
stm = ShortTermMemory()

# 2. Add data with embeddings
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there"}
]

for msg in messages:
    emb = embedder.generate(msg['content'])
    stm.add(role=msg['role'], content=msg['content'], embedding=emb)

# 3. Query
query_emb = embedder.generate("greeting")
results = stm.search_by_embedding(query_emb, top_k=3)

# 4. Show results
for r in results:
    print(f"{r['content']} (score: {r['relevance_score']:.3f})")
```

---

## 📚 Files Organization

```
memory-layer-lab/
├── schema.yaml                    # Your data schema
├── populate_from_schema.py        # ✨ Main script
├── example_embedding_usage.py     # ✨ Quick example
├── POPULATE_DATA_GUIDE.md         # ✨ Complete guide
├── EMBEDDING_SUMMARY.md           # ✨ This file
│
├── utils/
│   └── embedding_utils.py         # ✨ Embedding utilities
│
└── core/
    ├── short_term.py              # Has search_by_embedding()
    ├── mid_term.py                # Has search_by_embedding()
    └── long_term.py               # Has vector DB integration
```

---

## ✅ Checklist

### Testing
- [ ] Run `python example_embedding_usage.py`
- [ ] Verify embeddings are generated
- [ ] Check search results make sense

### Data Population
- [ ] Edit `schema.yaml` with your data
- [ ] Run `python populate_from_schema.py`
- [ ] Verify all memory layers populated
- [ ] Test queries with your data

### Production
- [ ] Consider switching to real embeddings
- [ ] Enable embedding cache
- [ ] Tune embedding dimension
- [ ] Add more test data

---

## 🔗 Related Documentation

- **POPULATE_DATA_GUIDE.md** - Detailed guide
- **WORKFLOW.md** - Overall system workflow
- **NEO4J_SETUP.md** - Neo4j integration
- **README.md** - Project overview

---

## 🆘 Troubleshooting

### "No embeddings generated"
```python
# Check if embedder is working
embedder = FakeEmbeddingGenerator()
emb = embedder.generate("test")
print(len(emb))  # Should be 384
```

### "Low similarity scores"
- Fake embeddings don't have real semantic meaning
- Try with more similar text
- Consider using real embeddings

### "schema.yaml not found"
```bash
# Ensure in correct directory
pwd  # Should show memory-layer-lab
ls schema.yaml  # Should exist
```

---

## 🎉 Summary

**Bạn có thể:**
1. ✅ Generate embeddings (fake hoặc real)
2. ✅ Load data từ schema.yaml
3. ✅ Populate vào STM, MTM, LTM
4. ✅ Query với semantic search
5. ✅ Test với data của bạn

**Bắt đầu ngay:**
```bash
python example_embedding_usage.py
python populate_from_schema.py
```

**Customize:**
- Edit `schema.yaml`
- Adjust embedding dimension
- Switch to real embeddings
- Add more queries

---

**Date**: 2025-09-30  
**Status**: ✅ Complete  
**Ready to use**: ✅ Yes
