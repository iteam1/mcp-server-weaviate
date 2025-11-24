import weaviate
from mcp.server.lowlevel import Server
from mcp.types import Tool, TextContent, CallToolResult
import mcp.types as types
from typing import Any

def register_test_connection_tool(app: Server, weaviate_client: weaviate.WeaviateClient):
    """Register the test connection tool with the MCP server."""
    
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
            )
        ]
    
    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None = None) -> list[types.TextContent]:
        if name == "test_connection":
            try:
                # Test connection by getting server metadata
                meta = weaviate_client.get_meta()
                
                if meta:
                    return [
                        TextContent(
                            type="text",
                            text=f"✅ Successfully connected to Weaviate!\n\n"
                                 f"Server Version: {meta.get('version', 'Unknown')}\n"
                                 f"Hostname: {meta.get('hostname', 'Unknown')}\n"
                                 f"Modules: {', '.join(meta.get('modules', []))}"
                        )
                    ]
                else:
                    return [
                        TextContent(
                            type="text",
                            text="✅ Connected to Weaviate, but could not retrieve metadata."
                        )
                    ]
                    
            except Exception as e:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Failed to connect to Weaviate: {str(e)}"
                    )
                ]
        else:
            raise ValueError(f"Unknown tool: {name}")
