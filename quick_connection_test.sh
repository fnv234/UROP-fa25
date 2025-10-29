#!/bin/bash
# Quick Forio Connection Test
# Run with: bash quick_connection_test.sh

echo "========================================================================"
echo "🔍 FORIO CONNECTION TEST"
echo "========================================================================"

# Activate conda base environment
source ~/anaconda3/bin/activate base

# Install required packages if not present
echo ""
echo "📦 Checking dependencies..."
pip install requests python-dotenv flask -q 2>/dev/null || true

# Run the test
echo ""
python test_forio_connection.py
