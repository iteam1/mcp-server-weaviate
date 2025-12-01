import weaviate
from mcp.types import TextContent
import mcp.types as types
from typing import Any
from weaviate.classes.query import MetadataQuery
import json


def near_text_search_handler(
    weaviate_client: weaviate.WeaviateClient, arguments: dict[str, Any] | None = None
) -> list[types.TextContent]:
    """Handle near text search tool call."""
    try:
        if not arguments:
            return [
                TextContent(
                    type="text",
                    text="❌ Missing required arguments: collection_name, query_text"
                )
            ]
        
        collection_name = arguments.get("collection_name")
        query_text = arguments.get("query_text")
        limit = arguments.get("limit", 5)
        
        if not collection_name or not query_text:
            return [
                TextContent(
                    type="text",
                    text="❌ Missing required arguments: collection_name, query_text"
                )
            ]
        
        # Get collection
        collection = weaviate_client.collections.get(collection_name)
        
        # Perform near text search
        response = collection.query.near_text(
            query=query_text,
            limit=limit,
            return_metadata=MetadataQuery(distance=True, certainty=True)
        )
        
        if not response or not response.objects:
            return [
                TextContent(
                    type="text",
                    text=f"ℹ️ Near text search for '{query_text}' in '{collection_name}' returned no results"
                )
            ]
        
        # Format results
        results = []
        results.append(f"🔍 Near Text Search Results for '{query_text}' in '{collection_name}':\n")
        results.append(f"Found {len(response.objects)} results (limit: {limit})\n")
        
        for i, obj in enumerate(response.objects, 1):
            results.append(f"\n--- Result {i} ---")
            
            # Add properties
            if hasattr(obj, 'properties') and obj.properties:
                for key, value in obj.properties.items():
                    if isinstance(value, str):
                        results.append(f"{key}: {value}")
            
            # Add metadata
            if hasattr(obj, 'metadata') and obj.metadata:
                if hasattr(obj.metadata, 'distance'):
                    results.append(f"Distance: {obj.metadata.distance}")
                if hasattr(obj.metadata, 'certainty'):
                    results.append(f"Certainty: {obj.metadata.certainty}")
        
        return [
            TextContent(
                type="text",
                text="\n".join(results)
            )
        ]
        
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"❌ Near text search failed: {str(e)}"
            )
        ]
