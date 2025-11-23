import os

from dotenv import load_dotenv
load_dotenv()

import weaviate


def test_weaviate_connection():
    """Test basic connection to Weaviate container."""
    # Get configuration from environment
    http_port = os.getenv("WEAVIATE_HTTP_PORT")
    grpc_port = os.getenv("WEAVIATE_GRPC_PORT")
    
    if not http_port:
        raise ValueError("WEAVIATE_HTTP_PORT environment variable is not set")
    if not grpc_port:
        raise ValueError("WEAVIATE_GRPC_PORT environment variable is not set")
    
    weaviate_url = f"http://localhost:{http_port}"
    
    print(f"Testing connection to Weaviate at {weaviate_url}")
    
    try:
        # Create client connection
        client = weaviate.Client(weaviate_url)
        
        # Test connection by getting live status
        is_live = client.is_live()
        print(f"Weaviate is live: {is_live}")
        assert is_live, "Weaviate server is not live"
        
        # Test connection by getting ready status
        is_ready = client.is_ready()
        print(f"Weaviate is ready: {is_ready}")
        assert is_ready, "Weaviate server is not ready"
        
        # Get cluster info to verify connection
        cluster_info = client.get_cluster_health()
        print(f"Cluster health: {cluster_info}")
        assert cluster_info is not None, "Failed to get cluster health info"
        
        # Get meta info to check modules
        meta = client.get_meta()
        print(f"Weaviate version: {meta.get('version', 'unknown')}")
        
        modules = meta.get("modules", [])
        openai_modules = [m for m in modules if "openai" in str(m).lower()]
        print(f"Available OpenAI modules: {openai_modules}")
        
        print("✅ Successfully connected to Weaviate!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Weaviate: {str(e)}")
        return False


if __name__ == "__main__":
    test_weaviate_connection()