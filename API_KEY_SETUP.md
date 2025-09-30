# 🔑 API Key Setup Guide

## Bạn có 3 options để chạy với LLM:

---

## Option 1: OpenAI (GPT-3.5/GPT-4) ⭐ Recommended

### Bước 1: Lấy API Key
1. Truy cập: https://platform.openai.com/api-keys
2. Đăng nhập hoặc tạo account
3. Click "Create new secret key"
4. Copy API key (bắt đầu với `sk-...`)

### Bước 2: Set API Key

**Cách A - Terminal (Temporary):**
```bash
export OPENAI_API_KEY='sk-your-key-here'
```

**Cách B - .bashrc/.zshrc (Permanent):**
```bash
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Cách C - Edit config.py:**
```python
# In config.py
LLM_CONFIG = {
    'provider': 'openai',
    'openai': {
        'api_key': 'sk-your-key-here',  # ← Paste here
        'model': 'gpt-3.5-turbo',
    },
    # ...
}
```

### Bước 3: Test
```bash
source .venv/bin/activate
python demo_llm.py
```

---

## Option 2: Anthropic Claude

### Bước 1: Lấy API Key
1. Truy cập: https://console.anthropic.com/settings/keys
2. Đăng nhập hoặc tạo account
3. Click "Create Key"
4. Copy API key

### Bước 2: Set API Key

**Terminal:**
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

**Edit config.py:**
```python
LLM_CONFIG = {
    'provider': 'anthropic',  # ← Change to anthropic
    'anthropic': {
        'api_key': 'your-key-here',  # ← Paste here
        'model': 'claude-3-sonnet-20240229',
    },
}
```

### Bước 3: Test
```bash
source .venv/bin/activate
python demo_llm.py
```

---

## Option 3: Mock LLM (No API Key) 

**Không cần API key!** Hệ thống sẽ dùng mock responses.

```bash
source .venv/bin/activate
python demo_llm.py
```

Mock LLM will work automatically nếu không có API key.

---

## 🚀 Quick Start (Interactive)

Chạy script helper:
```bash
source .venv/bin/activate
bash set_api_key.sh
```

Script sẽ hỏi bạn muốn dùng provider nào và guide bạn set API key.

---

## 📋 Check API Key

Verify API key đã set:

**OpenAI:**
```bash
echo $OPENAI_API_KEY
```

**Anthropic:**
```bash
echo $ANTHROPIC_API_KEY
```

Nếu thấy key → ✅ Success!

---

## 💡 Recommended Setup (Bảo Mật)

**ĐỪNG** commit API key vào git!

### Cách tốt nhất:

1. **Dùng Environment Variable:**
```bash
# Add to ~/.zshrc or ~/.bashrc
export OPENAI_API_KEY="sk-your-key"
```

2. **Tạo .env file (không commit):**
```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-key" > .env

# Add to .gitignore
echo ".env" >> .gitignore
```

3. **Load .env trong code:**
```python
# Install python-dotenv
pip install python-dotenv

# In your code
from dotenv import load_dotenv
load_dotenv()  # Load .env file
```

---

## 🧪 Test Different Models

### OpenAI Models
```python
# In config.py
'model': 'gpt-3.5-turbo',      # Fastest, cheapest
'model': 'gpt-4',               # Best quality
'model': 'gpt-4-turbo-preview', # Fast + good quality
```

### Anthropic Models
```python
# In config.py
'model': 'claude-3-haiku-20240307',    # Fastest
'model': 'claude-3-sonnet-20240229',   # Balanced ⭐
'model': 'claude-3-opus-20240229',     # Best quality
```

---

## 💰 Cost Estimates

### OpenAI (per 1M tokens)
- GPT-3.5-turbo: $0.50 input / $1.50 output
- GPT-4: $30 input / $60 output
- GPT-4-turbo: $10 input / $30 output

### Anthropic (per 1M tokens)
- Claude 3 Haiku: $0.25 input / $1.25 output
- Claude 3 Sonnet: $3 input / $15 output
- Claude 3 Opus: $15 input / $75 output

**Tip:** Start với GPT-3.5-turbo hoặc Claude Haiku cho testing.

---

## 🐛 Troubleshooting

### Error: "No API key found"
```bash
# Check if set
echo $OPENAI_API_KEY

# If empty, set it
export OPENAI_API_KEY='your-key'
```

### Error: "Invalid API key"
- Check key đúng format (OpenAI: `sk-...`)
- Verify key còn active tại console
- Check billing account có credit

### Error: "Rate limit exceeded"
- Đợi một chút rồi thử lại
- Upgrade plan nếu cần
- Giảm số requests

### Demo chạy nhưng không dùng LLM
Check provider trong config.py:
```python
LLM_CONFIG = {
    'provider': 'openai',  # ← Make sure this is correct
}
```

---

## ✅ Verification Checklist

Before running demo:
- [ ] API key obtained from provider
- [ ] API key set (env var hoặc config.py)
- [ ] Verified key with `echo $OPENAI_API_KEY`
- [ ] Virtual environment activated
- [ ] Provider set correctly in config.py

---

## 🎯 Recommended Flow

**First Time Setup:**
1. Get API key từ OpenAI hoặc Anthropic
2. Set environment variable: `export OPENAI_API_KEY='your-key'`
3. Keep key trong ~/.zshrc cho permanent
4. Test: `python demo_llm.py`

**For Testing:**
- Dùng Mock LLM (free, no API key)
- Run: `python demo_llm.py`

**For Production:**
- Use real API key
- Monitor costs
- Implement rate limiting

---

## 📚 Next Steps

Once API key is set:
1. ✅ Run `python demo_llm.py` - See full workflow
2. ✅ Run `python main.py` - Interactive chatbot
3. ✅ Edit queries in demo_llm.py
4. ✅ Adjust model/temperature in config.py
5. ✅ Add your own data to schema.yaml

---

**Need Help?**
- OpenAI Docs: https://platform.openai.com/docs
- Anthropic Docs: https://docs.anthropic.com
- Check `demo_llm.py` for examples
