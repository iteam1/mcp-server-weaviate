#!/usr/bin/env python3
"""
Pytest tests for OpenAI connection and model functionality.
Tests GPT model and embedding model.
"""

import os
import pytest
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


@pytest.fixture
def openai_client():
    """Create and return an OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key, "OPENAI_API_KEY environment variable is not set"
    
    client = OpenAI(api_key=api_key)
    return client


class TestOpenAIConnection:
    """Test OpenAI connection and basic functionality."""
    
    def test_openai_api_key_exists(self):
        """Test that OPENAI_API_KEY environment variable is set."""
        api_key = os.getenv("OPENAI_API_KEY")
        assert api_key is not None, "OPENAI_API_KEY environment variable is not set"
        assert len(api_key) > 0, "OPENAI_API_KEY is empty"
        print(f"✅ OpenAI API key found (length: {len(api_key)})")
    
    def test_openai_client_creation(self, openai_client):
        """Test that OpenAI client can be created."""
        assert openai_client is not None, "Failed to create OpenAI client"
        print("✅ OpenAI client created successfully")
    
    def test_gpt_model_call(self, openai_client):
        """Test calling GPT model (gpt-4o-mini)."""
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": "Say 'Hello from OpenAI GPT model' in exactly one sentence."
                    }
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            assert response is not None, "No response from GPT model"
            assert response.choices is not None, "No choices in response"
            assert len(response.choices) > 0, "Empty choices list"
            
            message = response.choices[0].message.content
            assert message is not None, "No message content in response"
            assert len(message) > 0, "Empty message content"
            
            print(f"✅ GPT model response: {message}")
            
        except Exception as e:
            pytest.fail(f"❌ Failed to call GPT model: {e}")
    
    def test_embedding_model_call(self, openai_client):
        """Test calling embedding model (text-embedding-3-small)."""
        try:
            test_text = "This is a test sentence for embedding"
            
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=test_text
            )
            
            assert response is not None, "No response from embedding model"
            assert response.data is not None, "No data in response"
            assert len(response.data) > 0, "Empty data list"
            
            embedding = response.data[0].embedding
            assert embedding is not None, "No embedding in response"
            assert len(embedding) > 0, "Empty embedding vector"
            
            print(f"✅ Embedding model response: vector of length {len(embedding)}")
            print(f"   First 5 dimensions: {embedding[:5]}")
            
        except Exception as e:
            pytest.fail(f"❌ Failed to call embedding model: {e}")
    
    def test_embedding_model_multiple_texts(self, openai_client):
        """Test embedding model with multiple texts."""
        try:
            texts = [
                "What is machine learning?",
                "How does neural network work?",
                "Explain deep learning"
            ]
            
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            
            assert response is not None, "No response from embedding model"
            assert len(response.data) == len(texts), "Number of embeddings doesn't match input"
            
            for i, embedding_obj in enumerate(response.data):
                embedding = embedding_obj.embedding
                assert len(embedding) > 0, f"Empty embedding for text {i}"
            
            print(f"✅ Successfully embedded {len(texts)} texts")
            print(f"   Embedding dimension: {len(response.data[0].embedding)}")
            
        except Exception as e:
            pytest.fail(f"❌ Failed to embed multiple texts: {e}")
    
    def test_gpt_model_with_context(self, openai_client):
        """Test GPT model with context (Q&A style)."""
        try:
            context = "The University of Notre Dame is a Catholic research university located in Notre Dame, Indiana."
            question = "Where is the University of Notre Dame located?"
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on the provided context."
                    },
                    {
                        "role": "user",
                        "content": f"Context: {context}\n\nQuestion: {question}"
                    }
                ],
                max_tokens=100,
                temperature=0.5
            )
            
            assert response is not None, "No response from GPT model"
            answer = response.choices[0].message.content
            assert answer is not None, "No answer in response"
            assert len(answer) > 0, "Empty answer"
            
            print(f"✅ GPT Q&A response: {answer}")
            
        except Exception as e:
            pytest.fail(f"❌ Failed Q&A with GPT model: {e}")
    
    def test_embedding_similarity(self, openai_client):
        """Test embedding similarity between related texts."""
        try:
            import math
            
            texts = [
                "The cat is on the mat",
                "The dog is on the rug",
                "The feline is resting on the carpet"
            ]
            
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            
            embeddings = [obj.embedding for obj in response.data]
            
            # Calculate cosine similarity
            def cosine_similarity(vec1, vec2):
                dot_product = sum(a * b for a, b in zip(vec1, vec2))
                magnitude1 = math.sqrt(sum(a ** 2 for a in vec1))
                magnitude2 = math.sqrt(sum(b ** 2 for b in vec2))
                return dot_product / (magnitude1 * magnitude2) if magnitude1 * magnitude2 != 0 else 0
            
            # Similarity between text 0 and 1 (different subjects)
            sim_01 = cosine_similarity(embeddings[0], embeddings[1])
            
            # Similarity between text 0 and 2 (same subject, different wording)
            sim_02 = cosine_similarity(embeddings[0], embeddings[2])
            
            print(f"✅ Embedding similarity test:")
            print(f"   Similarity (cat-dog): {sim_01:.4f}")
            print(f"   Similarity (cat-cat different wording): {sim_02:.4f}")
            print(f"   Texts with similar meaning have higher similarity: {sim_02 > sim_01}")
            
            # Texts with similar meaning should have higher similarity
            assert sim_02 > sim_01, "Similar texts should have higher similarity"
            
        except Exception as e:
            pytest.fail(f"❌ Failed embedding similarity test: {e}")


class TestOpenAIModels:
    """Test specific OpenAI models."""
    
    def test_gpt_4o_mini_model_exists(self, openai_client):
        """Test that gpt-4o-mini model is accessible."""
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            assert response is not None
            print("✅ gpt-4o-mini model is accessible")
        except Exception as e:
            pytest.fail(f"❌ gpt-4o-mini model not accessible: {e}")
    
    def test_text_embedding_3_small_model_exists(self, openai_client):
        """Test that text-embedding-3-small model is accessible."""
        try:
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input="test"
            )
            assert response is not None
            assert len(response.data) > 0
            print("✅ text-embedding-3-small model is accessible")
        except Exception as e:
            pytest.fail(f"❌ text-embedding-3-small model not accessible: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
