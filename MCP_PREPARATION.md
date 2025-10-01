# 🎯 MCP Preparation Guide

**Project:** Memory Layer Lab  
**Target:** Innocody Production (MCP Server)  
**Status:** Lab → Production Ready

---

## 📋 Overview

This Memory Layer will be packaged as an **MCP (Model Context Protocol) Server** for Innocody.

### What is MCP?
- Protocol for LLM context management
- Provides tools, resources, prompts to LLMs
- Stateful, persistent memory across sessions

### Memory Layer as MCP
```
┌─────────────────────────────────────────────┐
│           Innocody (Production)             │
├─────────────────────────────────────────────┤
│  LLM Client  ──────►  MCP Server            │
│                       (Memory Layer)        │
│                          │                  │
│                          ├─► STM            │
│                          ├─► MTM            │
│                          └─► LTM            │
└─────────────────────────────────────────────┘
```

---

## 🎯 MCP Endpoints to Implement

### 1. Memory Operations
```python
# Store message
POST /memory/store
{
  "role": "user",
  "content": "...",
  "context": {...}
}

# Query memory
POST /memory/query
{
  "query": "...",
  "top_k": 3,
  "layers": ["stm", "mtm", "ltm"]
}

# Get context for LLM
GET /memory/context?conversation_id=xxx
Response: {
  "stm": [...],
  "mtm": [...],
  "ltm": [...],
  "compressed": true,
  "token_count": 1500
}
```

### 2. Compression Operations
```python
# Compress conversation to summary
POST /memory/compress
{
  "conversation_id": "xxx",
  "strategy": "semantic"  # or "extractive"
}

# Get compression stats
GET /memory/stats/compression
```

### 3. Evaluation Operations
```python
# Run evaluation
POST /evaluate
{
  "config": {...},
  "test_queries": [...]
}

# Get current config
GET /config
```

---

## 🔧 Evaluation Tools

### Quick Reference

```bash
# 1. Full evaluation
python3 evaluate_memory.py

# 2. Tune parameters
python3 tune_parameters.py grid

# 3. Compare configs
python3 compare_configs.py preset

# 4. Check integration
python3 check_integration.py
```

### Evaluation Metrics

**Retrieval Quality:**
- Precision: How many retrieved items are relevant?
- Recall: How many relevant items are retrieved?
- F1 Score: Harmonic mean of precision & recall
- Source Coverage: Are all memory layers utilized?

**Context Compression:**
- Compression Ratio: compressed_tokens / total_tokens
- Token Savings %: How much context reduced?
- Information Retention: Quality after compression

**Performance:**
- Retrieval Latency: Time to find relevant memories
- Total Latency: End-to-end query time
- Token Count: Context size for LLM

---

## 📊 Parameter Tuning Guide

### Key Parameters

**STM (Short-Term Memory):**
- `max_items`: 5-20 (default: 10)
  - Lower: Faster, less context
  - Higher: Slower, more context

**MTM (Mid-Term Memory):**
- `max_chunks`: 10-50 (default: 20)
  - Lower: More compression
  - Higher: More detail

**Retrieval:**
- `top_k`: 1-7 (default: 3)
  - Lower: Faster, may miss info
  - Higher: Slower, better recall

### Tuning Strategy

**1. Start with defaults:**
```python
config = {
    'stm_max_items': 10,
    'mtm_max_chunks': 20,
    'top_k': 3
}
```

**2. Run baseline evaluation:**
```bash
python3 evaluate_memory.py
```

**3. Identify bottleneck:**
- Low F1? → Increase top_k or memory sizes
- High latency? → Decrease memory sizes
- Poor compression? → Tune MTM size

**4. Grid search for optimal:**
```bash
python3 tune_parameters.py grid
```

**5. A/B test top configs:**
```bash
python3 compare_configs.py
```

---

## 🎯 Target Performance (Production)

### Minimum Requirements
- ✅ F1 Score: ≥ 0.7
- ✅ Latency: ≤ 100ms
- ✅ Compression: ≥ 40% savings
- ✅ Pass Rate: ≥ 80%

### Optimal Targets
- 🎯 F1 Score: ≥ 0.85
- 🎯 Latency: ≤ 50ms
- 🎯 Compression: ≥ 60% savings
- 🎯 Pass Rate: ≥ 90%

---

## 🚀 Production Checklist

### Pre-Production

- [ ] Run full evaluation suite
  ```bash
  python3 evaluate_memory.py
  ```

- [ ] Tune parameters for your domain
  ```bash
  python3 tune_parameters.py grid
  ```

- [ ] Compare top 3 configurations
  ```bash
  python3 compare_configs.py
  ```

- [ ] Validate with real queries
  ```bash
  python3 test_code_analysis.py
  ```

- [ ] Check integration
  ```bash
  python3 check_integration.py
  ```

### MCP Packaging

- [ ] Implement MCP protocol endpoints
- [ ] Add authentication/authorization
- [ ] Setup persistent storage (DB)
- [ ] Configure scaling (if needed)
- [ ] Add monitoring & logging
- [ ] Create API documentation
- [ ] Write deployment guide

### Testing

- [ ] Unit tests for each layer
- [ ] Integration tests for pipeline
- [ ] Load testing (concurrent queries)
- [ ] Memory leak testing
- [ ] Failover testing

### Documentation

- [ ] API reference
- [ ] Configuration guide
- [ ] Deployment guide
- [ ] Troubleshooting guide
- [ ] Performance tuning guide

---

## 📦 MCP Package Structure

```
innocody-memory-mcp/
├── server/
│   ├── __init__.py
│   ├── mcp_server.py        # MCP protocol implementation
│   ├── memory_service.py    # Memory operations
│   └── compression.py       # Context compression
│
├── core/                    # From lab
│   ├── short_term.py
│   ├── mid_term.py
│   └── long_term.py
│
├── evaluation/              # Evaluation tools
│   ├── evaluate_memory.py
│   ├── tune_parameters.py
│   └── compare_configs.py
│
├── config/
│   ├── production.yaml
│   └── schema.json
│
├── tests/
│   ├── test_mcp.py
│   ├── test_memory.py
│   └── test_compression.py
│
├── docs/
│   ├── API.md
│   ├── TUNING.md
│   └── DEPLOYMENT.md
│
└── requirements.txt
```

---

## 🔄 Migration Path: Lab → Production

### Phase 1: Lab Testing ✅
- ✅ Develop memory layers
- ✅ Create test data
- ✅ Build evaluation tools
- ✅ Tune parameters

### Phase 2: MCP Development (Current)
- [ ] Implement MCP protocol
- [ ] Add persistence layer
- [ ] Setup authentication
- [ ] Create API docs

### Phase 3: Integration
- [ ] Integrate with Innocody
- [ ] Deploy to staging
- [ ] Run integration tests
- [ ] Load testing

### Phase 4: Production
- [ ] Deploy to production
- [ ] Monitor performance
- [ ] Iterate based on metrics
- [ ] Scale as needed

---

## 🎯 Next Steps

### Immediate (Lab)
1. Run evaluation with current data
2. Tune parameters for code analysis domain
3. Document optimal configuration
4. Prepare for MCP development

### Short-term (MCP Dev)
1. Setup MCP server skeleton
2. Implement memory endpoints
3. Add compression logic
4. Create integration tests

### Long-term (Production)
1. Deploy to Innocody staging
2. Collect real-world metrics
3. Refine based on usage patterns
4. Scale infrastructure

---

## 📚 Resources

### Evaluation
- `evaluate_memory.py` - Comprehensive evaluation
- `tune_parameters.py` - Parameter optimization
- `compare_configs.py` - Config comparison

### Documentation
- `README.md` - Project overview
- `SETUP.md` - Setup instructions
- `PROJECT_STATUS.md` - Current status
- `MCP_PREPARATION.md` - This guide

### Data
- `data/` - Test data (schema-compliant)
- `utils/schema/` - JSON schemas
- `config/` - Configuration files

---

**Status:** ✅ Lab Complete, Ready for MCP Development  
**Next:** Implement MCP Server Protocol  
**Target:** Production-ready Memory Layer for Innocody
