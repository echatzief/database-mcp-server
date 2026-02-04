import aiomysql
from typing import Any, List, Dict, Optional
from dataclasses import dataclass

@dataclass
class MySQLClient:
    pool: aiomysql.Pool

    async def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                if cursor.description:
                    return await cursor.fetchall()
                await connection.commit()
                return []

    async def list_databases(self) -> List[str]:
        result = await self.execute_query("SHOW DATABASES")
        return [row["Database"] for row in result]

    async def list_tables(self, database: Optional[str] = None) -> List[str]:
        if database:
            await self.execute_query(f"USE `{database}`")
        result = await self.execute_query("SHOW TABLES")
        if not result:
            return []
        key = list(result[0].keys())[0]
        return [row[key] for row in result]

    async def describe_table(self, table_name: str) -> List[Dict[str, Any]]:
        return await self.execute_query(f"DESCRIBE `{table_name}`")

    async def close(self) -> None:
        self.pool.close()
        await self.pool.wait_closed()
