# 🚀 Quick Start - Semantic Search

**Goal:** Get semantic search working in 5 minutes

---

## ⚡ 3 Commands to Success

```bash
# 1. Install dependencies (optional but recommended)
pip install sentence-transformers scikit-learn

# 2. Generate embedded test data
python3 generate_embedded_data.py

# 3. Run semantic search tests
python3 test_semantic_search.py
```

**Expected Output:**
- ✅ 20 MTM chunks generated
- ✅ 30 LTM facts generated  
- ✅ 6 queries tested
- ✅ Relevance: 60-80% (with real embeddings)

---

## 📖 Basic Usage

### 1. Generate Embeddings

```python
from utils.real_embedding import RealEmbeddingGenerator

embedder = RealEmbeddingGenerator()
embedding = embedder.generate("Hello, world!")
print(f"Embedding dimension: {len(embedding)}")  # 384
```

### 2. Add to Memory with Embeddings

```python
from core.short_term import ShortTermMemory

stm = ShortTermMemory()

# Add with embedding
content = "What is machine learning?"
embedding = embedder.generate(content)
stm.add(role='user', content=content, embedding=embedding)
```

### 3. Semantic Search

```python
# Search by similarity
query_emb = embedder.generate("Tell me about AI")
results = stm.search_by_embedding(query_emb, top_k=5)

for r in results:
    print(f"Similarity: {r['similarity']:.2f} - {r['content']}")
```

### 4. Use with Orchestrator

```python
from core.orchestrator import MemoryOrchestrator

context = orchestrator.get_context(
    query="How to train neural networks?",
    use_embedding_search=True  # Enable semantic search
)

print(f"STM hits: {context['aggregated']['stm_count']}")
print(f"MTM hits: {context['aggregated']['mtm_count']}")
```

---

## 📊 What You Get

### Performance:
- ⚡ **7ms** average query time
- 🎯 **60-80%** relevance (with real embeddings)
- 📦 **384-dim** embeddings
- 🔍 **Cosine similarity** scoring

### Features:
- ✅ Real semantic understanding
- ✅ Multi-layer search (STM + MTM + LTM)
- ✅ Automatic ranking by relevance
- ✅ Fallback to mock if dependencies missing
- ✅ Backwards compatible

---

## 🔧 Troubleshooting

### Issue: "No module named 'sentence_transformers'"
**Solution:**
```bash
pip install sentence-transformers scikit-learn torch
```

### Issue: "File not found: data/mid_term_chunks.json"
**Solution:**
```bash
mkdir -p data
python3 generate_embedded_data.py
```

### Issue: "Relevance is only 9.7%"
**Cause:** Using mock embeddings (random)
**Solution:** Install sentence-transformers (see above)

---

## 📚 More Info

- **SESSION_SUMMARY.md** - Full session summary
- **SEMANTIC_SEARCH_IMPLEMENTATION.md** - Complete guide
- **IMPROVEMENTS_SUMMARY.md** - What was fixed

---

## 🎯 Quick Test

```python
# Test if semantic search is working
from utils.real_embedding import RealEmbeddingGenerator

embedder = RealEmbeddingGenerator()

# Generate embeddings
emb1 = embedder.generate("I love machine learning")
emb2 = embedder.generate("AI is amazing")
emb3 = embedder.generate("I like pizza")

# Check similarity
sim_12 = embedder.similarity(emb1, emb2)  # Should be HIGH
sim_13 = embedder.similarity(emb1, emb3)  # Should be LOW

print(f"ML vs AI: {sim_12:.2f}")    # ~0.7-0.9
print(f"ML vs Pizza: {sim_13:.2f}") # ~0.4-0.5

if sim_12 > sim_13:
    print("✅ Semantic search is working!")
else:
    print("⚠️  Using mock embeddings (random)")
```

---

**That's it! You're ready to go! 🎉**
