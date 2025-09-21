#!/bin/bash
# Simple script to activate virtual environment
# Usage: source activate.sh

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated for FinChat"
    echo "📍 Current directory: $(pwd)"
    echo "🐍 Python: $(which python)"
else
    echo "❌ Virtual environment not found. Run 'python3 -m venv venv' first."
fi
