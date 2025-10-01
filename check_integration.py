#!/usr/bin/env python3
"""
Check project integration and consistency.

Validates:
- All data files exist and are valid
- Schemas are consistent
- Scripts reference correct files
- Documentation is up-to-date
"""

import os
import json
import sys


def check_data_files():
    """Check data files exist and are valid JSON."""
    print("\n1️⃣ Checking data files...")
    
    files = ['data/stm.json', 'data/mtm.json', 'data/ltm.json']
    all_ok = True
    
    for file in files:
        if not os.path.exists(file):
            print(f"   ❌ {file} - Missing")
            all_ok = False
            continue
        
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            print(f"   ✅ {file} - {len(data)} items")
        except json.JSONDecodeError as e:
            print(f"   ❌ {file} - Invalid JSON: {e}")
            all_ok = False
        except Exception as e:
            print(f"   ❌ {file} - Error: {e}")
            all_ok = False
    
    return all_ok


def check_schemas():
    """Check schema files exist and are valid."""
    print("\n2️⃣ Checking schema files...")
    
    files = ['utils/schema/stm.json', 'utils/schema/mtm.json', 'utils/schema/ltm.json']
    all_ok = True
    
    for file in files:
        if not os.path.exists(file):
            print(f"   ❌ {file} - Missing")
            all_ok = False
            continue
        
        try:
            with open(file, 'r') as f:
                schema = json.load(f)
            print(f"   ✅ {file} - Valid")
        except json.JSONDecodeError as e:
            print(f"   ❌ {file} - Invalid JSON: {e}")
            all_ok = False
    
    return all_ok


def check_scripts():
    """Check essential scripts exist."""
    print("\n3️⃣ Checking scripts...")
    
    scripts = {
        'generate_data.py': 'Data generator',
        'test_code_analysis.py': 'Test suite',
        'utils/schema_validator.py': 'Schema validator',
        'config_ui.py': 'Config UI',
        'main.py': 'Main application'
    }
    
    all_ok = True
    
    for script, desc in scripts.items():
        if os.path.exists(script):
            print(f"   ✅ {script} - {desc}")
        else:
            print(f"   ❌ {script} - Missing ({desc})")
            all_ok = False
    
    return all_ok


def check_file_references():
    """Check scripts reference correct files."""
    print("\n4️⃣ Checking file references...")
    
    checks = [
        ('test_code_analysis.py', ['data/stm.json', 'data/mtm.json', 'data/ltm.json']),
        ('generate_data.py', ['data/stm.json', 'data/mtm.json', 'data/ltm.json']),
        ('utils/schema_validator.py', ['data/stm.json', 'data/mtm.json', 'data/ltm.json']),
    ]
    
    all_ok = True
    
    for script, expected_files in checks:
        if not os.path.exists(script):
            print(f"   ⚠️  {script} - File doesn't exist")
            continue
        
        with open(script, 'r') as f:
            content = f.read()
        
        missing = []
        for file in expected_files:
            if file not in content:
                missing.append(file)
        
        if missing:
            print(f"   ⚠️  {script} - Missing refs: {missing}")
            all_ok = False
        else:
            print(f"   ✅ {script} - All references OK")
    
    return all_ok


def check_documentation():
    """Check documentation files."""
    print("\n5️⃣ Checking documentation...")
    
    docs = ['README.md', 'SETUP.md']
    all_ok = True
    
    for doc in docs:
        if os.path.exists(doc):
            with open(doc, 'r') as f:
                content = f.read()
            
            # Check for key sections
            if doc == 'README.md':
                required = ['Quick Start', 'Configuration', 'Features']
            else:
                required = ['Setup', 'Install']
            
            missing = [r for r in required if r not in content]
            
            if missing:
                print(f"   ⚠️  {doc} - Missing sections: {missing}")
                all_ok = False
            else:
                print(f"   ✅ {doc} - Complete")
        else:
            print(f"   ❌ {doc} - Missing")
            all_ok = False
    
    return all_ok


def check_config():
    """Check configuration files."""
    print("\n6️⃣ Checking configuration...")
    
    configs = [
        'config/system_config.yaml',
        'config.py',
    ]
    
    all_ok = True
    
    for config in configs:
        if os.path.exists(config):
            print(f"   ✅ {config}")
        else:
            print(f"   ⚠️  {config} - Missing (optional)")
    
    return True  # Config files are optional


def main():
    """Run all checks."""
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "INTEGRATION CHECK" + " "*36 + "║")
    print("╚" + "="*78 + "╝")
    
    checks = [
        ("Data Files", check_data_files),
        ("Schemas", check_schemas),
        ("Scripts", check_scripts),
        ("File References", check_file_references),
        ("Documentation", check_documentation),
        ("Configuration", check_config),
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    all_passed = all(results.values())
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {name}")
    
    print("\n" + "="*80)
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED - Project is well integrated!")
        print("="*80)
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED - Please review issues above")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
