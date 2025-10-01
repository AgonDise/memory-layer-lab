# 📊 Langfuse Setup Guide - Tracing & Observability

**Goal:** Add Langfuse tracing to Memory Layer Lab for monitoring and debugging

---

## 🎯 What is Langfuse?

**Langfuse** is an open-source observability platform for LLM applications that provides:
- 📊 **Tracing** - Track every LLM call and operation
- 📈 **Analytics** - Monitor performance and costs
- 🐛 **Debugging** - Find and fix issues quickly
- 💰 **Cost tracking** - Monitor API usage and costs
- 👥 **User feedback** - Collect and analyze user ratings

**Official site:** https://langfuse.com

---

## 🚀 Quick Start (5 minutes)

### Step 1: Get Langfuse Account

**Option A: Langfuse Cloud (Recommended)**
```bash
# 1. Sign up at https://cloud.langfuse.com
# 2. Create a new project
# 3. Copy your API keys
```

**Option B: Self-hosted**
```bash
# Run Langfuse locally with Docker
docker run -d \
  --name langfuse \
  -p 3000:3000 \
  -e DATABASE_URL="postgresql://..." \
  langfuse/langfuse:latest

# Access at http://localhost:3000
```

---

### Step 2: Install Dependencies

```bash
pip install langfuse
```

---

### Step 3: Configure

Copy config template:
```bash
cp config/langfuse_config.yaml.example config/langfuse_config.yaml
```

Edit `config/langfuse_config.yaml`:
```yaml
langfuse:
  public_key: "pk-lf-..."        # Your public key
  secret_key: "sk-lf-..."        # Your secret key
  host: "https://cloud.langfuse.com"
  enabled: true
  debug: false
  sample_rate: 1.0              # Trace 100% of requests
  environment: "development"
```

---

### Step 4: Test

```bash
python3 examples/langfuse_example.py
```

**Expected output:**
```
╔══════════════════════════════════════════════════════════════════════════╗
║                    LANGFUSE INTEGRATION EXAMPLES                         ║
╚══════════════════════════════════════════════════════════════════════════╝

📊 Example 1: Basic Tracing
✅ Created trace
✅ Logged event
✅ Flushed to Langfuse

🤖 Example 2: LLM Call Tracing
📝 Prompt: What is the capital of France?
💬 Response: This is a response to: What is the capital of France?
✅ LLM call traced

... (more examples)

🎉 All examples completed!
```

---

### Step 5: Check Dashboard

1. Go to https://cloud.langfuse.com (or your self-hosted URL)
2. Navigate to your project
3. Click on "Traces"
4. See your traced operations! 🎉

---

## 📖 Usage Examples

### Basic Usage

```python
from utils.langfuse_client import create_langfuse_client

# Create client
client = create_langfuse_client()

# Create trace
trace = client.create_trace(
    name="user_conversation",
    user_id="user_123",
    session_id="session_456"
)

# Log an event
client.log_event(
    trace_id=trace.id,
    name="message_received",
    metadata={"message": "Hello!"}
)

# Flush to Langfuse
client.flush()
```

---

### Trace LLM Calls

```python
from utils.langfuse_client import create_langfuse_client, LangfuseTracer

client = create_langfuse_client()
tracer = LangfuseTracer(client)

# Decorate your LLM function
@tracer.trace_llm_call(model="gpt-4")
def generate_response(prompt: str) -> str:
    return llm.generate(prompt)

# Use it normally - tracing happens automatically
response = generate_response("What is AI?")
```

---

### Trace Memory Operations

```python
@tracer.trace_operation(name="memory_retrieval")
def retrieve_context(query: str):
    # Your memory retrieval logic
    stm_items = stm.search(query)
    mtm_items = mtm.search(query)
    return {"stm": stm_items, "mtm": mtm_items}

# Traced automatically
context = retrieve_context("machine learning")
```

---

### Trace Full Pipeline

```python
with tracer.trace_context("full_pipeline"):
    # Preprocess
    query_obj = preprocessor.preprocess(user_input)
    
    # Retrieve context
    context = orchestrator.get_context(query_obj)
    
    # Generate response
    response = response_generator.generate(context)
    
    # All traced automatically!
```

---

## 🔧 Configuration Options

### Full Configuration

```yaml
langfuse:
  # Credentials
  public_key: "pk-lf-..."
  secret_key: "sk-lf-..."
  host: "https://cloud.langfuse.com"
  
  # Control
  enabled: true
  debug: false
  sample_rate: 1.0              # 0.0 to 1.0
  
  # Performance
  flush_at: 15                  # Flush after N events
  flush_interval: 1.0           # Flush every N seconds
  
  # Metadata
  release: "v1.0"
  environment: "development"    # development, staging, production
  
  # Tracing options
  trace_llm_calls: true
  trace_embeddings: true
  trace_retrievals: true
  trace_full_pipeline: true
  
  # Privacy
  mask_user_content: false      # Mask user messages
  mask_api_keys: true          # Mask API keys
```

---

### Environment-Specific Configs

**Development:**
```yaml
langfuse:
  enabled: true
  debug: true
  sample_rate: 1.0              # Trace everything
  environment: "development"
```

**Staging:**
```yaml
langfuse:
  enabled: true
  debug: false
  sample_rate: 0.5              # Trace 50%
  environment: "staging"
```

**Production:**
```yaml
langfuse:
  enabled: true
  debug: false
  sample_rate: 0.1              # Trace 10%
  environment: "production"
  mask_user_content: true       # Privacy!
```

---

## 📊 What Gets Traced?

### Automatic Tracing

With Langfuse integrated, you'll see:

1. **LLM Calls**
   - Model used
   - Input prompt
   - Generated output
   - Token usage
   - Latency
   - Cost (if available)

2. **Memory Operations**
   - Query text
   - Retrieved items count
   - Relevance scores
   - Retrieval time

3. **Full Pipeline**
   - User input
   - Preprocessing steps
   - Context aggregation
   - Response generation
   - Post-processing
   - Total latency

4. **Errors & Exceptions**
   - Error type
   - Stack trace
   - Context when error occurred

---

## 📈 Dashboard Features

### Traces View
- See all traces in real-time
- Filter by user, session, tags
- Sort by latency, cost, errors
- Click to see detailed breakdown

### Analytics
- Token usage over time
- Cost per user/session
- Latency percentiles (p50, p95, p99)
- Error rates

### Debugging
- View full trace tree
- See input/output at each step
- Identify bottlenecks
- Find errors quickly

---

## 🎯 Best Practices

### 1. Use Meaningful Names
```python
# Good
trace = client.create_trace(name="user_question_answering")

# Bad
trace = client.create_trace(name="trace1")
```

### 2. Add Rich Metadata
```python
trace = client.create_trace(
    name="conversation",
    metadata={
        "user_tier": "premium",
        "feature_flags": ["semantic_search", "ltm"],
        "model_version": "v2.1"
    }
)
```

### 3. Tag Appropriately
```python
trace = client.create_trace(
    name="conversation",
    tags=["production", "critical", "premium_user"]
)
```

### 4. Sample in Production
```yaml
# Don't trace everything in production
sample_rate: 0.1  # 10% is often enough
```

### 5. Flush Regularly
```python
# After each request/conversation
client.flush()
```

---

## 🔐 Security & Privacy

### Sensitive Data

**Mask user content in production:**
```yaml
langfuse:
  mask_user_content: true
  mask_api_keys: true
```

**Or mask specific fields:**
```python
# Instead of logging actual content
client.log_event(
    name="user_message",
    metadata={
        "content": mask_pii(user_message),  # Your masking function
        "length": len(user_message)
    }
)
```

---

### API Keys

**Never log API keys:**
```python
# Bad
metadata = {"api_key": openai_key}

# Good  
metadata = {"api_key": "***masked***"}
```

---

## 🐛 Troubleshooting

### Issue 1: Traces Not Appearing

**Check:**
1. Is Langfuse enabled?
   ```yaml
   enabled: true
   ```

2. Are credentials correct?
   ```bash
   # Test with curl
   curl -X POST https://cloud.langfuse.com/api/public/traces \
     -H "Authorization: Bearer pk-lf-..." \
     -H "Content-Type: application/json"
   ```

3. Did you flush?
   ```python
   client.flush()
   ```

---

### Issue 2: High Latency

**Solutions:**
1. Increase flush interval:
   ```yaml
   flush_interval: 5.0  # Flush every 5s instead of 1s
   ```

2. Increase flush threshold:
   ```yaml
   flush_at: 50  # Flush after 50 events instead of 15
   ```

3. Use sampling:
   ```yaml
   sample_rate: 0.1  # Only trace 10%
   ```

---

### Issue 3: Too Many Traces

**Solution:** Use sampling
```yaml
# Production
sample_rate: 0.1  # 10% of requests

# Or conditional sampling
```

```python
import random

def should_trace(user_id):
    # Always trace premium users
    if is_premium(user_id):
        return True
    # Sample 10% of free users
    return random.random() < 0.1
```

---

## 📚 Advanced Features

### Custom Scores

Add custom metrics to traces:
```python
trace.score(
    name="user_satisfaction",
    value=0.95,  # 0 to 1
    comment="User gave 5 stars"
)
```

### User Feedback

Collect user feedback:
```python
trace.update(
    metadata={
        "user_feedback": "helpful",
        "user_rating": 5
    }
)
```

### Experiments

A/B testing:
```python
trace = client.create_trace(
    name="conversation",
    metadata={
        "experiment": "model_comparison",
        "variant": "gpt-4"  # or "claude-3"
    }
)
```

---

## 🔗 Integration with Existing Code

### Minimal Integration

Just add tracing to critical paths:

```python
# In orchestrator.py
from utils.langfuse_client import create_langfuse_client, LangfuseTracer

class MemoryOrchestrator:
    def __init__(self, ...):
        # ... existing code ...
        self.langfuse = create_langfuse_client()
        self.tracer = LangfuseTracer(self.langfuse)
    
    def get_context(self, query):
        with self.tracer.trace_context("get_context"):
            # ... existing code ...
            return context
```

---

### Full Integration

Trace everything (see integration examples in repository)

---

## 📊 Monitoring Checklist

- [ ] Langfuse account created
- [ ] API keys configured
- [ ] Dependencies installed
- [ ] Configuration tested
- [ ] Examples run successfully
- [ ] Integration added to code
- [ ] Dashboard explored
- [ ] Alerts configured (optional)
- [ ] Team access granted (optional)

---

## 🎉 You're Ready!

**Next steps:**
1. Start tracing your application
2. Monitor performance in dashboard
3. Set up alerts for errors/latency
4. Use insights to optimize

**Resources:**
- Langfuse Docs: https://langfuse.com/docs
- Dashboard: https://cloud.langfuse.com
- Examples: `examples/langfuse_example.py`
- Support: https://langfuse.com/discord

---

## 💡 Tips

1. **Start small** - Add tracing to one endpoint first
2. **Use sampling** - Don't trace everything in production
3. **Add metadata** - Rich metadata = better insights
4. **Monitor costs** - Especially for LLM calls
5. **Set up alerts** - Get notified of issues
6. **Review regularly** - Check dashboard weekly

**Happy tracing! 📊🚀**
