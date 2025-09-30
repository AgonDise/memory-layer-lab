# Memory Layer Lab - Complete Workflow Documentation

## Overview

This document describes the complete memory layer workflow implementation based on `memory_layer_workflow.md`.

## Workflow Components

### 1. Input Preprocessor (`core/preprocessor.py`)

**Purpose**: Preprocess user input and create structured query objects.

**Input**: Raw user query (string)

**Output**: Structured query object
```json
{
  "raw_text": "Find bug in checkpoints.rs",
  "normalized_text": "find bug in checkpoints rs",
  "embedding": [0.123, -0.456, ...],  // 384-dim vector
  "intent": "code_search",
  "keywords": ["find", "checkpoints"],
  "timestamp": "2024-01-01T00:00:00"
}
```

**Features**:
- Text normalization (lowercase, remove noise)
- Intent detection (code_search, debug, documentation, commit_log, general)
- Embedding generation (mock or real model)
- Keyword extraction

**Usage**:
```python
from core import InputPreprocessor

preprocessor = InputPreprocessor(embedding_dim=384)
query_obj = preprocessor.preprocess("Find bug in code")
print(query_obj['intent'])  # 'debug'
print(len(query_obj['embedding']))  # 384
```

---

### 2. Memory Layers

#### Short-term Memory (`core/short_term.py`)

**Purpose**: Store recent messages (5-20 turns) with TTL.

**Features**:
- Fixed-size buffer with automatic cleanup
- TTL (time-to-live) for messages
- Embedding-based similarity search
- Cosine similarity scoring

**Methods**:
```python
stm = ShortTermMemory(max_size=10, ttl_seconds=3600)

# Add message with embedding
stm.add('user', 'Hello', embedding=[...])

# Get recent messages
messages = stm.get_recent(n=5)

# Search by embedding
results = stm.search_by_embedding(query_embedding, top_k=3)
```

#### Mid-term Memory (`core/mid_term.py`)

**Purpose**: Store summarized conversation chunks.

**Features**:
- Stores summaries of conversation segments
- Embedding search for semantic retrieval
- Keyword-based search
- Relevance scoring

**Methods**:
```python
mtm = MidTermMemory(max_size=100)

# Add summary chunk
mtm.add_chunk(summary, metadata={'embedding': [...]})

# Search by embedding
results = mtm.search_by_embedding(query_embedding, top_k=5)

# Search by keywords
results = mtm.search_by_keywords(['debug', 'error'], top_k=5)
```

#### Long-term Memory (`core/long_term.py`)

**Purpose**: Placeholder for persistent cross-session memory.

**Future Features**:
- Vector database integration (Chroma, Pinecone)
- Graph database for relationships (Neo4j)
- Semantic search with embeddings
- Knowledge base storage

---

### 3. Memory Aggregator (`core/aggregator.py`)

**Purpose**: Merge and rank contexts from multiple memory layers.

**Input**: 
- STM context
- MTM context
- LTM context (optional)
- Query embedding

**Output**: Aggregated context with ranking
```json
{
  "items": [
    {
      "content": "...",
      "source": "short_term",
      "final_score": 0.85,
      "relevance_score": 0.9,
      "base_score": 0.5
    }
  ],
  "total_items": 10,
  "stm_count": 4,
  "mtm_count": 5,
  "ltm_count": 1
}
```

**Features**:
- Weighted scoring (STM: 0.5, MTM: 0.3, LTM: 0.2)
- Deduplication based on text similarity
- Relevance ranking
- Source tracking

**Usage**:
```python
from core import MemoryAggregator

aggregator = MemoryAggregator(
    stm_weight=0.5,
    mtm_weight=0.3,
    ltm_weight=0.2
)

aggregated = aggregator.aggregate(
    stm_context=stm_messages,
    mtm_context=mtm_chunks,
    ltm_context=None,
    query_embedding=query_obj['embedding']
)
```

---

### 4. Context Compressor (`core/compressor.py`)

**Purpose**: Compress aggregated context to fit token budget.

**Input**: Aggregated context

**Output**: Compressed context
```json
{
  "compressed_items": [...],
  "total_tokens": 450,
  "original_tokens": 2000,
  "compression_ratio": 0.225,
  "strategy": "score_based",
  "items_kept": 5,
  "items_removed": 8
}
```

**Strategies**:
1. **Truncate**: Simple cutoff at token limit
2. **Score-based**: Keep highest-scoring items, preserve recent
3. **MMR**: Maximal Marginal Relevance for diversity (TODO)

**Features**:
- Token estimation (~4 chars per token)
- Preserve recent messages option
- Multiple compression strategies
- Compression metrics

**Usage**:
```python
from core import ContextCompressor

compressor = ContextCompressor(
    max_tokens=2000,
    strategy='score_based'
)

compressed = compressor.compress(
    aggregated_context,
    preserve_recent=True
)
```

---

### 5. Response Synthesizer (`core/synthesizer.py`)

**Purpose**: Format and synthesize final responses.

**Input**: Raw LLM response, context metadata, query info

**Output**: Synthesized response
```json
{
  "response": "formatted response text",
  "raw_response": "...",
  "format": "markdown",
  "timestamp": "2024-01-01T00:00:00",
  "context_info": {
    "total_tokens": 450,
    "compression_ratio": 0.65,
    "items_used": 5
  },
  "query_info": {
    "intent": "debug",
    "keywords": ["bug", "fix"]
  }
}
```

**Features**:
- Multiple output formats (markdown, JSON, plain)
- Post-processing (whitespace cleanup)
- Citation support
- Error handling
- Metadata injection

**Usage**:
```python
from core import ResponseSynthesizer

synthesizer = ResponseSynthesizer(output_format='markdown')

response_dict = synthesizer.synthesize(
    raw_response="Here's the answer...",
    context_metadata=compressed_context,
    query_info=query_obj
)
```

---

### 6. Memory Orchestrator (`core/orchestrator.py`)

**Purpose**: Orchestrate the entire workflow.

**Enhanced Features**:
- Manages all memory layers
- Integrates preprocessor, aggregator, compressor
- Provides unified interface for context retrieval
- Auto-summarization of STM to MTM
- Embedding-based retrieval

**Key Methods**:

```python
orchestrator = MemoryOrchestrator(
    short_term=stm,
    mid_term=mtm,
    long_term=ltm,
    summarizer=summarizer,
    preprocessor=preprocessor,
    aggregator=aggregator,
    compressor=compressor,
    summarize_every=5
)

# Add message (auto-summarizes when threshold reached)
orchestrator.add_message('user', 'Hello', embedding=[...])

# Get context with advanced workflow
context = orchestrator.get_context(
    query="debug my code",
    use_embedding_search=True
)

# Get formatted context string
context_string = orchestrator.get_context_string(
    query="debug my code",
    use_compression=True
)
```

---

### 7. ChatBot (`bot/chatbot.py`)

**Enhanced Features**:
- Advanced workflow mode
- Embedding-based context retrieval
- Response synthesis integration
- Query preprocessing
- Intent detection

**Usage**:

```python
from bot import ChatBot

chatbot = ChatBot(
    orchestrator=orchestrator,
    response_generator=response_gen,
    synthesizer=synthesizer,
    use_advanced_workflow=True
)

# Chat with embedding search
response = chatbot.chat(
    "Help me debug this code",
    use_embedding_search=True
)
```

---

## Complete Workflow Example

```python
from config import get_config
from main import create_chatbot

# Create chatbot with advanced workflow
config = get_config()
chatbot = create_chatbot(config, use_advanced_workflow=True)

# Start conversation
print(chatbot.start())

# User query
user_message = "Find bug in my Python code"

# Process (complete workflow):
# 1. Preprocess input → embedding + intent
# 2. Retrieve from memory layers (embedding search)
# 3. Aggregate contexts with ranking
# 4. Compress to fit token budget
# 5. Generate response with context
# 6. Synthesize and format output
response = chatbot.chat(user_message, use_embedding_search=True)

print(response)
```

---

## Workflow Diagram

```
[User Input]
     ↓
[InputPreprocessor] ──→ {embedding, intent, keywords}
     ↓
[Memory Orchestrator]
     ├─→ [ShortTermMemory] ──→ embedding search
     ├─→ [MidTermMemory]   ──→ embedding search
     └─→ [LongTermMemory]  ──→ semantic search
     ↓
[MemoryAggregator] ──→ {ranked, merged contexts}
     ↓
[ContextCompressor] ──→ {compressed, fitted to token budget}
     ↓
[ResponseGenerator] ──→ {raw response}
     ↓
[ResponseSynthesizer] ──→ {formatted response + metadata}
     ↓
[Final Output to User]
```

---

## Configuration

All workflow components can be configured in `main.py`:

```python
# Embedding dimension
preprocessor = InputPreprocessor(embedding_dim=384)

# Memory layer weights
aggregator = MemoryAggregator(
    stm_weight=0.5,  # Short-term importance
    mtm_weight=0.3,  # Mid-term importance
    ltm_weight=0.2   # Long-term importance
)

# Token budget
compressor = ContextCompressor(
    max_tokens=2000,
    strategy='score_based'
)

# Output format
synthesizer = ResponseSynthesizer(output_format='markdown')
```

---

## Testing

Run the workflow demos:

```bash
# Simple tests
python test_simple.py

# Complete workflow demo
python demo_workflow.py

# Interactive chatbot
python main.py
```

---

## Future Enhancements

1. **Real Embedding Models**
   - Integrate sentence-transformers
   - OpenAI embedding API
   - Custom fine-tuned models

2. **Vector Databases**
   - ChromaDB integration
   - Pinecone for production scale
   - FAISS for local deployment

3. **Graph Databases**
   - Neo4j for relationship mapping
   - AST-based code navigation
   - Dependency graphs

4. **Advanced Compression**
   - MMR algorithm implementation
   - Attention-based compression
   - Learned compression models

5. **LLM Integration**
   - OpenAI GPT integration
   - Anthropic Claude support
   - Local LLMs (Llama, Mistral)

---

## References

- Original workflow specification: `memory_layer_workflow.md`
- Configuration: `config.py`
- Main entry point: `main.py`
