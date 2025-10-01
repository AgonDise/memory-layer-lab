#!/usr/bin/env python3
"""
Generate schema-compliant test data for CODE ANALYSIS domain.

Generates STM, MTM, LTM data matching JSON schemas in utils/schema/.
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

PROJECT_ID = "innocody-demo"
CONVERSATION_ID = "conv_" + str(uuid.uuid4())[:8]

# Try real embeddings
try:
    from utils.real_embedding import RealEmbeddingGenerator
    embedder = RealEmbeddingGenerator()
    USE_REAL = True
except:
    USE_REAL = False
    class MockEmbedder:
        def generate(self, text):
            import hashlib, random
            h = int(hashlib.md5(text.encode()).hexdigest(), 16)
            random.seed(h)
            return [random.random() for _ in range(384)]
    embedder = MockEmbedder()

print(f"📊 Embedding: {'Real' if USE_REAL else 'Mock'}")

# ============================================================================
# STM DATA - Code discussion messages
# ============================================================================

STM_MESSAGES = [
    ("user", "Hàm computeMetrics bị lỗi chia cho 0, làm sao sửa?", "debug", "analytics/stats.py", "computeMetrics", 42, 58),
    ("assistant", "Lỗi chia 0 xảy ra khi count=0. Thêm check: if count == 0: return None", "response", "analytics/stats.py", "computeMetrics", 42, 58),
    ("user", "Commit nào đã fix lỗi này?", "commit_search", None, None, None, None),
    ("assistant", "Commit abc123 (John Doe - 2023-09-10) đã fix với message 'Fix division by zero'", "response", None, None, None, None),
    ("user", "Module Analytics có những hàm nào?", "code_search", "analytics/", None, None, None),
    ("assistant", "Module Analytics có: computeMetrics, calculateAverage, calculateStdDev, generateReport", "response", "analytics/", None, None, None),
]

def generate_stm():
    """Generate STM data."""
    messages = []
    base_time = datetime.now()
    
    for idx, (role, content, intent, file_path, func, line_start, line_end) in enumerate(STM_MESSAGES):
        msg = {
            "id": f"stm_{uuid.uuid4().hex[:12]}",
            "role": role,
            "content": content,
            "timestamp": (base_time - timedelta(minutes=len(STM_MESSAGES)-idx)).isoformat(),
            "project_id": PROJECT_ID,
            "metadata": {
                "conversation_id": CONVERSATION_ID,
                "embedding": embedder.generate(content),
                "intent": intent,
                "keywords": [w for w in ["computeMetrics", "commit", "analytics", "error", "fix", "module"] if w.lower() in content.lower()],
            }
        }
        
        if file_path:
            msg["metadata"]["file_path"] = file_path
        if func:
            msg["metadata"]["function_name"] = func
        if line_start:
            msg["metadata"]["line_start"] = line_start
            msg["metadata"]["line_end"] = line_end
        
        messages.append(msg)
    
    return messages


# ============================================================================
# MTM DATA - Commit logs and summaries
# ============================================================================

MTM_COMMITS = [
    ("abc123", "Fix division by zero in computeMetrics", "bugfix", "John Doe", "analytics/stats.py", "computeMetrics", 42, 58, "#242", 2, 0, "critical"),
    ("def456", "Refactor metrics calculation logic", "refactor", "John Doe", "analytics/stats.py", "computeMetrics", 30, 80, None, 15, 10, "medium"),
    ("xyz789", "Add analytics module documentation", "doc", "Jane Smith", "docs/analytics.md", None, None, None, None, 50, 0, "low"),
    ("ghi012", "Implement new aggregation features", "feature", "Jane Smith", "analytics/aggregator.py", "aggregate", 10, 45, "#188", 35, 0, "high"),
]

def generate_mtm():
    """Generate MTM data."""
    chunks = []
    base_time = datetime.now()
    
    # 1. Commit-based chunks
    for idx, (commit, msg, change_type, author, file_path, func, line_start, line_end, issue_id, added, removed, severity) in enumerate(MTM_COMMITS):
        summary = f"Commit {commit}: {msg}"
        if issue_id:
            summary += f" (fixes {issue_id})"
        
        chunk = {
            "id": f"mtm_{uuid.uuid4().hex[:12]}",
            "name": f"Commit {commit[:7]}",
            "summary": summary,
            "project_id": PROJECT_ID,
            "timestamp": (base_time - timedelta(days=30-idx*7)).isoformat(),
            "metadata": {
                "change_type": change_type,
                "git_commit": commit,
                "author": author,
                "embedding": embedder.generate(summary),
            }
        }
        
        if file_path:
            chunk["metadata"]["file_path"] = file_path
        if func:
            chunk["metadata"]["function_name"] = func
        if line_start:
            chunk["metadata"]["line_start"] = line_start
            chunk["metadata"]["line_end"] = line_end
        if issue_id:
            chunk["metadata"]["issue_id"] = issue_id
        if added is not None:
            chunk["metadata"]["lines_added"] = added
            chunk["metadata"]["lines_removed"] = removed
        if severity:
            chunk["metadata"]["severity"] = severity
        
        chunks.append(chunk)
    
    # 2. Conversation summary
    summary = "Debugging session: User reported divide-by-zero error in computeMetrics. Found fix in commit abc123."
    chunks.append({
        "id": f"mtm_{uuid.uuid4().hex[:12]}",
        "name": "Debug Session Summary",
        "summary": summary,
        "project_id": PROJECT_ID,
        "timestamp": base_time.isoformat(),
        "metadata": {
            "change_type": "bugfix",
            "git_commit": "abc123",
            "embedding": embedder.generate(summary),
        }
    })
    
    return chunks


# ============================================================================
# LTM DATA - Knowledge base
# ============================================================================

LTM_FACTS = [
    ("architecture", "System consists of 4 modules: Analytics, UI, Database, API. Analytics handles data processing.", "high", ["analytics", "architecture", "modules"]),
    ("module", "Analytics module: Located in analytics/. Main functions: computeMetrics, calculateAverage, calculateStdDev.", "high", ["analytics", "module"]),
    ("function", "computeMetrics(data): Calculates mean, median, std. Raises ValueError on empty input. Fixed divide-by-zero in commit abc123.", "critical", ["computeMetrics", "function", "analytics"]),
    ("function", "calculateAverage(numbers): Returns arithmetic mean. Used by computeMetrics. Includes zero-division check.", "medium", ["calculateAverage", "function"]),
    ("commit_log", "Commit abc123 by John Doe (2023-09-10): Fixed divide-by-zero in computeMetrics. Issue #242.", "high", ["commit", "abc123", "bugfix"]),
    ("commit_log", "Commit def456 by John Doe (2023-08-01): Refactored metrics calculation for better performance.", "medium", ["commit", "def456", "refactor"]),
    ("guideline", "All calculation functions must validate inputs. Check for empty arrays and zero division before operations.", "critical", ["guideline", "validation"]),
    ("guideline", "Testing policy: Min 80% coverage. Unit tests required for all public functions. Use pytest framework.", "high", ["testing", "guideline"]),
    ("architecture", "Module dependencies: Analytics -> Database (data), API -> Analytics (metrics), UI -> API (display).", "medium", ["dependencies", "architecture"]),
]

def generate_ltm():
    """Generate LTM data."""
    facts = []
    base_time = datetime.now()
    
    for idx, (category, content, importance, tags) in enumerate(LTM_FACTS):
        fact = {
            "id": f"ltm_{uuid.uuid4().hex[:12]}",
            "content": content,
            "project_id": PROJECT_ID,
            "metadata": {
                "category": category,
                "embedding": embedder.generate(content),
                "importance": importance,
                "created_at": (base_time - timedelta(days=60+idx*5)).isoformat(),
                "last_accessed": base_time.isoformat(),
            }
        }
        
        if tags:
            fact["metadata"]["tags"] = tags
        
        # Add module info for relevant facts
        if "analytics" in content.lower():
            fact["metadata"]["module"] = "Analytics"
        
        # Add git commit for commit logs
        if category == "commit_log":
            if "abc123" in content:
                fact["metadata"]["git_commit"] = "abc123"
                fact["metadata"]["author"] = "John Doe"
                fact["metadata"]["issue_id"] = "#242"
            elif "def456" in content:
                fact["metadata"]["git_commit"] = "def456"
                fact["metadata"]["author"] = "John Doe"
        
        facts.append(fact)
    
    return facts


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🏗️  GENERATING SCHEMA-COMPLIANT CODE ANALYSIS DATA")
    print("="*80)
    
    os.makedirs("data", exist_ok=True)
    
    # Generate
    print("\n1️⃣  Generating STM...")
    stm = generate_stm()
    print(f"   ✅ {len(stm)} messages")
    
    print("\n2️⃣  Generating MTM...")
    mtm = generate_mtm()
    print(f"   ✅ {len(mtm)} chunks")
    
    print("\n3️⃣  Generating LTM...")
    ltm = generate_ltm()
    print(f"   ✅ {len(ltm)} facts")
    
    # Save
    with open("data/stm.json", 'w', encoding='utf-8') as f:
        json.dump(stm, f, ensure_ascii=False, indent=2)
    
    with open("data/mtm.json", 'w', encoding='utf-8') as f:
        json.dump(mtm, f, ensure_ascii=False, indent=2)
    
    with open("data/ltm.json", 'w', encoding='utf-8') as f:
        json.dump(ltm, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"STM: {len(stm)} messages → data/stm.json")
    print(f"MTM: {len(mtm)} chunks → data/mtm.json")
    print(f"LTM: {len(ltm)} facts → data/ltm.json")
    print(f"Project: {PROJECT_ID}")
    print(f"Conversation: {CONVERSATION_ID}")
    print("\n✅ Data generation complete!")
    print("\nValidate: python3 utils/schema_validator.py")
    print("="*80)


if __name__ == "__main__":
    main()
