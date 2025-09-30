# 🎨 UI & Evaluation Guide

## 🎉 Features Mới Đã Thêm!

### 1. Web UI (Gradio) ✨
- **Clean chat interface** - Giao diện đẹp, dễ dùng
- **Real-time pipeline logging** - Xem từng bước xử lý
- **Memory status** - Monitor STM, MTM, LTM
- **Live metrics** - Performance tracking

### 2. Evaluation Framework 📊
- **Context retrieval quality** - Precision, Recall, F1
- **Compression effectiveness** - Ratio, efficiency  
- **Memory recall accuracy** - Test với queries
- **Response quality** - Metrics đa chiều

### 3. Metrics Collection 📈
- **Query-level metrics** - Track mỗi query
- **Session statistics** - Tổng hợp performance
- **Trend analysis** - Xem performance over time
- **Intent breakdown** - Phân tích intent distribution

---

## 🚀 Quick Start

### 1. Launch Web UI

```bash
source .venv/bin/activate
export OPENAI_API_KEY='your-key'
python ui_chat.py
```

**Access:** http://localhost:7860

**Features:**
- 💬 Chat interface - Gõ và chat như normal
- 📊 Pipeline Log - See real-time processing
- 💾 Memory Status - STM/MTM/LTM usage
- 📈 Metrics - Performance stats

### 2. Run Evaluation

```python
from evaluation import MemoryEvaluator

evaluator = MemoryEvaluator()

test_cases = [
    {
        'query': 'Your query',
        'retrieved_items': [...],  # Retrieved context
        'ground_truth_items': [...],  # Expected context
        'original_items': [...],  # Before compression
        'compressed_items': [...],  # After compression
        'response': '...',  # Generated response
        'context': '...',  # Context used
    }
]

results = evaluator.run_evaluation_suite(test_cases)
print(evaluator.generate_report(results))
```

### 3. Collect Metrics

```python
from evaluation import MetricsCollector, QueryMetrics

collector = MetricsCollector()

# Record each query
metrics = QueryMetrics(
    timestamp=datetime.now().isoformat(),
    query="user query",
    intent="general",
    stm_hits=3,
    mtm_hits=2,
    ltm_hits=0,
    total_retrieved=5,
    original_items=10,
    compressed_items=5,
    compression_ratio=0.5,
    preprocessing_time=0.1,
    retrieval_time=0.2,
    generation_time=1.0,
    total_time=1.3,
    response_length=150,
    context_utilization=0.7
)
collector.record_query(metrics)

# Generate report
print(collector.generate_report())

# Save metrics
collector.save('metrics.json')
```

---

## 📊 Evaluation Metrics Explained

### 1. Context Retrieval Quality

**Precision**: Relevant retrieved / Total retrieved
- Cao → Ít noise trong retrieved context
- 0.8+ là tốt

**Recall**: Relevant retrieved / Total relevant  
- Cao → Không miss important context
- 0.7+ là tốt

**F1 Score**: Harmonic mean of precision & recall
- Balance giữa precision và recall
- 0.75+ là tốt

**Example:**
```python
{
    'precision': 0.80,  # 80% retrieved là relevant
    'recall': 0.75,     # 75% relevant được retrieved
    'f1': 0.77,         # Good balance
}
```

### 2. Compression Effectiveness

**Compression Ratio**: Compressed / Original
- Thấp → Compression hiệu quả
- 0.3-0.5 là ideal

**Token Reduction**: Compressed tokens / Original tokens
- Measure token savings
- 0.4-0.6 là tốt

**Word Retention**: Important words kept
- Cao → Ít mất information
- 0.7+ là tốt

**Efficiency Score**: (1 - token_ratio) × word_retention
- Higher is better
- Combines savings và quality

**Example:**
```python
{
    'compression_ratio': 0.40,      # 40% items kept
    'token_reduction': 0.45,        # 55% tokens saved
    'word_retention': 0.80,         # 80% important words kept
    'efficiency_score': 0.44,       # Good efficiency
}
```

### 3. Memory Recall

**Average Recall**: Across test queries
- Test if memory remembers past info
- 0.6+ là acceptable

**Example Test:**
```python
test_queries = [
    {
        'query': 'What did we discuss about login?',
        'expected_keywords': ['login_user', 'authentication', 'JWT']
    }
]
```

### 4. Response Quality

**Context Utilization**: Context words in response
- Cao → Response uses context well
- 0.5+ là tốt

**Query Coverage**: Query keywords in response  
- Cao → Response addresses query
- 0.6+ là tốt

**Response Length**: Characters/words
- Monitor verbosity
- Adjust based on needs

**Example:**
```python
{
    'response_length': 250,
    'word_count': 45,
    'context_utilization': 0.65,  # 65% context used
    'query_coverage': 0.75,       # 75% query addressed
}
```

---

## 🎯 Interpreting Results

### Good Performance Indicators

**Context Retrieval:**
- ✅ Precision > 0.75
- ✅ Recall > 0.70
- ✅ F1 > 0.72

**Compression:**
- ✅ Compression ratio: 0.3-0.5
- ✅ Token reduction: 0.4-0.6  
- ✅ Word retention: > 0.70
- ✅ Efficiency score: > 0.40

**Performance:**
- ✅ Avg response time: < 2s
- ✅ Retrieval time: < 0.5s
- ✅ Generation time: < 1.5s

**Quality:**
- ✅ Context utilization: > 0.50
- ✅ Query coverage: > 0.60

### Red Flags 🚨

**Poor Retrieval:**
- ❌ Precision < 0.50 → Too much noise
- ❌ Recall < 0.40 → Missing important context
- ❌ F1 < 0.45 → Overall poor retrieval

**Bad Compression:**
- ❌ Compression ratio > 0.70 → Not compressing enough
- ❌ Word retention < 0.50 → Losing too much info
- ❌ Efficiency < 0.30 → Not effective

**Slow Performance:**
- ❌ Response time > 5s → Too slow
- ❌ Retrieval > 1s → Memory inefficient  
- ❌ Generation > 3s → LLM bottleneck

---

## 🔧 How to Improve

### If Retrieval is Poor:

1. **Add more data** to memory layers
2. **Improve embeddings** - Use real embeddings
3. **Tune similarity threshold**
4. **Better keyword extraction**

### If Compression is Bad:

1. **Adjust token budget** in config
2. **Improve summarization** algorithm
3. **Better deduplication** logic
4. **Prioritize recent items**

### If Response is Slow:

1. **Use faster LLM** (GPT-3.5 instead of GPT-4)
2. **Reduce max_tokens**
3. **Cache embeddings**
4. **Optimize memory retrieval**

### If Quality is Low:

1. **Better system prompts**
2. **More relevant context**
3. **Fine-tune LLM parameters**
4. **Improve context formatting**

---

## 📈 Monitoring in Production

### 1. Real-time Dashboard

Use Web UI to monitor:
- Live memory status
- Pipeline logs per query
- Metrics updates

### 2. Periodic Evaluation

Run evaluation suite regularly:
```bash
# Weekly evaluation
python -m evaluation.evaluator
```

### 3. Metrics Collection

Collect and analyze trends:
```python
# Load historical metrics
collector.load('metrics_history.json')

# Analyze trends
trends = collector.get_performance_trends()

# Check for degradation
if trends['response_times'][-10:].mean() > threshold:
    alert("Performance degraded!")
```

### 4. A/B Testing

Compare configurations:
```python
# Config A
results_a = run_with_config(config_a)

# Config B  
results_b = run_with_config(config_b)

# Compare
compare_evaluations(results_a, results_b)
```

---

## 🎬 Complete Example

```python
#!/usr/bin/env python3
"""Complete monitoring example."""

from evaluation import MemoryEvaluator, MetricsCollector, QueryMetrics
from datetime import datetime

# Initialize
evaluator = MemoryEvaluator()
collector = MetricsCollector()

# Simulate queries
for query in test_queries:
    start = datetime.now()
    
    # Process query
    result = chatbot.process(query)
    
    # Record metrics
    metrics = QueryMetrics(
        timestamp=datetime.now().isoformat(),
        query=query,
        intent=result['intent'],
        stm_hits=result['stm_count'],
        mtm_hits=result['mtm_count'],
        ltm_hits=0,
        total_retrieved=result['total'],
        original_items=result['original'],
        compressed_items=result['compressed'],
        compression_ratio=result['compressed']/result['original'],
        preprocessing_time=result['preprocess_time'],
        retrieval_time=result['retrieval_time'],
        generation_time=result['generation_time'],
        total_time=(datetime.now() - start).total_seconds(),
        response_length=len(result['response']),
        context_utilization=result['context_util']
    )
    collector.record_query(metrics)

# Generate reports
print("\n=== METRICS REPORT ===")
print(collector.generate_report())

# Save results
collector.save('session_metrics.json')

print("\n✅ Monitoring complete!")
```

---

## 🔗 Files Created

1. **`ui_chat.py`** - Web UI with Gradio
2. **`evaluation/evaluator.py`** - Evaluation framework
3. **`evaluation/metrics.py`** - Metrics collection
4. **`evaluation/__init__.py`** - Module exports

---

## 💡 Tips

### UI Best Practices
- Keep pipeline log open to debug
- Monitor memory status regularly
- Check metrics after each session
- Clear memory when testing

### Evaluation Best Practices
- Create diverse test cases
- Test edge cases
- Run regularly (weekly/monthly)
- Track trends over time

### Metrics Best Practices
- Record every query
- Save to files regularly
- Analyze trends
- Set alerts for degradation

---

## 🎊 Summary

Bây giờ bạn có:

✅ **Web UI** - Chat dễ dàng, monitor real-time  
✅ **Evaluation** - Measure quality objectively  
✅ **Metrics** - Track performance over time  
✅ **Monitoring** - Know when something breaks

**Start using:**
```bash
python ui_chat.py  # Launch UI
```

---

**Date:** 2025-09-30  
**Status:** ✅ Complete  
**Ready:** ✅ Production Monitoring Ready
