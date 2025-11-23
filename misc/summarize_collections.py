#!/usr/bin/env python3
"""
Script to summarize Weaviate collections and their records.
Saves the summary to the misc folder.
"""

import os
import json
import weaviate
from dotenv import load_dotenv
from datetime import datetime

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

def get_collection_summary(client, collection_name):
    """Get detailed summary of a collection."""
    try:
        collection = client.collections.get(collection_name)
        
        # Get total count
        aggregate_response = collection.aggregate.over_all(total_count=True)
        total_count = aggregate_response.total_count
        
        # Get sample records
        sample_response = collection.query.fetch_objects(
            limit=3, 
            return_properties=["question", "answer", "qa_id"]
        )
        
        # Get sample questions and answers
        samples = []
        for obj in sample_response.objects:
            props = obj.properties
            samples.append({
                "qa_id": props.get("qa_id", ""),
                "question": props.get("question", ""),
                "answer": props.get("answer", "")[:100] + "..." if len(props.get("answer", "")) > 100 else props.get("answer", "")
            })
        
        return {
            "collection": collection_name,
            "total_records": total_count,
            "sample_records": samples
        }
        
    except Exception as e:
        print(f"❌ Error getting summary for {collection_name}: {e}")
        return None

def create_summary_report(client):
    """Create a comprehensive summary report."""
    print("📊 Creating collection summary...")
    
    # Get all collections
    all_collections = client.collections.list_all()
    collection_names = list(all_collections.keys())
    
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_collections": len(collection_names),
        "total_records": 0,
        "collections": []
    }
    
    print(f"Found {len(collection_names)} collections")
    
    for collection_name in sorted(collection_names):
        print(f"Processing {collection_name}...")
        
        collection_summary = get_collection_summary(client, collection_name)
        if collection_summary:
            summary["collections"].append(collection_summary)
            summary["total_records"] += collection_summary["total_records"]
    
    return summary

def print_summary(summary):
    """Print summary to console only."""
    print(f"\n📄 Weaviate Collections Summary")
    print("=" * 50)
    print(f"Generated: {summary['generated_at']}")
    print(f"Total Collections: {summary['total_collections']}")
    print(f"Total Records: {summary['total_records']}\n")
    
    for collection in summary["collections"]:
        print(f"Collection: {collection['collection']}")
        print(f"Records: {collection['total_records']}")
        print(f"Sample Q&A:")
        
        for i, sample in enumerate(collection['sample_records'], 1):
            print(f"  {i}. Q: {sample['question']}")
            print(f"     A: {sample['answer']}")
        
        print("\n" + "-" * 30 + "\n")

def main():
    """Main function to create and display collection summary."""
    print("=== Weaviate Collection Summarizer ===")
    
    # Connect to Weaviate
    client = connect_to_weaviate()
    if not client:
        return
    
    try:
        # Create summary
        summary = create_summary_report(client)
        
        # Print summary to console
        print_summary(summary)
        
        # Print brief summary to console
        print(f"📊 Quick Summary:")
        print(f"   Collections: {summary['total_collections']}")
        print(f"   Total Records: {summary['total_records']}")
        
        for collection in summary["collections"]:
            print(f"   📂 {collection['collection']}: {collection['total_records']} records")
        
    finally:
        client.close()

if __name__ == "__main__":
    main()
