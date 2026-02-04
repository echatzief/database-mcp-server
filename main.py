import asyncio

from src.lib.config import Config
from src.database.manager import DatabaseManager
from dotenv import load_dotenv

load_dotenv()

async def main():
    config = Config()
    database_manager = DatabaseManager(config)

    await database_manager.connect()

if __name__ == "__main__":
    asyncio.run(main())
