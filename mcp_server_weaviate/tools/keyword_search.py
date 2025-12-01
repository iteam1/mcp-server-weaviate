import weaviate
from mcp.types import TextContent
import mcp.types as types
from typing import Any
from weaviate.classes.query import MetadataQuery
import json


def keyword_search_handler(
    weaviate_client: weaviate.WeaviateClient, arguments: dict[str, Any] | None = None
) -> list[types.TextContent]:
    """Handle keyword search (BM25) tool call."""
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
        
        # Perform keyword search using BM25
        response = collection.query.bm25(
            query=query_text,
            limit=limit,
            return_metadata=MetadataQuery(score=True, certainty=True)
        )
        
        if not response or not response.objects:
            return [
                TextContent(
                    type="text",
                    text=f"ℹ️ Keyword search for '{query_text}' in '{collection_name}' returned no results. "
                         f"Note: BM25 search requires inverted indices to be built."
                )
            ]
        
        # Format results
        results = []
        results.append(f"🔎 Keyword Search Results for '{query_text}' in '{collection_name}':\n")
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
                text=f"❌ Keyword search failed: {str(e)}"
            )
        ]
