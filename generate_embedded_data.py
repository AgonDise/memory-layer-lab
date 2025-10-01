#!/usr/bin/env python3
"""
Generate test data with embeddings for MT and LT memory layers.

This script creates structured test data with pre-computed embeddings
to enable semantic search testing.
"""

import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

# Try to use real embeddings
try:
    from utils.real_embedding import RealEmbeddingGenerator
    print("✅ Using RealEmbeddingGenerator (sentence-transformers)")
    embedder = RealEmbeddingGenerator()
    use_real = True
except Exception as e:
    print(f"⚠️  RealEmbeddingGenerator not available: {e}")
    print("   Using mock embeddings")
    from utils import FakeEmbeddingGenerator
    embedder = FakeEmbeddingGenerator()
    use_real = False


# Sample conversations for different topics
CONVERSATIONS = {
    "ai_engineering": [
        "Tôi là AI Engineer, làm việc với các mô hình ngôn ngữ lớn.",
        "Công việc chính của tôi là training và fine-tuning LLM models.",
        "Tôi thường sử dụng PyTorch và Hugging Face Transformers.",
        "Vector embeddings và semantic search là kỹ năng quan trọng.",
        "RAG (Retrieval Augmented Generation) giúp cải thiện chatbot.",
    ],
    "cooking": [
        "Tôi làm đầu bếp tại nhà hàng Sasukekeke ở Nhật Bản.",
        "Món gà chiên (Karaage) là specialty của tôi.",
        "Công thức gà chiên: ướp gà với gừng, tỏi, nước tương, sake.",
        "Bí quyết là chiên 2 lần: lần 1 nhiệt độ thấp, lần 2 nhiệt độ cao.",
        "Món sushi và sashimi cũng rất được khách yêu thích.",
        "Nguyên liệu tươi sống là yếu tố quan trọng nhất.",
    ],
    "gaming": [
        "Tôi chơi Valorant rank Immortal.",
        "Main agent của tôi là Jett và Reyna.",
        "Aim training mỗi ngày 30 phút rất quan trọng.",
        "Map Ascent là map yêu thích của tôi.",
        "Team coordination và communication quyết định 70% trận đấu.",
    ],
    "technology": [
        "OpenAI GPT-4 là model mạnh nhất hiện tại.",
        "API rate limit là 10,000 requests/minute cho tier 3.",
        "Token pricing: $0.03/1K input, $0.06/1K output tokens.",
        "Streaming responses cải thiện user experience đáng kể.",
        "Fine-tuning costs $0.008/1K training tokens.",
    ],
    "travel": [
        "Tôi đã du lịch Tokyo vào mùa xuân năm ngoái.",
        "Hoa anh đào (sakura) ở công viên Ueno rất đẹp.",
        "Đi tàu điện ngầm rất tiện lợi và đúng giờ.",
        "Món ramen Ichiran là must-try khi đến Tokyo.",
        "TeamLab Borderless museum có triển lãm ánh sáng tuyệt vời.",
    ],
    "education": [
        "Tôi học chuyên ngành Computer Science tại Đại học Bách Khoa.",
        "Môn học yêu thích là Machine Learning và NLP.",
        "Thesis của tôi về Transformer architecture optimization.",
        "Đang làm research về efficient attention mechanisms.",
        "Professor Nguyen là advisor rất tốt.",
    ]
}


def generate_mid_term_chunks(num_chunks: int = 20) -> List[Dict[str, Any]]:
    """
    Generate mid-term memory chunks with embeddings.
    
    Each chunk represents a summary of 5-10 messages.
    """
    print(f"\n📦 Generating {num_chunks} Mid-Term Memory chunks...")
    
    chunks = []
    topics = list(CONVERSATIONS.keys())
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(num_chunks):
        # Pick random topic
        topic = random.choice(topics)
        topic_messages = CONVERSATIONS[topic]
        
        # Sample messages for this chunk
        num_messages = random.randint(3, 5)
        chunk_messages = random.sample(topic_messages, min(num_messages, len(topic_messages)))
        
        # Create summary
        summary = f"[{topic.replace('_', ' ').title()}] {' | '.join(chunk_messages[:2])}"
        
        # Generate embedding
        print(f"   {i+1}/{num_chunks} Embedding: {summary[:50]}...")
        embedding = embedder.generate(summary)
        
        chunk = {
            "id": f"mtm_chunk_{i+1:03d}",
            "summary": summary,
            "embedding": embedding,
            "metadata": {
                "topic": topic,
                "message_count": num_messages,
                "timestamp": (base_time + timedelta(hours=i*2)).isoformat(),
                "importance": random.uniform(0.5, 1.0),
            },
            "original_messages": chunk_messages,
        }
        chunks.append(chunk)
    
    print(f"✅ Generated {len(chunks)} MTM chunks")
    return chunks


def generate_long_term_facts(num_facts: int = 30) -> List[Dict[str, Any]]:
    """
    Generate long-term memory facts with embeddings.
    
    These are persistent knowledge items.
    """
    print(f"\n📚 Generating {num_facts} Long-Term Memory facts...")
    
    facts = [
        # Personal info
        {"fact": "Tên tôi là Innotech, AI Engineer và đầu bếp chuyên nghiệp", "category": "identity"},
        {"fact": "Tôi làm việc với LLM models và RAG systems", "category": "work"},
        {"fact": "Tôi làm đầu bếp tại nhà hàng Sasukekeke ở Nhật Bản", "category": "work"},
        {"fact": "Main agent Valorant của tôi là Jett và Reyna, rank Immortal", "category": "gaming"},
        
        # Technical knowledge
        {"fact": "RAG = Retrieval Augmented Generation, kết hợp retrieval và generation", "category": "tech"},
        {"fact": "Vector embeddings convert text thành numerical vectors", "category": "tech"},
        {"fact": "Cosine similarity đo độ tương đồng giữa hai vectors", "category": "tech"},
        {"fact": "Sentence-transformers là library tốt cho semantic search", "category": "tech"},
        {"fact": "GPT-4 context window là 128K tokens", "category": "tech"},
        {"fact": "Fine-tuning requires minimum 10 high-quality examples", "category": "tech"},
        
        # Cooking knowledge
        {"fact": "Gà chiên Nhật (Karaage) cần ướp với gừng, tỏi, nước tương", "category": "cooking"},
        {"fact": "Chiên 2 lần: lần 1 nhiệt độ 160°C, lần 2 nhiệt độ 180°C", "category": "cooking"},
        {"fact": "Sushi rice cần nêm với giấm, đường, muối theo tỷ lệ 5:2:1", "category": "cooking"},
        {"fact": "Cá ngừ (maguro) tốt nhất cho sashimi phải được bảo quản -60°C", "category": "cooking"},
        {"fact": "Wasabi thật được làm từ rễ cây wasabi, rất đắt tiền", "category": "cooking"},
        
        # Gaming knowledge
        {"fact": "Valorant có 5 roles chính: Duelist, Controller, Initiator, Sentinel", "category": "gaming"},
        {"fact": "Jett có ability dash và updraft để di chuyển nhanh", "category": "gaming"},
        {"fact": "Crosshair placement ở head level giúp tăng headshot rate", "category": "gaming"},
        {"fact": "Economy management: save round khi team có < 2000 credits", "category": "gaming"},
        {"fact": "Spike plant takes 4 seconds, defuse takes 7 seconds (4 with kit)", "category": "gaming"},
        
        # Travel knowledge
        {"fact": "Tokyo có 13 subway lines và JR Yamanote line loop", "category": "travel"},
        {"fact": "Sakura season ở Tokyo thường từ cuối tháng 3 đến đầu tháng 4", "category": "travel"},
        {"fact": "Shibuya crossing là nơi đông đúc nhất Tokyo với 2500 người/lần", "category": "travel"},
        {"fact": "Tsukiji outer market mở cửa 5am, tốt nhất đến sớm", "category": "travel"},
        {"fact": "Suica card hoạt động cho tất cả tàu điện và nhiều cửa hàng", "category": "travel"},
        
        # Education
        {"fact": "Transformer architecture gồm encoder và decoder với attention mechanism", "category": "education"},
        {"fact": "Self-attention complexity là O(n²) với n là sequence length", "category": "education"},
        {"fact": "BERT uses masked language modeling for pre-training", "category": "education"},
        {"fact": "Learning rate scheduling giúp training ổn định hơn", "category": "education"},
        {"fact": "Gradient clipping prevents exploding gradients trong RNN", "category": "education"},
    ]
    
    ltm_facts = []
    for i, fact_data in enumerate(facts[:num_facts]):
        fact = fact_data["fact"]
        category = fact_data["category"]
        
        print(f"   {i+1}/{num_facts} Embedding: {fact[:50]}...")
        embedding = embedder.generate(fact)
        
        ltm_fact = {
            "id": f"ltm_fact_{i+1:03d}",
            "content": fact,
            "embedding": embedding,
            "metadata": {
                "category": category,
                "importance": random.uniform(0.7, 1.0),
                "access_count": random.randint(1, 50),
                "last_accessed": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                "created_at": (datetime.now() - timedelta(days=random.randint(30, 180))).isoformat(),
            }
        }
        ltm_facts.append(ltm_fact)
    
    print(f"✅ Generated {len(ltm_facts)} LTM facts")
    return ltm_facts


def calculate_statistics(data: List[Dict[str, Any]], data_type: str) -> Dict[str, Any]:
    """Calculate statistics about the generated data."""
    if not data:
        return {}
    
    embedding_field = 'embedding'
    content_field = 'summary' if data_type == 'MTM' else 'content'
    
    # Get embedding dimension
    if data and embedding_field in data[0]:
        embedding_dim = len(data[0][embedding_field])
    else:
        embedding_dim = 0
    
    # Average content length
    avg_length = sum(len(item.get(content_field, '')) for item in data) / len(data)
    
    return {
        "total_items": len(data),
        "embedding_dimension": embedding_dim,
        "avg_content_length": int(avg_length),
        "has_embeddings": all(embedding_field in item for item in data),
        "categories": list(set(item.get('metadata', {}).get('category', 'unknown') for item in data if 'metadata' in item)),
    }


def main():
    """Generate all test data with embeddings."""
    
    print("=" * 80)
    print("🚀 GENERATING EMBEDDED TEST DATA FOR MEMORY LAYER LAB")
    print("=" * 80)
    
    if use_real:
        print(f"📦 Model: sentence-transformers")
        print(f"📐 Embedding dimension: {embedder.embedding_dim}")
    else:
        print(f"⚠️  Using mock embeddings (install sentence-transformers for real)")
    
    # Generate data
    mtm_chunks = generate_mid_term_chunks(num_chunks=20)
    ltm_facts = generate_long_term_facts(num_facts=30)
    
    # Calculate statistics
    mtm_stats = calculate_statistics(mtm_chunks, 'MTM')
    ltm_stats = calculate_statistics(ltm_facts, 'LTM')
    
    # Create metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "generator_version": "1.0",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2" if use_real else "mock",
        "embedding_dimension": embedder.embedding_dim,
        "statistics": {
            "mid_term": mtm_stats,
            "long_term": ltm_stats,
        }
    }
    
    # Save data
    print("\n💾 Saving data...")
    
    # Save MTM chunks
    mtm_file = "data/mid_term_chunks.json"
    with open(mtm_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": metadata,
            "chunks": mtm_chunks
        }, f, ensure_ascii=False, indent=2)
    print(f"   ✅ Saved {len(mtm_chunks)} MTM chunks to {mtm_file}")
    
    # Save LTM facts
    ltm_file = "data/long_term_facts.json"
    with open(ltm_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": metadata,
            "facts": ltm_facts
        }, f, ensure_ascii=False, indent=2)
    print(f"   ✅ Saved {len(ltm_facts)} LTM facts to {ltm_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 GENERATION SUMMARY")
    print("=" * 80)
    print(f"\n✅ Mid-Term Memory (MTM):")
    print(f"   Total chunks: {mtm_stats['total_items']}")
    print(f"   Embedding dim: {mtm_stats['embedding_dimension']}")
    print(f"   Avg length: {mtm_stats['avg_content_length']} chars")
    print(f"   Has embeddings: {mtm_stats['has_embeddings']}")
    
    print(f"\n✅ Long-Term Memory (LTM):")
    print(f"   Total facts: {ltm_stats['total_items']}")
    print(f"   Embedding dim: {ltm_stats['embedding_dimension']}")
    print(f"   Avg length: {ltm_stats['avg_content_length']} chars")
    print(f"   Has embeddings: {ltm_stats['has_embeddings']}")
    print(f"   Categories: {', '.join(ltm_stats['categories'])}")
    
    print("\n🎉 Data generation complete!")
    print("\n💡 Next steps:")
    print("   1. Run tests: python3 test_comprehensive.py")
    print("   2. Test semantic search with real queries")
    print("   3. Compare relevance scores before/after")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
