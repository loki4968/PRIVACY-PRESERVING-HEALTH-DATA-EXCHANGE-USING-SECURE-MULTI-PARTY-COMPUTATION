#!/usr/bin/env python3
"""
Startup script for the Health Data Exchange Platform
This script starts the server with all the new improvements.
"""

import uvicorn
import sys
import os
import platform
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Start the server with improved configuration"""
    try:
        # Add the project root to Python path
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)
        
        # Set event loop policy for Windows
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        logger.info("🚀 Starting Health Data Exchange Platform...")
        logger.info("📊 Version: 1.0.0")
        logger.info("🔒 Security features: Enabled")
        logger.info("📝 Error handling: Enabled")
        logger.info("⚡ Rate limiting: Enabled")
        
        # Run the server with improved configuration
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
