#!/bin/bash
# Helper script to activate virtual environment

echo "🔧 Activating virtual environment..."

if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv .venv
    echo "✅ Virtual environment created!"
fi

source .venv/bin/activate

echo "✅ Virtual environment activated!"
echo ""
echo "You can now run:"
echo "  python test_simple.py"
echo "  python example_embedding_usage.py"
echo "  python populate_from_schema.py"
echo ""
echo "To deactivate: type 'deactivate'"
