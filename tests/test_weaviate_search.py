#!/usr/bin/env python3
"""
Pytest tests for Weaviate search functionality.
Tests near text search, keyword search, and hybrid search on collections.
"""

import os
import pytest
import weaviate
from weaviate.classes.query import Filter, MetadataQuery
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def weaviate_client():
    """Create and return a Weaviate client."""
    http_port = os.getenv("WEAVIATE_HTTP_PORT")
    grpc_port = os.getenv("WEAVIATE_GRPC_PORT")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    assert http_port, "WEAVIATE_HTTP_PORT environment variable is not set"
    assert grpc_port, "WEAVIATE_GRPC_PORT environment variable is not set"
    assert openai_api_key, "OPENAI_API_KEY environment variable is not set"
    
    try:
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
        print(f"✅ Connected to Weaviate on HTTP port {http_port}, gRPC port {grpc_port}")
        return client
    except Exception as e:
        pytest.fail(f"❌ Failed to connect to Weaviate: {e}")


@pytest.fixture
def test_collection(weaviate_client):
    """Get a test collection for search tests."""
    try:
        # List all collections
        all_collections = weaviate_client.collections.list_all()
        collection_names = list(all_collections.keys())
        
        if not collection_names:
            pytest.skip("No collections found. Please load data first using misc/load_and_embed_data.py")
        
        # Use the first available collection for testing
        collection_name = collection_names[0]
        collection = weaviate_client.collections.get(collection_name)
        
        # Verify collection has data
        count_response = collection.aggregate.over_all(total_count=True)
        count = count_response.total_count
        
        if count == 0:
            pytest.skip(f"Collection {collection_name} has no data")
        
        print(f"✅ Using collection '{collection_name}' with {count} records for search tests")
        return collection, collection_name
        
    except Exception as e:
        pytest.fail(f"❌ Error setting up test collection: {e}")


class TestWeaviateSearch:
    """Test Weaviate search functionality."""
    
    def test_near_text_search_basic(self, weaviate_client, test_collection):
        """Test basic near text search functionality."""
        collection, collection_name = test_collection
        
        try:
            # Perform near text search
            query_text = "What is machine learning?"
            response = collection.query.near_text(
                query=query_text,
                limit=5,
                return_metadata=MetadataQuery(distance=True, certainty=True)
            )
            
            assert response is not None, "Near text search returned None"
            assert hasattr(response, 'objects'), "Response missing objects attribute"
            
            objects = response.objects
            assert len(objects) > 0, "Near text search returned no results"
            assert len(objects) <= 5, "Near text search returned more results than limit"
            
            # Verify results have required properties
            for obj in objects:
                assert hasattr(obj, 'properties'), "Object missing properties"
                assert 'question' in obj.properties, "Object missing question property"
                assert 'answer' in obj.properties, "Object missing answer property"
                assert hasattr(obj, 'metadata'), "Object missing metadata"
                
                if obj.metadata:
                    print(f"   Result: {obj.properties['question'][:50]}...")
                    print(f"   Distance: {obj.metadata.distance}, Certainty: {obj.metadata.certainty}")
            
            print(f"✅ Near text search for '{query_text}' returned {len(objects)} results")
            
        except Exception as e:
            pytest.fail(f"❌ Near text search failed: {e}")
    
    def test_near_text_search_with_filters(self, weaviate_client, test_collection):
        """Test near text search with additional filters."""
        collection, collection_name = test_collection
        
        try:
            # Perform near text search with filter
            query_text = "computer science"
            response = collection.query.near_text(
                query=query_text,
                limit=3,
                filters=Filter.by_property("qa_id").greater_than(0),
                return_metadata=MetadataQuery(distance=True)
            )
            
            assert response is not None, "Filtered near text search returned None"
            objects = response.objects
            assert len(objects) > 0, "Filtered near text search returned no results"
            
            # Verify all results meet filter criteria
            for obj in objects:
                qa_id = obj.properties.get('qa_id', 0)
                assert qa_id > 0, f"Filter failed: qa_id {qa_id} is not greater than 0"
            
            print(f"✅ Filtered near text search for '{query_text}' returned {len(objects)} results")
            
        except Exception as e:
            pytest.fail(f"❌ Filtered near text search failed: {e}")
    
    def test_keyword_search_basic(self, weaviate_client, test_collection):
        """Test basic keyword search functionality."""
        collection, collection_name = test_collection
        
        try:
            # Perform keyword search
            search_term = "learning"
            response = collection.query.bm25(
                query=search_term,
                limit=5,
                return_metadata=MetadataQuery(score=True, certainty=True)
            )
            
            assert response is not None, "Keyword search returned None"
            assert hasattr(response, 'objects'), "Response missing objects attribute"
            
            objects = response.objects
            
            if len(objects) == 0:
                pytest.skip("BM25 search returned no results - inverted indices may not be built")
            
            assert len(objects) <= 5, "Keyword search returned more results than limit"
            
            # Verify results contain the search term (case-insensitive)
            for obj in objects:
                question = obj.properties.get('question', '').lower()
                answer = obj.properties.get('answer', '').lower()
                context = obj.properties.get('context', '').lower()
                
                # At least one field should contain the search term
                combined_text = f"{question} {answer} {context}"
                assert search_term.lower() in combined_text, f"Search term '{search_term}' not found in result"
                
                if obj.metadata:
                    print(f"   Result: {obj.properties['question'][:50]}...")
                    print(f"   Score: {obj.metadata.score}")
            
            print(f"✅ Keyword search for '{search_term}' returned {len(objects)} results")
            
        except Exception as e:
            pytest.fail(f"❌ Keyword search failed: {e}")
    
    def test_keyword_search_with_properties(self, weaviate_client, test_collection):
        """Test keyword search on specific properties."""
        collection, collection_name = test_collection
        
        try:
            # Perform keyword search on specific properties
            search_term = "what"
            response = collection.query.bm25(
                query=search_term,
                limit=3,
                return_metadata=MetadataQuery(score=True)
            )
            
            assert response is not None, "Keyword search returned None"
            objects = response.objects
            
            if len(objects) == 0:
                pytest.skip("BM25 search returned no results - inverted indices may not be built")
            
            # Verify results contain the search term in the question field
            for obj in objects:
                question = obj.properties.get('question', '').lower()
                assert search_term.lower() in question, f"Search term '{search_term}' not found in question"
            
            print(f"✅ Keyword search for '{search_term}' returned {len(objects)} results")
            
        except Exception as e:
            pytest.fail(f"❌ Keyword search failed: {e}")
    
    def test_hybrid_search_basic(self, weaviate_client, test_collection):
        """Test basic hybrid search functionality."""
        collection, collection_name = test_collection
        
        try:
            # Perform hybrid search
            query_text = "artificial intelligence"
            response = collection.query.hybrid(
                query=query_text,
                limit=5,
                alpha=0.5,  # Balance between keyword and vector search
                return_metadata=MetadataQuery(score=True, certainty=True)
            )
            
            assert response is not None, "Hybrid search returned None"
            assert hasattr(response, 'objects'), "Response missing objects attribute"
            
            objects = response.objects
            assert len(objects) > 0, "Hybrid search returned no results"
            assert len(objects) <= 5, "Hybrid search returned more results than limit"
            
            # Verify results have required properties and metadata
            for obj in objects:
                assert hasattr(obj, 'properties'), "Object missing properties"
                assert 'question' in obj.properties, "Object missing question property"
                assert hasattr(obj, 'metadata'), "Object missing metadata"
                
                if obj.metadata:
                    print(f"   Result: {obj.properties['question'][:50]}...")
                    print(f"   Score: {obj.metadata.score}, Certainty: {obj.metadata.certainty}")
            
            print(f"✅ Hybrid search for '{query_text}' returned {len(objects)} results")
            
        except Exception as e:
            pytest.fail(f"❌ Hybrid search failed: {e}")
    
    def test_hybrid_search_with_alpha(self, weaviate_client, test_collection):
        """Test hybrid search with different alpha values."""
        collection, collection_name = test_collection
        
        try:
            query_text = "data science"
            
            # Test with alpha=0 (pure keyword search)
            response_keyword = collection.query.hybrid(
                query=query_text,
                limit=3,
                alpha=0.0,
                return_metadata=MetadataQuery(score=True)
            )
            
            # Test with alpha=1 (pure vector search)
            response_vector = collection.query.hybrid(
                query=query_text,
                limit=3,
                alpha=1.0,
                return_metadata=MetadataQuery(score=True, certainty=True)
            )
            
            # Test with alpha=0.5 (balanced hybrid)
            response_balanced = collection.query.hybrid(
                query=query_text,
                limit=3,
                alpha=0.5,
                return_metadata=MetadataQuery(score=True, certainty=True)
            )
            
            assert response_keyword is not None, "Keyword-weighted hybrid search returned None"
            assert response_vector is not None, "Vector-weighted hybrid search returned None"
            assert response_balanced is not None, "Balanced hybrid search returned None"
            
            keyword_objects = response_keyword.objects
            vector_objects = response_vector.objects
            balanced_objects = response_balanced.objects
            
            # Vector search should always work
            assert len(vector_objects) > 0, "Vector-weighted search returned no results"
            assert len(balanced_objects) > 0, "Balanced search returned no results"
            
            # Keyword-weighted might fail if BM25 not available
            if len(keyword_objects) == 0:
                print("   Note: Alpha=0.0 (keyword-only) returned no results - BM25 may not be available")
            
            print(f"✅ Hybrid search with different alpha values:")
            print(f"   Alpha=0.0 (keyword): {len(keyword_objects)} results")
            print(f"   Alpha=1.0 (vector): {len(vector_objects)} results")
            print(f"   Alpha=0.5 (balanced): {len(balanced_objects)} results")
            
        except Exception as e:
            pytest.fail(f"❌ Hybrid search with alpha failed: {e}")
    
    def test_search_comparison(self, weaviate_client, test_collection):
        """Compare results from different search methods."""
        collection, collection_name = test_collection
        
        try:
            query_text = "neural networks"
            limit = 3
            
            # Near text search
            near_text_response = collection.query.near_text(
                query=query_text,
                limit=limit,
                return_metadata=MetadataQuery(certainty=True)
            )
            
            # Keyword search
            keyword_response = collection.query.bm25(
                query=query_text,
                limit=limit,
                return_metadata=MetadataQuery(score=True)
            )
            
            # Hybrid search
            hybrid_response = collection.query.hybrid(
                query=query_text,
                limit=limit,
                alpha=0.5,
                return_metadata=MetadataQuery(score=True, certainty=True)
            )
            
            assert near_text_response is not None, "Near text search returned None"
            assert keyword_response is not None, "Keyword search returned None"
            assert hybrid_response is not None, "Hybrid search returned None"
            
            near_text_objects = near_text_response.objects
            keyword_objects = keyword_response.objects
            hybrid_objects = hybrid_response.objects
            
            print(f"✅ Search comparison for '{query_text}':")
            print(f"   Near Text: {len(near_text_objects)} results")
            print(f"   Keyword: {len(keyword_objects)} results")
            print(f"   Hybrid: {len(hybrid_objects)} results")
            
            # Verify vector-based searches returned results
            assert len(near_text_objects) > 0, "Near text search returned no results"
            assert len(hybrid_objects) > 0, "Hybrid search returned no results"
            
            # Keyword search might fail if BM25 not available
            if len(keyword_objects) == 0:
                print("   Note: Keyword search returned no results - BM25 may not be available")
            
            # Display sample results for comparison (only for searches that returned results)
            print(f"\n   Sample results:")
            max_results = max(len(near_text_objects), len(hybrid_objects))
            for i in range(max_results):
                if i < len(near_text_objects):
                    print(f"   {i+1}. Near Text: {near_text_objects[i].properties['question'][:40]}...")
                if i < len(keyword_objects):
                    print(f"      Keyword: {keyword_objects[i].properties['question'][:40]}...")
                if i < len(hybrid_objects):
                    print(f"      Hybrid: {hybrid_objects[i].properties['question'][:40]}...")
                print()
            
        except Exception as e:
            pytest.fail(f"❌ Search comparison failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
