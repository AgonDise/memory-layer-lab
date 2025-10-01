# ⚡ Setup Guide

## Minimal Setup (5 minutes)

```bash
# 1. Install core dependencies
pip install -r requirements.txt

# 2. Run chatbot
python main.py
```

Done! The system works with default settings.

---

## Full Setup (with all features)

### 1. Install Optional Dependencies

```bash
# Semantic search (recommended)
pip install sentence-transformers scikit-learn

# Tracing & observability
pip install langfuse
```

### 2. Configure System

**Option A: Via Web UI (Easy)**
```bash
python config_ui.py
# Open http://localhost:7861
# Adjust parameters via sliders
```

**Option B: Via Config File**
```bash
# Edit config file
nano config/system_config.yaml

# Adjust parameters:
# - compression.max_tokens
# - semantic_search.top_k_stm
# - response_generation.temperature
# etc.
```

### 3. Setup Langfuse (Optional)

```bash
# 1. Get API keys from https://cloud.langfuse.com
# 2. Copy config template
cp config/langfuse_config.yaml.example config/langfuse_config.yaml

# 3. Edit with your keys
nano config/langfuse_config.yaml

# 4. Enable in system config
# Set langfuse.enabled: true in config/system_config.yaml
```

### 4. Setup Neo4j (Optional)

```bash
# 1. Install Neo4j (or use Docker)
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# 2. Configure connection
cp config/neo4j_config.yaml.example config/neo4j_config.yaml
nano config/neo4j_config.yaml

# 3. Test connection
python test_neo4j_connection.py
```

---

## Quick Commands

```bash
# Run chatbot
python main.py

# Config UI
python config_ui.py

# Generate test data
python generate_embedded_data.py

# Run tests
python test_semantic_search.py
python test_comprehensive.py

# Test Neo4j
python test_neo4j_connection.py
```

---

## Troubleshooting

**Issue: Import errors**
```bash
pip install -r requirements.txt
```

**Issue: Langfuse not working**
- Check API keys in `config/langfuse_config.yaml`
- Set `langfuse.enabled: true` in `config/system_config.yaml`

**Issue: Slow performance**
- Disable real embeddings: `semantic_search.use_real_embeddings: false`
- Reduce top_k values
- Adjust compression.max_tokens

---

## What's Configured

Check `config/system_config.yaml` for 200+ parameters:
- Memory layer sizes
- Compression settings
- Semantic search thresholds
- LLM parameters
- Langfuse settings
- Neo4j settings

All adjustable via web UI or directly in the file!
