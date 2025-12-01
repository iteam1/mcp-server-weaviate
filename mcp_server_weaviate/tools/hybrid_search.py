import weaviate
from mcp.types import TextContent
import mcp.types as types
from typing import Any
from weaviate.classes.query import MetadataQuery
import json


def hybrid_search_handler(
    weaviate_client: weaviate.WeaviateClient, arguments: dict[str, Any] | None = None
) -> list[types.TextContent]:
    """Handle hybrid search tool call."""
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
        alpha = arguments.get("alpha", 0.5)  # Balance between keyword and vector search
        
        if not collection_name or not query_text:
            return [
                TextContent(
                    type="text",
                    text="❌ Missing required arguments: collection_name, query_text"
                )
            ]
        
        # Validate alpha parameter
        if not (0 <= alpha <= 1):
            return [
                TextContent(
                    type="text",
                    text="❌ Invalid alpha parameter. Must be between 0 and 1 (0=keyword-only, 1=vector-only)"
                )
            ]
        
        # Get collection
        collection = weaviate_client.collections.get(collection_name)
        
        # Perform hybrid search
        response = collection.query.hybrid(
            query=query_text,
            limit=limit,
            alpha=alpha,
            return_metadata=MetadataQuery(score=True, certainty=True)
        )
        
        if not response or not response.objects:
            return [
                TextContent(
                    type="text",
                    text=f"ℹ️ Hybrid search for '{query_text}' in '{collection_name}' returned no results"
                )
            ]
        
        # Format results
        results = []
        alpha_desc = "keyword-only" if alpha == 0 else "vector-only" if alpha == 1 else f"balanced (α={alpha})"
        results.append(f"🔗 Hybrid Search Results for '{query_text}' in '{collection_name}' ({alpha_desc}):\n")
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
                if hasattr(obj.metadata, 'score'):
                    results.append(f"Score: {obj.metadata.score}")
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
                text=f"❌ Hybrid search failed: {str(e)}"
            )
        ]
