import asyncio
import structlog
from dotenv import load_dotenv

load_dotenv()
logger = structlog.get_logger()

async def main():
    logger.info("Agents service started")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
