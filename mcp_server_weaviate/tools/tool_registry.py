import weaviate
from mcp.server.lowlevel import Server
from mcp.types import Tool, TextContent
import mcp.types as types
from typing import Any
from .test_connection import test_connection_handler
from .list_collections import list_collections_handler

def register_all_tools(app: Server, weaviate_client: weaviate.WeaviateClient):
    """Register all tools with the MCP server."""
    
    @app.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="test_connection",
                description="Test connection to Weaviate server and get server information",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="list_collections",
                description="List all available collections in Weaviate",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
    
    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None = None) -> list[types.TextContent]:
        if name == "test_connection":
            return test_connection_handler(weaviate_client, arguments)
        elif name == "list_collections":
            return list_collections_handler(weaviate_client, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
