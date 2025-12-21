
import sys
import asyncio
import warnings
import uvicorn

# Suppress DeprecationWarning for WindowsProactorEventLoopPolicy in Python 3.14+
warnings.filterwarnings("ignore", category=DeprecationWarning)

if __name__ == "__main__":
    if sys.platform == "win32":
        # Force ProactorEventLoopPolicy for Playwright compatibility on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the server on port 8000
    # Reload is set to False to ensure the event loop policy is respected in this process.
    # If reload is needed, we might need a more complex setup or ensure spawned processes run this script.
    print("Starting backend with ProactorEventLoop policy...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
