import asyncio
from typing import Optional

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

from src.lib.config import Config
from src.database.manager import DatabaseManager
from src.database.formatter import format_results


def create_mcp_server(database_manager: DatabaseManager, config: Config) -> FastMCP:
    mcp = FastMCP(
        "database-mcp-server", host=config.http_host, port=int(config.http_port)
    )

    @mcp.tool(
        description=
            """
                Execute a query against the database. 
        
                For PostgreSQL/MySQL: Use SQL syntax (e.g., "SELECT * FROM users WHERE active = true LIMIT 10")

                For MongoDB: Use JSON format with operation type:
                    - find: {"collection": "users", "operation": "find", "filter": {"active": true}, "limit": 10}
                    - find_one: {"collection": "users", "operation": "find_one", "filter": {"_id": "..."}}
                    - insert_one: {"collection": "users", "operation": "insert_one", "document": {"name": "John"}}
                    - insert_many: {"collection": "users", "operation": "insert_many", "documents": [{...}, {...}]}
                    - update_one/update_many: {"collection": "users", "operation": "update_many", "filter": {...}, "update": {"$set": {...}}}
                    - delete_one/delete_many: {"collection": "users", "operation": "delete_many", "filter": {...}}
                    - aggregate: {"collection": "users", "operation": "aggregate", "pipeline": [{"$group": {...}}]}
                    - count: {"collection": "users", "operation": "count", "filter": {...}}

                Optional fields for find: projection, sort, skip, limit
            """
    )
    async def execute_query(query: str, format_type: str = "json") -> str:
        results = await database_manager.client.execute_query(query)
        return format_results(results, format_type)

    @mcp.tool()
    async def list_databases(format_type: str = "json") -> str:
        results = await database_manager.client.list_databases()
        return format_results(results, format_type)

    @mcp.tool()
    async def list_tables(
        database: Optional[str] = None, format_type: str = "json"
    ) -> str:
        results = await database_manager.client.list_tables(database)
        return format_results(results, format_type)

    @mcp.tool()
    async def describe_table(table_name: str, format_type: str = "json") -> str:
        results = await database_manager.client.describe_table(table_name)
        return format_results(results, format_type)

    return mcp


async def run_server():
    config = Config()
    database_manager = DatabaseManager(config)
    await database_manager.connect()

    mcp = create_mcp_server(database_manager, config)
    await mcp.run_streamable_http_async()

    await database_manager.disconnect()


def main():
    asyncio.run(run_server())
