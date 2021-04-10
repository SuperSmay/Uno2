import asyncio
import time

runLoop = True

async def loop():
    while (runLoop):
        print("hello from loop")
        asyncio.sleep(1)