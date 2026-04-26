#!/bin/bash
echo "AI Compliance Monitor — Agent 4: Report Drafting Agent"
echo "=========================================================="

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "Python 3 is required. Please install it."
  exit 1
fi

# Install deps
echo "Installing dependencies..."
pip install fastapi uvicorn anthropic pydantic python-multipart --break-system-packages -q

# Check API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo ""
  echo "ANTHROPIC_API_KEY not set!"
  echo "   Export it: export ANTHROPIC_API_KEY=sk-ant-..."
  echo ""
fi

echo ""
echo "Starting backend on http://localhost:8000"
echo "Open frontend/index.html in your browser"
echo ""
echo "Press Ctrl+C to stop."
echo ""

cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
