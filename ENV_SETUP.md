# 🔐 Environment Setup Guide

Quick guide for setting up Neo4j and OpenAI API credentials.

---

## 📋 Quick Setup

### 1. Create `.env` File

```bash
# Copy example
cp .env.example .env

# Edit with your credentials
nano .env
```

### 2. Configure Neo4j

**Option A: Local Neo4j Server**
```bash
NEO4J_URI=bolt://192.168.2.46:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

**Option B: Neo4j Aura (Cloud)**
```bash
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_aura_password
NEO4J_DATABASE=neo4j
```

### 3. Configure OpenAI

```bash
OPENAI_API_KEY=sk-proj-your_api_key_here
MODEL_NAME=gpt-4-turbo-preview
```

### 4. Test Connections

```bash
python3 utils/env_loader.py
```

Expected output:
```
✅ Configuration loaded:
  Neo4j URI: bolt://192.168.2.46:7687
  Neo4j User: neo4j
  Neo4j DB: neo4j
  Neo4j Timeout: 120s
  Model: gpt-4-turbo-preview
  OpenAI API: ✅ Set
```

---

## 🔧 Configuration Options

### Neo4j Settings

```bash
# Connection
NEO4J_URI=bolt://localhost:7687    # Server address
NEO4J_USER=neo4j                    # Username
NEO4J_PASSWORD=password             # Password
NEO4J_DATABASE=neo4j                # Database name

# Timeouts (optional)
NEO4J_TIMEOUT=120                            # Query timeout (seconds)
NEO4J_MAX_CONNECTION_LIFETIME=3600           # Connection lifetime
NEO4J_CONNECTION_ACQUISITION_TIMEOUT=120     # Acquisition timeout
NEO4J_MAX_TRANSACTION_RETRY_TIME=30         # Retry timeout
```

### OpenAI Settings

```bash
OPENAI_API_KEY=sk-proj-...          # API key (required)
MODEL_NAME=gpt-4-turbo-preview      # Model to use
OPENAI_API_BASE=https://api.openai.com/v1   # API endpoint
```

---

## 📝 Usage in Code

### Load Configuration

```python
from utils.env_loader import get_config

config = get_config()
print(config.neo4j_uri)      # bolt://192.168.2.46:7687
print(config.model_name)      # gpt-4-turbo-preview
```

### Create Neo4j Manager

```python
from utils.neo4j_manager import create_neo4j_manager_from_env

# Auto-loads from .env
manager = create_neo4j_manager_from_env()
manager.connect()

# Use manager
result = manager.execute_read("MATCH (n) RETURN count(n) as count")
print(result)

manager.disconnect()
```

### Use OpenAI Client

```python
from utils.env_loader import get_config
import openai

config = get_config()
openai.api_key = config.openai_api_key

response = openai.chat.completions.create(
    model=config.model_name,
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

## 🔒 Security Best Practices

### 1. Never Commit `.env`

✅ `.env` is already in `.gitignore`

```bash
# Check
cat .gitignore | grep .env
```

### 2. Use Strong Passwords

- Neo4j: 12+ characters, mix of letters/numbers/symbols
- API Keys: Keep secret, rotate regularly

### 3. Restrict Access

- Neo4j: Use firewall rules
- API Keys: Set usage limits

### 4. Environment-Specific Configs

```bash
.env              # Local development
.env.staging      # Staging environment
.env.production   # Production (never commit!)
```

---

## 🧪 Testing

### Test Environment Load

```bash
python3 utils/env_loader.py
```

### Test Neo4j Connection

```bash
python3 test_connections.py
```

Expected:
```
1️⃣ Testing Neo4j Connection...
   URI: bolt://192.168.2.46:7687
   Connecting...
   ✅ Connected successfully!
   ✅ Test query successful!
   ✅ Neo4j version: 5.x.x
   ✅ Disconnected

2️⃣ Testing OpenAI API Connection...
   ✅ Response: test successful
   ✅ OpenAI API working!

📊 SUMMARY
   ✅ PASS - NEO4J
   ✅ PASS - OPENAI

🎉 All connection tests passed!
```

---

## 🐛 Troubleshooting

### Problem: "NEO4J_URI not set"

**Solution:**
```bash
# Check .env exists
ls -la .env

# Check content
cat .env | grep NEO4J_URI

# Recreate if needed
cp .env.example .env
nano .env
```

### Problem: "Connection refused"

**Solution:**
1. Check Neo4j is running:
   ```bash
   # If using Docker
   docker ps | grep neo4j
   
   # If local install
   neo4j status
   ```

2. Check firewall allows connection

3. Verify URI format:
   - Local: `bolt://localhost:7687`
   - Remote: `bolt://192.168.x.x:7687`
   - Aura: `neo4j+s://xxxxx.databases.neo4j.io`

### Problem: "Authentication failed"

**Solution:**
1. Verify username/password in .env
2. Reset Neo4j password:
   ```bash
   neo4j-admin set-initial-password <new-password>
   ```
3. Update .env with new password

### Problem: "OpenAI API error"

**Solution:**
1. Check API key is valid
2. Check you have credits
3. Check model name is correct
4. Try simpler model: `gpt-3.5-turbo`

---

## 📚 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEO4J_URI` | Yes | - | Neo4j server URI |
| `NEO4J_USER` | Yes | - | Username |
| `NEO4J_PASSWORD` | Yes | - | Password |
| `NEO4J_DATABASE` | No | `neo4j` | Database name |
| `NEO4J_TIMEOUT` | No | `120` | Query timeout (sec) |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `MODEL_NAME` | No | `gpt-4-turbo-preview` | LLM model |
| `OPENAI_API_BASE` | No | `https://api.openai.com/v1` | API endpoint |

---

## 🚀 Next Steps

After setup:

1. **Test connections:**
   ```bash
   python3 test_connections.py
   ```

2. **Run evaluations:**
   ```bash
   python3 evaluate_memory.py
   ```

3. **Start development:**
   - Use `get_config()` to access settings
   - Use `create_neo4j_manager_from_env()` for Neo4j
   - Import OpenAI key from config

---

**Status:** ✅ Environment configuration ready  
**Security:** 🔒 .env protected in .gitignore  
**Next:** Test connections and start development
