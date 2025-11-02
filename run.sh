#!/bin/bash

# BloomSkin API - Run Script

echo "🚀 Starting BloomSkin API..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
