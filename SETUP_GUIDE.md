# Setup Guide - Giải quyết vấn đề cài đặt

## 🚨 Vấn đề: "externally-managed-environment"

Nếu bạn gặp lỗi này trên macOS:
```
error: externally-managed-environment
× This environment is externally managed
```

**Nguyên nhân:** macOS (từ Monterey trở lên) không cho phép cài packages vào system Python.

---

## ✅ Giải pháp: Dùng Virtual Environment

### Option 1: Quick Start (Đã có .venv)

```bash
# Activate venv có sẵn
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_simple.py
```

### Option 2: Tạo mới Virtual Environment

```bash
# 1. Tạo venv
python3 -m venv .venv

# 2. Activate
source .venv/bin/activate

# 3. Install
pip install -r requirements.txt

# 4. Verify
python test_simple.py
```

### Option 3: Dùng Helper Script

```bash
# Easy way!
source activate_env.sh
```

---

## 🔧 Các Commands Thường Dùng

### Activate Virtual Environment
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### Deactivate
```bash
deactivate
```

### Install Package
```bash
# Trong venv
pip install package_name

# Hoặc từ requirements
pip install -r requirements.txt
```

### Check Python Location
```bash
# Trong venv - should show .venv path
which python

# System Python
which python3
```

---

## 🎯 Complete Setup Process

```bash
# 1. Clone/Navigate to project
cd /Users/innotech/memory-layer-lab

# 2. Activate venv (đã có sẵn)
source .venv/bin/activate

# 3. Verify Python
which python
# Should output: /Users/innotech/memory-layer-lab/.venv/bin/python

# 4. Install dependencies (nếu chưa có)
pip install -r requirements.txt

# 5. Test
python test_simple.py

# 6. Try examples
python example_embedding_usage.py
python populate_from_schema.py
```

---

## 🐛 Troubleshooting

### Error: "command not found: pip"
**Solution:**
```bash
# Make sure venv is activated
source .venv/bin/activate

# Then use pip (not pip3)
pip install -r requirements.txt
```

### Error: "No module named pip3"
**Solution:**
```bash
# Use 'pip' instead of 'pip3' in venv
python -m pip install -r requirements.txt
```

### Error: ".venv not found"
**Solution:**
```bash
# Create it
python3 -m venv .venv

# Then activate
source .venv/bin/activate
```

### Python version issues
**Solution:**
```bash
# Check Python version (need 3.8+)
python --version

# If < 3.8, install newer Python
brew install python@3.11
```

---

## 📋 Verification Checklist

- [ ] Virtual environment exists: `ls .venv/`
- [ ] Virtual environment activated: `which python` shows `.venv` path
- [ ] Dependencies installed: `pip list` shows numpy, pyyaml, etc.
- [ ] Tests pass: `python test_simple.py` → ✅ All tests passed
- [ ] Examples work: `python example_embedding_usage.py`

---

## 💡 Best Practices

### Always use Virtual Environment
```bash
# ✅ Good (in venv)
source .venv/bin/activate
pip install package

# ❌ Bad (system-wide)
pip3 install package  # Will fail on macOS
```

### One-liner for commands
```bash
# Run command in venv without staying in it
source .venv/bin/activate && python script.py

# Or
.venv/bin/python script.py
```

### Requirements management
```bash
# Save current packages
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt
```

---

## 🚀 Quick Reference

| Task | Command |
|------|---------|
| Activate venv | `source .venv/bin/activate` |
| Deactivate | `deactivate` |
| Install deps | `pip install -r requirements.txt` |
| Run tests | `python test_simple.py` |
| Run example | `python example_embedding_usage.py` |
| Check Python | `which python` |
| List packages | `pip list` |

---

## 🔗 Related Files

- `activate_env.sh` - Helper script to activate venv
- `QUICKSTART.md` - Quick start guide (updated)
- `requirements.txt` - All dependencies
- `test_simple.py` - Verify installation

---

## ✅ Success Indicators

Bạn biết setup thành công khi:

1. **Venv activated:**
   ```bash
   $ which python
   /Users/innotech/memory-layer-lab/.venv/bin/python
   ```

2. **Tests pass:**
   ```bash
   $ python test_simple.py
   ✅ Imports: PASS
   ✅ Instantiation: PASS
   ✅ Basic Workflow: PASS
   🎉 All tests passed!
   ```

3. **Examples work:**
   ```bash
   $ python example_embedding_usage.py
   ✅ Example complete!
   ```

---

**Date:** 2025-09-30  
**Status:** ✅ Tested & Working
