import asyncpg
import aiomysql

from src.lib.config import Config


class DatabaseManager:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.pool = None
        self.client = None

    async def connect(self) -> None:
        if self.config.db_provider == "postgres":
            await self._connect_postgres()
        elif self.config.db_provider == "mysql":
            await self._connect_mysql()
        else:
            raise ValueError(
                f"Unsupported database provider: {self.config.db_provider}"
            )

    async def _connect_postgres(self) -> None:
        self.pool = await asyncpg.create_pool(
            host=self.config.db_host,
            port=int(self.config.db_port),
            user=self.config.db_user,
            password=self.config.db_password,
            database=self.config.db_password,
            min_size=int(self.config.db_min_pool_size),
            max_size=int(self.config.db_max_pool_size),
        )
        self.client = self.pool

    async def _connect_mysql(self) -> None:
        self.pool = await aiomysql.create_pool(
            host=self.config.db_host,
            port=int(self.config.db_port),
            user=self.config.db_user,
            password=self.config.db_password,
            database=self.config.db_password,
            min_size=int(self.config.db_min_pool_size),
            max_size=int(self.config.db_max_pool_size),
        )
        self.client = self.pool

    async def disconnect(self) -> None:
        if self.pool:
            self.pool.close()
            await self.pool.close()
            self.pool = None
            self.client = None

    async def get_client(self):
        if self.pool is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return await self.pool.acquire()
