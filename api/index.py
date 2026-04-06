"""
VISIONZ FastAPI Application - Vercel Deployment Handler
Entry point for Vercel's Python runtime
"""

import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent

# Add backend to path
backend_path = str(project_root / 'visionz_fixed' / 'backend')
sys.path.insert(0, backend_path)

# Change to backend directory for relative imports
os.chdir(backend_path)

try:
    from app.main import app
except Exception as e:
    print(f"Error importing FastAPI app: {e}")
    raise

# Export as both 'app' and 'handler' for Vercel compatibility
handler = app


