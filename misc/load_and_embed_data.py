#!/usr/bin/env python3
"""
Script to load SQuAD data and embed into Weaviate using OpenAI embeddings.
Each topic becomes a separate collection.
"""

import os
import json
import weaviate
from weaviate.classes.config import Property, DataType, Configure
from dotenv import load_dotenv

load_dotenv()


def connect_to_weaviate():
    """Connect to Weaviate instance."""
    http_port = os.getenv("WEAVIATE_HTTP_PORT")
    grpc_port = os.getenv("WEAVIATE_GRPC_PORT")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not http_port:
        raise ValueError("WEAVIATE_HTTP_PORT environment variable is not set")
    if not grpc_port:
        raise ValueError("WEAVIATE_GRPC_PORT environment variable is not set")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    try:
        client = weaviate.WeaviateClient(
            connection_params=weaviate.connect.ConnectionParams(
                http={"host": "localhost", "port": int(http_port), "secure": False},
                grpc={"host": "localhost", "port": int(grpc_port), "secure": False},
            ),
            additional_headers={"X-OpenAI-Api-Key": openai_api_key},
        )

        client.connect()
        print(
            f"✅ Connected to Weaviate on HTTP port {http_port}, gRPC port {grpc_port}"
        )
        return client
    except Exception as e:
        print(f"❌ Failed to connect to Weaviate: {e}")
        return None


def load_squad_data(data_file):
    """Load SQuAD data from JSON file."""
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"✅ Loaded data from {data_file}")
        print(f"📊 Found {len(data)} topics")

        return data
    except Exception as e:
        print(f"❌ Error loading data file: {e}")
        return None


def sanitize_class_name(topic_name):
    """Convert topic name to valid Weaviate class name."""
    import re

    sanitized = re.sub(r"[^a-zA-Z0-9]", "", topic_name)
    if sanitized:
        return sanitized[0].upper() + sanitized[1:]
    return "Unknown"


def create_collection_with_vectorizer(client, topic_name):
    """Create a collection with OpenAI vectorizer."""
    class_name = sanitize_class_name(topic_name)

    try:
        # Check if collection already exists
        if client.collections.exists(class_name):
            print(f"ℹ️  Collection {class_name} already exists")
            return class_name

        # Create collection with OpenAI vectorizer
        client.collections.create(
            name=class_name,
            description=f"Q&A pairs for {topic_name} from SQuAD dataset",
            properties=[
                Property(
                    name="question",
                    data_type=DataType.TEXT,
                    description="The question text",
                    skip_vectorization=False,
                ),
                Property(
                    name="answer",
                    data_type=DataType.TEXT,
                    description="The answer text",
                    skip_vectorization=False,
                ),
                Property(
                    name="context",
                    data_type=DataType.TEXT,
                    description="The context passage",
                    skip_vectorization=False,
                ),
                Property(
                    name="qa_id",
                    data_type=DataType.INT,
                    description="Unique identifier for Q&A pair",
                    skip_vectorization=True,
                ),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_openai(
                model="text-embedding-3-small"
            ),
        )

        print(
            f"✅ Created collection: {class_name} (with OpenAI text-embedding-3-small)"
        )
        return class_name

    except Exception as e:
        print(f"❌ Error creating collection {class_name}: {e}")
        return None


def embed_topic_data(client, topic_data):
    """Embed Q&A data for a topic into Weaviate."""
    topic = topic_data.get("topic", "")
    context = topic_data.get("context", "")
    qa_pairs = topic_data.get("qa_pairs", [])

    print(f"\n📝 Processing topic: {topic}")

    # Create collection for this topic
    class_name = create_collection_with_vectorizer(client, topic)
    if not class_name:
        return False

    # Get collection
    collection = client.collections.get(class_name)

    success_count = 0

    for qa in qa_pairs:
        try:
            data_object = {
                "question": qa.get("question", ""),
                "answer": qa.get("answer", ""),
                "context": context,
                "qa_id": qa.get("id", 0),
            }

            collection.data.insert(properties=data_object)
            success_count += 1

            if success_count % 10 == 0:
                print(f"   Embedded {success_count}/{len(qa_pairs)} Q&A pairs...")

        except Exception as e:
            print(f"   ❌ Error embedding Q&A pair {qa.get('id', 'unknown')}: {e}")

    print(f"✅ Successfully embedded {success_count} Q&A pairs into {class_name}")
    return True


def verify_collections(client):
    """Verify collections and their data."""
    print(f"\n📊 Verifying collections...")

    try:
        all_collections = client.collections.list_all()
        collection_names = list(all_collections.keys())

        if not collection_names:
            print("❌ No collections found")
            return False

        print(f"✅ Found {len(collection_names)} collections:")

        total_records = 0
        for collection_name in sorted(collection_names):
            try:
                collection = client.collections.get(collection_name)
                count_response = collection.aggregate.over_all(total_count=True)
                count = count_response.total_count
                total_records += count
                print(f"   📂 {collection_name}: {count} records")
            except Exception as e:
                print(f"   ❌ Error getting stats for {collection_name}: {e}")

        print(f"\n📊 Total records embedded: {total_records}")
        return True

    except Exception as e:
        print(f"❌ Error verifying collections: {e}")
        return False


def main():
    """Main function to load and embed data."""
    print("=== SQuAD Data Loader & Embedder ===")
    print("Loading data and embedding with OpenAI models\n")

    # Connect to Weaviate
    client = connect_to_weaviate()
    if not client:
        return

    try:
        # Load data
        data_file = "assets/data/squad_train_100qa.json"
        squad_data = load_squad_data(data_file)
        if not squad_data:
            return

        print(f"\n🚀 Starting embedding process...")

        # Embed each topic
        total_embedded = 0
        successful_topics = 0

        for topic_data in squad_data:
            if embed_topic_data(client, topic_data):
                successful_topics += 1
                total_embedded += len(topic_data.get("qa_pairs", []))

        print(f"\n✅ Embedding complete!")
        print(
            f"📊 Successfully embedded {total_embedded} Q&A pairs across {successful_topics} collections"
        )

        # Verify collections
        verify_collections(client)

        print(
            f"\n🎉 All done! Your SQuAD data is now embedded in Weaviate with OpenAI embeddings!"
        )

    finally:
        client.close()


if __name__ == "__main__":
    main()
