import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from source.models.models import Base
from source.config.conf import config

engine = create_async_engine(config.DB_URL)

async def create_database_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await create_database_tables()

if __name__ == "__main__":
    asyncio.run(main())
