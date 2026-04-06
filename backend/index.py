"""
Vercel serverless handler - NOT used for Railway deployment
This file is kept for reference only
Railway uses: uvicorn app.main:app via Procfile
"""

import sys
import os
from pathlib import Path

backend_path = str(Path(__file__).parent)
sys.path.insert(0, backend_path)
os.chdir(backend_path)

try:
    from app.main import app
except Exception as e:
    print(f"Error importing FastAPI app: {e}")
    raise

handler = app


