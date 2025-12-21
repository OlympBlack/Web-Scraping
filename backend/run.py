import sys
import asyncio
import uvicorn

if __name__ == "__main__":
    # Fix for Playwright on Windows: ensure ProactorEventLoop is used
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Run Uvicorn programmatically
    # reload=False to test if the reloader is causing the loop policy issue
    # loop="asyncio" ensures uvicorn uses the standard asyncio loop, respecting our Proactor policy
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False, loop="asyncio")
