#!/usr/bin/env python
"""
Wrapper script to run STT service with uvicorn
Run with: python run.py
Or: python -m uvicorn app:app --host 127.0.0.1 --port 8003
"""
import os
import sys
import uvicorn

if __name__ == "__main__":
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Add current directory to path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Run uvicorn
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8003,
        reload=False,
        log_level="info"
    )
