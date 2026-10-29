"""
VakeelAI LegalTech Application Server
-------------------------------------
Starts the FastAPI application with Uvicorn.
Run with:
    python run.py
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("Starting VakeelAI Legal Engineering Platform...")
    print("Web Dashboard: http://localhost:8000")
    print("FastAPI Docs:  http://localhost:8000/docs")
    print("=" * 70)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

