"""
VISIONZ Backend — Server Launcher
Run this file to start the API server.

Usage:
    python run.py
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("  VISIONZ QC Backend — Starting Server")
    print("=" * 50)
    print("  API URL  : http://localhost:8000")
    print("  API Docs : http://localhost:8000/docs")
    print("  Health   : http://localhost:8000/api/health")
    print("=" * 50)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,          # auto-reload on code changes
        log_level="info",
    )
