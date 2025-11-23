#!/usr/bin/env python3
"""
Script to remove specific collections or all collections from Weaviate.
"""

import os
import weaviate
from dotenv import load_dotenv

load_dotenv()

def connect_to_weaviate():
    """Connect to Weaviate instance."""
    http_port = os.getenv("WEAVIATE_HTTP_PORT")
    grpc_port = os.getenv("WEAVIATE_GRPC_PORT")
    
    if not http_port:
        raise ValueError("WEAVIATE_HTTP_PORT environment variable is not set")
    if not grpc_port:
        raise ValueError("WEAVIATE_GRPC_PORT environment variable is not set")
    
    try:
        client = weaviate.WeaviateClient(
            connection_params=weaviate.connect.ConnectionParams(
                http={"host": "localhost", "port": int(http_port), "secure": False},
                grpc={"host": "localhost", "port": int(grpc_port), "secure": False}
            )
        )
        
        client.connect()
        return client
    except Exception as e:
        print(f"❌ Failed to connect to Weaviate: {e}")
        return None

def list_collections(client):
    """List all collections in Weaviate."""
    try:
        all_collections = client.collections.list_all()
        collection_names = list(all_collections.keys())
        
        if not collection_names:
            print("📭 No collections found")
            return []
        
        print(f"📚 Found {len(collection_names)} collections:")
        for i, name in enumerate(sorted(collection_names), 1):
            # Get record count for each collection
            try:
                collection = client.collections.get(name)
                count_response = collection.aggregate.over_all(total_count=True)
                count = count_response.total_count
                print(f"   {i}. {name} ({count} records)")
            except:
                print(f"   {i}. {name} (count unavailable)")
        
        return sorted(collection_names)
        
    except Exception as e:
        print(f"❌ Error listing collections: {e}")
        return []

def remove_collection(client, collection_name):
    """Remove a specific collection."""
    try:
        # Check if collection exists
        if not client.collections.exists(collection_name):
            print(f"❌ Collection '{collection_name}' does not exist")
            return False
        
        # Get record count before deletion
        collection = client.collections.get(collection_name)
        count_response = collection.aggregate.over_all(total_count=True)
        count = count_response.total_count
        
        # Confirm deletion
        print(f"🗑️  Removing collection '{collection_name}' with {count} records...")
        
        # Delete the collection
        client.collections.delete(collection_name)
        
        print(f"✅ Successfully removed collection '{collection_name}'")
        return True
        
    except Exception as e:
        print(f"❌ Error removing collection '{collection_name}': {e}")
        return False

def remove_all_collections(client):
    """Remove all collections from Weaviate."""
    try:
        collection_names = list_collections(client)
        
        if not collection_names:
            print("📭 No collections to remove")
            return True
        
        print(f"\n⚠️  WARNING: About to remove ALL {len(collection_names)} collections!")
        print("This action cannot be undone.")
        
        # Get confirmation
        confirm = input("Type 'DELETE ALL' to confirm: ").strip()
        
        if confirm != "DELETE ALL":
            print("❌ Operation cancelled")
            return False
        
        print("\n🗑️  Removing all collections...")
        
        success_count = 0
        for collection_name in collection_names:
            if remove_collection(client, collection_name):
                success_count += 1
        
        print(f"\n✅ Successfully removed {success_count}/{len(collection_names)} collections")
        return True
        
    except Exception as e:
        print(f"❌ Error removing all collections: {e}")
        return False

def interactive_mode(client):
    """Interactive mode for managing collections."""
    while True:
        print("\n" + "="*50)
        print("🗂️  Weaviate Collection Manager")
        print("="*50)
        print("1. List all collections")
        print("2. Remove specific collection")
        print("3. Remove ALL collections")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == "1":
            list_collections(client)
        
        elif choice == "2":
            collections = list_collections(client)
            if not collections:
                continue
            
            print("\nSelect collection to remove:")
            for i, name in enumerate(collections, 1):
                print(f"   {i}. {name}")
            
            try:
                idx = input(f"Enter number (1-{len(collections)}) or collection name: ").strip()
                
                if idx.isdigit():
                    idx_num = int(idx) - 1
                    if 0 <= idx_num < len(collections):
                        collection_name = collections[idx_num]
                    else:
                        print("❌ Invalid number")
                        continue
                else:
                    collection_name = idx
                
                remove_collection(client, collection_name)
                
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == "3":
            remove_all_collections(client)
        
        elif choice == "4":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please select 1-4.")

def main():
    """Main function."""
    print("=== Weaviate Collection Remover ===")
    
    # Connect to Weaviate
    client = connect_to_weaviate()
    if not client:
        return
    
    try:
        # Check for command line arguments
        import sys
        
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "list":
                list_collections(client)
            
            elif command == "remove" and len(sys.argv) > 2:
                collection_name = sys.argv[2]
                remove_collection(client, collection_name)
            
            elif command == "remove-all":
                remove_all_collections(client)
            
            else:
                print("Usage:")
                print("  python remove_collections.py list")
                print("  python remove_collections.py remove <collection_name>")
                print("  python remove_collections.py remove-all")
                print("  python remove_collections.py  # Interactive mode")
        
        else:
            # Interactive mode
            interactive_mode(client)
        
    finally:
        client.close()

if __name__ == "__main__":
    main()
