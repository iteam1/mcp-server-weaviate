import weaviate
from mcp.types import TextContent
import mcp.types as types
from typing import Any

def test_connection_handler(weaviate_client: weaviate.WeaviateClient, arguments: dict[str, Any] | None = None) -> list[types.TextContent]:
    """Handle test connection tool call."""
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
