# Quick Start Guide

## 🚀 Get Started in 4 Steps

### 1. Install Dependencies

**macOS/Linux (với virtual environment - Recommended):**
```bash
# Activate existing venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Alternative (nếu chưa có venv):**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install
pip install -r requirements.txt
```

**Windows:**
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Tests

```bash
# Verify installation
python test_simple.py
```

Expected output:
```
✅ Imports: PASS
✅ Instantiation: PASS
✅ Basic Workflow: PASS
🎉 All tests passed!
```

### 3. Populate Data from Schema

```bash
# Load sample data and test queries
python populate_from_schema.py
```

Or try quick embedding example:
```bash
python example_embedding_usage.py
```

### 4. Try the Demos

```bash
# Complete workflow demo
python demo_workflow.py

# Neo4j integration demo
python demo_neo4j.py
```

**demo_workflow.py** runs 6 demos:
1. Input Preprocessing
2. Memory Layer Operations
3. Memory Aggregation & Ranking
4. Context Compression
5. Response Synthesis
6. Complete End-to-End Workflow

---

## 💬 Interactive Chatbot

```bash
python main.py
```

Commands:
- Type your message to chat
- `stats` - View conversation statistics
- `reset` - Clear all memory
- `quit` or `exit` - Save and exit

---

## 📖 Understanding the Workflow

### Basic Flow

```
Your Message
    ↓
Preprocess (extract intent, keywords, embedding)
    ↓
Search Memory Layers (STM, MTM, LTM)
    ↓
Aggregate & Rank contexts
    ↓
Compress to fit token budget
    ↓
Generate Response
    ↓
Format & Return
```

### Example

```python
from config import get_config
from main import create_chatbot

# Create chatbot
config = get_config()
chatbot = create_chatbot(config, use_advanced_workflow=True)

# Start
print(chatbot.start())

# Chat
response = chatbot.chat("Help me debug my code", use_embedding_search=True)
print(response)
```

---

## 🔧 Configuration

Edit `config.py`:

```python
MEMORY_CONFIG = {
    'short_term': {
        'max_size': 10,      # Number of recent messages
        'ttl': 3600,         # Time to live (seconds)
    },
    'mid_term': {
        'max_size': 100,     # Number of summary chunks
        'summarize_every': 5, # Summarize after N messages
    }
}
```

---

## 📁 Project Structure

```
memory_layer_lab/
├── main.py              # Run this for chatbot
├── demo_workflow.py     # Run this for demos
├── test_simple.py       # Run this for tests
│
├── core/                # Core workflow modules
│   ├── preprocessor.py  # Input preprocessing
│   ├── aggregator.py    # Context aggregation
│   ├── compressor.py    # Context compression
│   ├── synthesizer.py   # Response synthesis
│   └── ...
│
├── bot/                 # Chatbot implementation
└── utils/               # Utilities
```

---

## 📚 Documentation

- **README.md** - Project overview
- **WORKFLOW.md** - Detailed workflow documentation
- **IMPLEMENTATION_SUMMARY.md** - Implementation details
- **memory_layer_workflow.md** - Original specification

---

## ✅ Verification Checklist

- [ ] `pip install -r requirements.txt` runs successfully
- [ ] `python test_simple.py` passes all tests
- [ ] `python demo_workflow.py` completes without errors
- [ ] `python main.py` starts the chatbot
- [ ] Can chat with the bot and receive responses

---

## 🎯 What's Implemented

✅ **Core Workflow**
- Input preprocessing with embeddings
- Multi-layer memory (STM, MTM, LTM)
- Context aggregation with ranking
- Token-aware compression
- Response synthesis

✅ **Features**
- Intent detection (code_search, debug, documentation, etc.)
- Embedding-based similarity search
- Automatic summarization
- Weighted scoring across memory layers
- Multiple output formats

✅ **Demo & Tests**
- Simple tests for verification
- Complete workflow demonstration
- Interactive chatbot

---

## 🚧 Coming Soon

- Real embedding models (sentence-transformers)
- LLM API integration (OpenAI, Anthropic)
- Vector databases (ChromaDB, Pinecone)
- Graph database support (Neo4j)
- Web interface

---

## 🆘 Troubleshooting

### Import Errors

```bash
# Make sure numpy is installed
pip install numpy>=1.24.0
```

### Module Not Found

```bash
# Run from project root
cd memory-layer-lab
python main.py
```

### Memory Errors

```bash
# Clear saved memory state
rm memory_state.json
```

---

## 📞 Need Help?

1. Check `WORKFLOW.md` for detailed documentation
2. Review `IMPLEMENTATION_SUMMARY.md` for architecture
3. Run `demo_workflow.py` to see examples
4. Read code comments in core modules

---

**Ready to start? Run:** `python main.py` 🚀
