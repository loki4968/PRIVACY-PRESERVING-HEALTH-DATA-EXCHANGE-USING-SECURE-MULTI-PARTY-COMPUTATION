import uvicorn
import sys
import os
import platform
import asyncio

if __name__ == "__main__":
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Set event loop policy for Windows
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the server
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True) 