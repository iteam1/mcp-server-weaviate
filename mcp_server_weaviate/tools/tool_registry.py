import weaviate
from mcp.server.lowlevel import Server
from mcp.types import Tool, TextContent
import mcp.types as types
from typing import Any
from .test_connection import test_connection_handler
from .list_collections import list_collections_handler
from .near_text_search import near_text_search_handler
from .keyword_search import keyword_search_handler
from .hybrid_search import hybrid_search_handler

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
            ),
            Tool(
                name="near_text_search",
                description="Perform near text search (semantic/vector search) in a collection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection to search in"
                        },
                        "query_text": {
                            "type": "string",
                            "description": "Text query to search for semantically similar results"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["collection_name", "query_text"]
                }
            ),
            Tool(
                name="keyword_search",
                description="Perform keyword search (BM25) in a collection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection to search in"
                        },
                        "query_text": {
                            "type": "string",
                            "description": "Keywords to search for using BM25 algorithm"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["collection_name", "query_text"]
                }
            ),
            Tool(
                name="hybrid_search",
                description="Perform hybrid search (combination of keyword and vector search) in a collection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collection_name": {
                            "type": "string",
                            "description": "Name of the collection to search in"
                        },
                        "query_text": {
                            "type": "string",
                            "description": "Text query for hybrid search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5
                        },
                        "alpha": {
                            "type": "number",
                            "description": "Balance between keyword (0) and vector (1) search. 0=keyword-only, 1=vector-only, 0.5=balanced (default: 0.5)",
                            "default": 0.5,
                            "minimum": 0,
                            "maximum": 1
                        }
                    },
                    "required": ["collection_name", "query_text"]
                }
            )
        ]
    
    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None = None) -> list[types.TextContent]:
        if name == "test_connection":
            return test_connection_handler(weaviate_client, arguments)
        elif name == "list_collections":
            return list_collections_handler(weaviate_client, arguments)
        elif name == "near_text_search":
            return near_text_search_handler(weaviate_client, arguments)
        elif name == "keyword_search":
            return keyword_search_handler(weaviate_client, arguments)
        elif name == "hybrid_search":
            return hybrid_search_handler(weaviate_client, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
