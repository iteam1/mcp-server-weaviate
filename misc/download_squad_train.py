#!/usr/bin/env python3
"""
Script to download 100 questions from 4 topics from SQuAD train dataset.
"""

import requests
import json
import os

def download_squad_train_data():
    """Download the SQuAD v1.1 train dataset."""
    print("Downloading SQuAD v1.1 train dataset...")
    
    url = "https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v1.1.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        squad_data = response.json()
        print("Downloaded train dataset successfully")
        return squad_data
    except Exception as e:
        print(f"Error downloading train dataset: {e}")
        return None

def extract_topics_and_qa(squad_data, num_topics=4, qa_per_topic=25):
    """Extract topics and Q&A pairs from SQuAD data."""
    converted_data = []
    
    articles = squad_data.get('data', [])
    
    # Get unique topics
    unique_topics = {}
    topic_count = 0
    
    for article in articles:
        title = article.get('title', '').replace('_', ' ')
        
        # Skip if we already have this topic or reached our limit
        if title in unique_topics or topic_count >= num_topics:
            continue
        
        # Collect all Q&A pairs for this topic
        topic_qa_pairs = []
        
        for paragraph in article.get('paragraphs', []):
            context = paragraph.get('context', '')
            qas = paragraph.get('qas', [])
            
            for qa in qas:
                if len(topic_qa_pairs) >= qa_per_topic:
                    break
                
                question = qa.get('question', '')
                answers = qa.get('answers', [])
                
                if answers:
                    answer = answers[0].get('text', '')
                    
                    topic_qa_pairs.append({
                        "id": len(converted_data) * 100 + len(topic_qa_pairs) + 1,
                        "question": question,
                        "answer": answer
                    })
            
            if len(topic_qa_pairs) >= qa_per_topic:
                break
        
        # Add topic if we have enough Q&A pairs
        if len(topic_qa_pairs) >= 5:  # Minimum 5 Q&A pairs
            # Use the first context for this topic
            first_context = article.get('paragraphs', [{}])[0].get('context', '')
            
            converted_data.append({
                "topic": title,
                "context": first_context,
                "qa_pairs": topic_qa_pairs[:qa_per_topic]  # Limit to requested number
            })
            
            unique_topics[title] = True
            topic_count += 1
            
            print(f"✓ Added topic: {title} ({len(topic_qa_pairs[:qa_per_topic])} Q&A pairs)")
            
            if topic_count >= num_topics:
                break
    
    return converted_data

def main():
    """Main function to download and process SQuAD data."""
    print("=== SQuAD Train Dataset Downloader ===")
    print("Target: 100 questions from 4 topics (25 per topic)")
    
    # Download the dataset
    squad_data = download_squad_train_data()
    if not squad_data:
        print("Failed to download SQuAD dataset")
        return
    
    # Extract topics and Q&A
    print("\nExtracting topics and Q&A pairs...")
    converted_data = extract_topics_and_qa(squad_data, num_topics=4, qa_per_topic=25)
    
    # Save the data
    output_file = "assets/data/squad_train_100qa.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, indent=2, ensure_ascii=False)
    
    total_qa = sum(len(topic['qa_pairs']) for topic in converted_data)
    
    print(f"\n✅ Success!")
    print(f"📁 Saved to: {output_file}")
    print(f"📊 Topics: {len(converted_data)}")
    print(f"❓ Total Q&A pairs: {total_qa}")
    
    print(f"\n📋 Topics downloaded:")
    for i, topic in enumerate(converted_data, 1):
        print(f"  {i}. {topic['topic']} ({len(topic['qa_pairs'])} Q&A pairs)")

if __name__ == "__main__":
    main()
