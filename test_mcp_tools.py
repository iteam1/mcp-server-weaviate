#!/usr/bin/env python3
"""
Test script to verify MCP search tools work correctly.
"""

import os
import asyncio
import weaviate
from dotenv import load_dotenv
from mcp_server_weaviate.tools.near_text_search import near_text_search_handler
from mcp_server_weaviate.tools.keyword_search import keyword_search_handler
from mcp_server_weaviate.tools.hybrid_search import hybrid_search_handler

load_dotenv()


async def test_search_tools():
    """Test all search tools."""
    
    # Initialize Weaviate client
    http_port = os.getenv("WEAVIATE_HTTP_PORT", "8080")
    grpc_port = os.getenv("WEAVIATE_GRPC_PORT", "50051")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    client = weaviate.WeaviateClient(
        connection_params=weaviate.connect.ConnectionParams(
            http={"host": "localhost", "port": int(http_port), "secure": False},
            grpc={"host": "localhost", "port": int(grpc_port), "secure": False}
        ),
        additional_headers={
            "X-OpenAI-Api-Key": openai_api_key
        }
    )
    
    client.connect()
    print("✅ Connected to Weaviate\n")
    
    # Get first collection
    all_collections = client.collections.list_all()
    collection_names = list(all_collections.keys())
    
    if not collection_names:
        print("❌ No collections found")
        return
    
    collection_name = collection_names[0]
    print(f"Testing with collection: {collection_name}\n")
    
    # Test near text search
    print("=" * 60)
    print("Testing Near Text Search")
    print("=" * 60)
    result = near_text_search_handler(client, {
        "collection_name": collection_name,
        "query_text": "What is the main topic?",
        "limit": 3
    })
    print(result[0].text)
    print()
    
    # Test keyword search
    print("=" * 60)
    print("Testing Keyword Search")
    print("=" * 60)
    result = keyword_search_handler(client, {
        "collection_name": collection_name,
        "query_text": "what",
        "limit": 3
    })
    print(result[0].text)
    print()
    
    # Test hybrid search
    print("=" * 60)
    print("Testing Hybrid Search (balanced)")
    print("=" * 60)
    result = hybrid_search_handler(client, {
        "collection_name": collection_name,
        "query_text": "important information",
        "limit": 3,
        "alpha": 0.5
    })
    print(result[0].text)
    print()
    
    # Test hybrid search with vector-only
    print("=" * 60)
    print("Testing Hybrid Search (vector-only, alpha=1.0)")
    print("=" * 60)
    result = hybrid_search_handler(client, {
        "collection_name": collection_name,
        "query_text": "important information",
        "limit": 3,
        "alpha": 1.0
    })
    print(result[0].text)
    print()
    
    client.close()
    print("✅ All tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_search_tools())
