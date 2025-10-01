# 📊 Evaluation Tools Guide

Complete guide for evaluating and tuning Memory Layer parameters.

---

## 🎯 Overview

The evaluation suite helps you:
- **Measure** retrieval quality & compression efficiency
- **Tune** parameters for optimal performance
- **Compare** different configurations
- **Prepare** for production deployment

---

## 🛠️ Tools

### 1. `evaluate_memory.py` - Full Evaluation

**Purpose:** Comprehensive assessment of memory layer performance

**Usage:**
```bash
python3 evaluate_memory.py
```

**What it measures:**
- ✅ Retrieval quality (Precision, Recall, F1)
- ✅ Source coverage (STM, MTM, LTM usage)
- ✅ Context compression efficiency
- ✅ Query latency
- ✅ Token usage

**Output:**
```
📊 SUMMARY
Avg F1 Score:      0.850
Avg Precision:     0.867
Avg Recall:        0.833
Source Coverage:   0.900
Avg Latency:       45.23ms
Tests Passed:      5/5
Compression:       62.3% savings
Grade:             🟢 EXCELLENT
```

**Report:** `evaluation_report_YYYYMMDD_HHMMSS.json`

---

### 2. `tune_parameters.py` - Parameter Optimization

**Purpose:** Find optimal parameter values automatically

**Usage:**
```bash
# Grid search (recommended)
python3 tune_parameters.py grid

# Tune specific parameter
python3 tune_parameters.py stm    # Tune STM size
python3 tune_parameters.py mtm    # Tune MTM size
python3 tune_parameters.py topk   # Tune top_k
```

**Grid Search:**
Tests combinations of:
- STM size: 5, 10, 15
- MTM size: 10, 20, 30
- top_k: 2, 3, 5

Total: 27 configurations

**Output:**
```
📊 TUNING RESULTS
Best Config:
  - STM size: 10
  - MTM size: 20
  - top_k: 3
  - F1 Score: 0.875

Top 5 configurations:
1. STM=10, MTM=20, top_k=3 → F1=0.875
2. STM=15, MTM=20, top_k=3 → F1=0.867
3. STM=10, MTM=30, top_k=3 → F1=0.858
...
```

**Report:** `tuning_report_YYYYMMDD_HHMMSS.json`

---

### 3. `compare_configs.py` - Config Comparison

**Purpose:** A/B test multiple configurations side-by-side

**Usage:**
```bash
# Compare preset configs
python3 compare_configs.py preset

# Compare custom configs (edit script)
python3 compare_configs.py
```

**Preset Configs:**
- **Minimal**: Low memory (STM=5, MTM=10, top_k=2)
- **Balanced**: Default (STM=10, MTM=20, top_k=3)
- **Quality**: High recall (STM=15, MTM=30, top_k=5)
- **Performance**: Low latency (STM=5, MTM=15, top_k=2)

**Output:**
```
📊 COMPARISON TABLE
Metric                    Config 1     Config 2     Config 3
--------------------------------------------------------------
F1 Score                  0.750        0.850        0.883
Precision                 0.783        0.867        0.900
Recall                    0.717        0.833        0.867
Source Coverage           0.867        0.900        0.933
Pass Rate                 80.00%       100.00%      100.00%
Avg Latency (ms)          32.50        45.23        67.89
Compression Ratio         0.420        0.377        0.310
Token Savings %           58.0         62.3         69.0

💡 RECOMMENDATION
🏆 Best F1 Score: Config 3
⚡ Fastest: Config 1
💾 Best Compression: Config 3
🎯 Best Overall: Config 2
```

**Report:** `comparison_report_YYYYMMDD_HHMMSS.json`

---

## 📋 Evaluation Metrics Explained

### Retrieval Quality

**Precision:**
```
Precision = Found Relevant / Total Retrieved
```
- How many retrieved items are actually relevant?
- Higher = Less noise
- Target: ≥ 0.8

**Recall:**
```
Recall = Found Relevant / Total Relevant
```
- How many relevant items did we find?
- Higher = Better coverage
- Target: ≥ 0.7

**F1 Score:**
```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```
- Balanced measure
- Main metric for optimization
- Target: ≥ 0.75

**Source Coverage:**
```
Coverage = Layers Used / Expected Layers
```
- Are all memory layers utilized?
- Shows multi-layer integration
- Target: ≥ 0.8

### Context Compression

**Compression Ratio:**
```
Ratio = Compressed Tokens / Original Tokens
```
- Lower = More compression
- Typical: 0.3 - 0.5 (50-70% savings)

**Token Savings:**
```
Savings % = (1 - Compression Ratio) * 100
```
- How much context reduced?
- Target: ≥ 40%

### Performance

**Latency:**
- Time to retrieve memories
- Target: ≤ 100ms (production)
- Optimal: ≤ 50ms

**Pass Rate:**
```
Pass Rate = Tests Passed / Total Tests
```
- Tests meeting minimum relevance
- Target: ≥ 80%

---

## 🎯 Tuning Workflow

### Step 1: Baseline Evaluation
```bash
python3 evaluate_memory.py
```

Review metrics:
- Is F1 score acceptable (≥ 0.75)?
- Is latency acceptable (≤ 100ms)?
- Is compression good (≥ 40%)?

### Step 2: Identify Issues

**Low F1 Score (<0.75):**
- Increase `top_k` → More results
- Increase memory sizes → More context

**High Latency (>100ms):**
- Decrease memory sizes → Less to search
- Decrease `top_k` → Fewer comparisons

**Poor Compression (<40%):**
- Decrease STM size → Less raw data
- Tune MTM summarization

### Step 3: Grid Search
```bash
python3 tune_parameters.py grid
```

Let it find optimal combination automatically.

### Step 4: Compare Top Configs
```bash
python3 compare_configs.py
```

Edit script to compare top 3 configs from grid search.

### Step 5: Validate
```bash
python3 test_code_analysis.py
```

Test with real queries to ensure quality.

---

## 📊 Interpreting Results

### Excellent Performance
```
✅ F1 ≥ 0.85
✅ Latency ≤ 50ms
✅ Compression ≥ 60%
✅ Pass Rate 100%
→ Grade: 🟢 EXCELLENT
```

### Good Performance
```
✅ F1 ≥ 0.70
✅ Latency ≤ 80ms
✅ Compression ≥ 50%
✅ Pass Rate ≥ 80%
→ Grade: 🟡 GOOD
```

### Needs Improvement
```
⚠️  F1 < 0.60
⚠️  Latency > 100ms
⚠️  Compression < 40%
⚠️  Pass Rate < 70%
→ Grade: 🔴 NEEDS IMPROVEMENT
```

---

## 🔧 Common Tuning Scenarios

### Scenario 1: Low Memory Environment

**Goal:** Minimize memory footprint

**Config:**
```python
{
    'stm_max_items': 5,
    'mtm_max_chunks': 10,
    'top_k': 2
}
```

**Expected:**
- F1: ~0.70
- Latency: <40ms
- Memory: Low

### Scenario 2: High Quality Requirements

**Goal:** Maximum recall, F1 > 0.85

**Config:**
```python
{
    'stm_max_items': 15,
    'mtm_max_chunks': 30,
    'top_k': 5
}
```

**Expected:**
- F1: ~0.85+
- Latency: ~70ms
- Memory: High

### Scenario 3: Balanced (Default)

**Goal:** Good balance of all metrics

**Config:**
```python
{
    'stm_max_items': 10,
    'mtm_max_chunks': 20,
    'top_k': 3
}
```

**Expected:**
- F1: ~0.80
- Latency: ~50ms
- Memory: Medium

### Scenario 4: Low Latency

**Goal:** Minimize response time

**Config:**
```python
{
    'stm_max_items': 5,
    'mtm_max_chunks': 15,
    'top_k': 2
}
```

**Expected:**
- F1: ~0.72
- Latency: <35ms
- Memory: Low

---

## 📈 Tracking Improvements

### Baseline → Tuned Example

**Before (Default):**
```
F1 Score:      0.722
Latency:       52.34ms
Compression:   57.8%
Pass Rate:     60%
```

**After (Tuned):**
```
F1 Score:      0.850  (+17.7%)
Latency:       45.23ms (-13.6%)
Compression:   62.3%  (+7.8%)
Pass Rate:     100%   (+66.7%)
```

**Config Change:**
- STM: 10 → 10 (no change)
- MTM: 20 → 20 (no change)
- top_k: 2 → 3 (+1)

**Lesson:** Small parameter changes can have big impact!

---

## 🚀 Quick Reference

```bash
# Full evaluation
python3 evaluate_memory.py

# Find best config
python3 tune_parameters.py grid

# Compare configs
python3 compare_configs.py preset

# Test with queries
python3 test_code_analysis.py

# Check integration
python3 check_integration.py

# Generate fresh data
python3 generate_data.py

# Validate schemas
python3 utils/schema_validator.py
```

---

## 📝 Reports Generated

All tools generate timestamped JSON reports:

```
evaluation_report_20251001_142530.json
tuning_report_20251001_143015.json
comparison_report_20251001_143245.json
```

**Use these for:**
- Tracking improvements over time
- Comparing different data sets
- Documentation & audits
- Production deployment decisions

---

## 🎯 Production Readiness

### Minimum Requirements
- ✅ F1 Score: ≥ 0.70
- ✅ Latency: ≤ 100ms
- ✅ Compression: ≥ 40%
- ✅ Pass Rate: ≥ 80%

### Checklist
- [ ] Run full evaluation
- [ ] Tune parameters
- [ ] Compare top configs
- [ ] Validate with real queries
- [ ] Document chosen config
- [ ] Save evaluation reports

### Deploy When:
- All metrics meet minimum requirements
- Config validated with real-world queries
- Reports archived for reference

---

**Status:** ✅ Evaluation Suite Complete  
**Next:** Run evaluations and tune for your domain  
**Goal:** Production-ready configuration for Innocody
