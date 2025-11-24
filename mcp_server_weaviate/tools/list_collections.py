import weaviate
from mcp.types import TextContent
import mcp.types as types
from typing import Any

def list_collections_handler(weaviate_client: weaviate.WeaviateClient, arguments: dict[str, Any] | None = None) -> list[types.TextContent]:
    """Handle list collections tool call."""
    try:
        # Get all collections
        collections = weaviate_client.collections.list_all()
        
        if collections:
            result_text = "📚 Available Weaviate Collections:\n\n"
            
            for collection in collections:
                # Handle different collection object types
                if hasattr(collection, 'name'):
                    collection_name = collection.name
                elif isinstance(collection, str):
                    collection_name = collection
                else:
                    collection_name = str(collection)
                    
                result_text += f"🔹 **{collection_name}**\n"
                
                try:
                    # Get collection info and count
                    collection_info = weaviate_client.collections.get(collection_name)
                    
                    # Get record count
                    try:
                        # Try to get object count using aggregation
                        response = collection_info.aggregate.over_all()
                        total_objects = response.total_count if hasattr(response, 'total_count') else 0
                        result_text += f"   📊 Total Records: {total_objects}\n"
                    except Exception as count_error:
                        result_text += f"   📊 Total Records: Unable to fetch ({str(count_error)})\n"
                    
                    # Get configuration details
                    if hasattr(collection_info, 'config') and collection_info.config:
                        config = collection_info.config
                        result_text += f"   ⚙️  Configuration:\n"
                        
                        if hasattr(config, 'vectorizer'):
                            result_text += f"      - Vectorizer: {config.vectorizer}\n"
                        if hasattr(config, 'generative'):
                            result_text += f"      - Generative: {config.generative}\n"
                        if hasattr(config, 'inverted_index'):
                            result_text += f"      - Inverted Index: {config.inverted_index}\n"
                        if hasattr(config, 'module_config'):
                            result_text += f"      - Module Config: {config.module_config}\n"
                        if hasattr(config, 'properties'):
                            result_text += f"      - Properties: {len(config.properties)} fields\n"
                    
                    # Get some sample properties if available
                    try:
                        # Try to get a sample object to see the structure
                        sample_query = collection_info.query.fetch_objects(limit=1)
                        if sample_query.objects:
                            sample_obj = sample_query.objects[0]
                            result_text += f"   📋 Sample Properties: {list(sample_obj.properties.keys()) if hasattr(sample_obj, 'properties') else 'N/A'}\n"
                    except Exception:
                        pass
                        
                except Exception as detail_error:
                    result_text += f"   ⚠️  Unable to fetch details: {str(detail_error)}\n"
                
                result_text += "\n"
            
            return [
                TextContent(
                    type="text",
                    text=result_text
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text="📭 No collections found in Weaviate.\n\nUse Weaviate's API or client libraries to create collections with data."
                )
            ]
            
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"❌ Failed to list collections: {str(e)}"
            )
        ]
