"""
VISIONZ FastAPI Application - Vercel Deployment Handler
Serverless entry point for Vercel runtime
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'visionz_fixed', 'backend')
sys.path.insert(0, backend_path)

# Change to backend directory for relative imports
os.chdir(backend_path)

from app.main import app

# Vercel expects either 'app' or 'handler'
# FastAPI app is exported as 'app' for Vercel Python runtime

