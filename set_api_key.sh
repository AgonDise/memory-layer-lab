#!/bin/bash
# Helper script to set API keys

echo "🔑 Set your LLM API Key"
echo "======================="
echo ""
echo "Choose your provider:"
echo "1. OpenAI (GPT-3.5/GPT-4)"
echo "2. Anthropic (Claude)"
echo "3. Use Mock LLM (no API key needed)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
  1)
    echo ""
    echo "Enter your OpenAI API key:"
    echo "(Get it from: https://platform.openai.com/api-keys)"
    read -p "API Key: " api_key
    
    if [ -n "$api_key" ]; then
      export OPENAI_API_KEY="$api_key"
      echo ""
      echo "✅ OpenAI API key set!"
      echo ""
      echo "Now run:"
      echo "  python demo_llm.py"
    else
      echo "❌ No API key provided"
    fi
    ;;
    
  2)
    echo ""
    echo "Enter your Anthropic API key:"
    echo "(Get it from: https://console.anthropic.com/settings/keys)"
    read -p "API Key: " api_key
    
    if [ -n "$api_key" ]; then
      export ANTHROPIC_API_KEY="$api_key"
      # Also update config to use anthropic
      echo ""
      echo "✅ Anthropic API key set!"
      echo ""
      echo "Update config.py: LLM_CONFIG['provider'] = 'anthropic'"
      echo "Or run:"
      echo "  python demo_llm.py"
    else
      echo "❌ No API key provided"
    fi
    ;;
    
  3)
    echo ""
    echo "✅ Using Mock LLM (no API key needed)"
    echo ""
    echo "Run:"
    echo "  python demo_llm.py"
    ;;
    
  *)
    echo "❌ Invalid choice"
    ;;
esac
