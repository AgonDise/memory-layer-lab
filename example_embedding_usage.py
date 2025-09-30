#!/usr/bin/env python3
"""
Quick example: How to use embeddings with memory layers.
"""

from utils import FakeEmbeddingGenerator, get_embedder
from core import ShortTermMemory, MidTermMemory

def main():
    print("=" * 60)
    print("Example: Using Embeddings with Memory Layers")
    print("=" * 60)
    
    # 1. Create embedding generator
    print("\n1️⃣  Create Embedding Generator")
    embedder = FakeEmbeddingGenerator(embedding_dim=384)
    print("✓ Created FakeEmbeddingGenerator (dim=384)")
    
    # 2. Generate embeddings
    print("\n2️⃣  Generate Embeddings")
    texts = [
        "Analyze the login_user function",
        "The function handles authentication",
        "How does OAuth2 work?"
    ]
    
    embeddings = {}
    for text in texts:
        emb = embedder.generate(text)
        embeddings[text] = emb
        print(f"  '{text[:40]}...' → embedding[{len(emb)}]")
    
    # 3. Add to Short-term Memory
    print("\n3️⃣  Add to Short-term Memory")
    stm = ShortTermMemory(max_size=10)
    
    stm.add(
        role='user',
        content=texts[0],
        embedding=embeddings[texts[0]]
    )
    stm.add(
        role='assistant',
        content=texts[1],
        embedding=embeddings[texts[1]]
    )
    stm.add(
        role='user',
        content=texts[2],
        embedding=embeddings[texts[2]]
    )
    
    print(f"✓ Added {len(stm.messages)} messages to STM")
    
    # 4. Search by embedding
    print("\n4️⃣  Search by Embedding")
    query = "authentication and login"
    query_emb = embedder.generate(query)
    
    results = stm.search_by_embedding(query_emb, top_k=3)
    
    print(f"\nQuery: '{query}'")
    print(f"Found {len(results)} results:\n")
    
    for i, msg in enumerate(results, 1):
        score = msg.get('relevance_score', msg.get('similarity', 0))
        print(f"  {i}. [{msg['role']}] Score: {score:.3f}")
        print(f"     {msg['content'][:60]}...")
    
    # 5. Add to Mid-term Memory
    print("\n5️⃣  Add to Mid-term Memory")
    mtm = MidTermMemory(max_size=100)
    
    summary = "Discussion about login_user function and authentication"
    summary_emb = embedder.generate(summary)
    
    mtm.add_chunk(
        summary=summary,
        metadata={
            'embedding': summary_emb,
            'file': 'auth_service.py',
            'function': 'login_user',
            'topic': 'authentication'
        }
    )
    
    print(f"✓ Added chunk to MTM")
    
    # 6. Search MTM
    print("\n6️⃣  Search Mid-term Memory")
    mtm_results = mtm.search_by_embedding(query_emb, top_k=2)
    
    print(f"\nQuery: '{query}'")
    print(f"Found {len(mtm_results)} results:\n")
    
    for i, chunk in enumerate(mtm_results, 1):
        score = chunk.get('relevance_score', chunk.get('similarity', 0))
        print(f"  {i}. Score: {score:.3f}")
        print(f"     {chunk['summary'][:60]}...")
        print(f"     Metadata: {chunk['metadata'].get('file', 'N/A')}")
    
    # 7. Calculate similarity between texts
    print("\n7️⃣  Calculate Similarity")
    text_a = "login authentication"
    text_b = "user login system"
    text_c = "database query"
    
    emb_a = embedder.generate(text_a)
    emb_b = embedder.generate(text_b)
    emb_c = embedder.generate(text_c)
    
    sim_ab = embedder.cosine_similarity(emb_a, emb_b)
    sim_ac = embedder.cosine_similarity(emb_a, emb_c)
    
    print(f"\n  '{text_a}' vs '{text_b}'")
    print(f"  → Similarity: {sim_ab:.3f}")
    
    print(f"\n  '{text_a}' vs '{text_c}'")
    print(f"  → Similarity: {sim_ac:.3f}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"✓ Generated {len(embeddings)} embeddings")
    print(f"✓ STM: {len(stm.messages)} messages")
    print(f"✓ MTM: {len(mtm.chunks)} chunks")
    print(f"✓ Cache: {embedder.get_cache_size()} items")
    
    print("\n💡 Key Points:")
    print("  • Same text → same embedding (reproducible)")
    print("  • Similar texts → higher similarity score")
    print("  • Embeddings enable semantic search")
    print("  • Works with all memory layers (STM, MTM, LTM)")
    
    print("\n✅ Example complete!")
    print("\nNext steps:")
    print("  • Try with your own data")
    print("  • Run: python populate_from_schema.py")
    print("  • Read: POPULATE_DATA_GUIDE.md")

if __name__ == '__main__':
    main()
