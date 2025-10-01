#!/usr/bin/env python3
"""
Test Connections to External Services

Tests:
- Neo4j database connection
- OpenAI API connection
"""

import sys
from utils.env_loader import get_config
from utils.neo4j_manager import create_neo4j_manager_from_env


def test_neo4j():
    """Test Neo4j connection."""
    print("\n1️⃣ Testing Neo4j Connection...")
    print("="*80)
    
    try:
        config = get_config()
        print(f"   URI: {config.neo4j_uri}")
        print(f"   User: {config.neo4j_user}")
        print(f"   Database: {config.neo4j_database}")
        
        # Create manager
        manager = create_neo4j_manager_from_env()
        
        # Connect
        print("\n   Connecting...")
        manager.connect()
        
        if manager.is_connected():
            print("   ✅ Connected successfully!")
            
            # Test query
            result = manager.execute_read("RETURN 1 as test")
            if result and result[0]['test'] == 1:
                print("   ✅ Test query successful!")
            
            # Get Neo4j version
            version_result = manager.execute_read("CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version")
            if version_result:
                print(f"   ✅ Neo4j version: {version_result[0]['version']}")
            
            # Disconnect
            manager.disconnect()
            print("   ✅ Disconnected")
            
            return True
        else:
            print("   ❌ Connection failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_openai():
    """Test OpenAI API connection."""
    print("\n2️⃣ Testing OpenAI API Connection...")
    print("="*80)
    
    try:
        config = get_config()
        
        if not config.openai_api_key:
            print("   ⚠️  OpenAI API key not set in .env")
            return False
        
        print(f"   API Key: {config.openai_api_key[:20]}...")
        print(f"   Model: {config.model_name}")
        
        # Try to import openai
        try:
            import openai
        except ImportError:
            print("   ⚠️  OpenAI library not installed")
            print("   Install: pip install openai")
            return False
        
        # Set API key
        openai.api_key = config.openai_api_key
        
        # Test simple completion
        print("\n   Testing API call...")
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Use cheaper model for test
                messages=[{"role": "user", "content": "Say 'test successful' in Vietnamese"}],
                max_tokens=20
            )
            
            message = response.choices[0].message.content
            print(f"   ✅ Response: {message}")
            print("   ✅ OpenAI API working!")
            return True
            
        except Exception as e:
            print(f"   ❌ API call failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Run all connection tests."""
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "CONNECTION TESTS" + " "*38 + "║")
    print("╚" + "="*78 + "╝")
    
    # Load config
    print("\n📋 Loading configuration from .env...")
    config = get_config()
    print("   ✅ Configuration loaded")
    
    # Run tests
    results = {
        'neo4j': test_neo4j(),
        'openai': test_openai()
    }
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    for service, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {service.upper()}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 All connection tests passed!")
        print("="*80)
        return 0
    else:
        print("⚠️  Some connection tests failed")
        print("   Check your .env configuration")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
