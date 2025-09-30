#!/usr/bin/env python3
"""
Main entry point for the Memory Layer Lab chatbot.
"""

import sys
from config import get_config
from core import (
    ShortTermMemory, MidTermMemory, LongTermMemory, 
    Summarizer, MemoryOrchestrator,
    InputPreprocessor, MemoryAggregator, ContextCompressor, ResponseSynthesizer
)
from bot import ChatBot, ResponseGenerator
from utils import setup_logger, MemoryStorage

def create_chatbot(config: dict, use_advanced_workflow: bool = True) -> ChatBot:
    """
    Create and configure a chatbot instance.
    
    Args:
        config: Configuration dictionary
        use_advanced_workflow: Use advanced memory workflow with embeddings
        
    Returns:
        Configured ChatBot instance
    """
    # Initialize memory layers
    short_term = ShortTermMemory(
        max_size=config['memory']['short_term']['max_size'],
        ttl_seconds=config['memory']['short_term']['ttl']
    )
    
    mid_term = MidTermMemory(
        max_size=config['memory']['mid_term']['max_size']
    )
    
    long_term = LongTermMemory(
        enabled=config['memory']['long_term']['enabled']
    )
    
    # Initialize core components
    summarizer = Summarizer(strategy='simple')
    preprocessor = InputPreprocessor(embedding_dim=384, use_mock_embeddings=True)
    aggregator = MemoryAggregator(stm_weight=0.5, mtm_weight=0.3, ltm_weight=0.2)
    compressor = ContextCompressor(max_tokens=2000, strategy='score_based')
    
    # Initialize orchestrator
    orchestrator = MemoryOrchestrator(
        short_term=short_term,
        mid_term=mid_term,
        long_term=long_term,
        summarizer=summarizer,
        preprocessor=preprocessor,
        aggregator=aggregator,
        compressor=compressor,
        summarize_every=config['memory']['mid_term']['summarize_every']
    )
    
    # Initialize response components
    response_generator = ResponseGenerator(
        mode='mock',  # Change to 'llm' when API is configured
        llm_config=config['llm']
    )
    
    synthesizer = ResponseSynthesizer(output_format='markdown')
    
    # Create chatbot
    chatbot = ChatBot(
        orchestrator=orchestrator,
        response_generator=response_generator,
        synthesizer=synthesizer,
        bot_name="MemoryBot",
        use_advanced_workflow=use_advanced_workflow
    )
    
    return chatbot

def run_interactive(chatbot: ChatBot, storage: MemoryStorage):
    """
    Run the chatbot in interactive mode.
    
    Args:
        chatbot: ChatBot instance
        storage: MemoryStorage instance
    """
    print("=" * 60)
    print(chatbot.start())
    print("=" * 60)
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'stats' to see conversation statistics")
    print("Type 'reset' to clear all memory")
    print("=" * 60)
    print()
    
    try:
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print(f"\n{chatbot.bot_name}: {chatbot.end()}")
                # Save memory state before exiting
                storage.save(chatbot.get_memory_snapshot())
                print("\nMemory state saved. Goodbye!")
                break
            
            elif user_input.lower() == 'stats':
                stats = chatbot.get_stats()
                print(f"\n--- Conversation Statistics ---")
                print(f"Bot Name: {stats['bot_name']}")
                print(f"Active: {stats['conversation_active']}")
                print(f"Short-term messages: {stats['short_term_messages']}")
                print(f"Mid-term chunks: {stats['mid_term_chunks']}")
                print(f"Message counter: {stats['message_count']}")
                print("-------------------------------\n")
                continue
            
            elif user_input.lower() == 'reset':
                chatbot.reset()
                print(f"\n{chatbot.bot_name}: Memory cleared. Starting fresh!\n")
                continue
            
            # Get bot response
            response = chatbot.chat(user_input)
            print(f"\n{chatbot.bot_name}: {response}\n")
    
    except KeyboardInterrupt:
        print(f"\n\n{chatbot.bot_name}: {chatbot.end()}")
        storage.save(chatbot.get_memory_snapshot())
        print("\nMemory state saved. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

def main():
    """Main function."""
    # Load configuration
    config = get_config()
    
    # Setup logger
    logger = setup_logger(
        name='memory_layer',
        level=config['logging']['level'],
        log_format=config['logging']['format'],
        log_file=config['logging']['file']
    )
    
    logger.info("Starting Memory Layer Lab chatbot")
    
    # Initialize storage
    storage = MemoryStorage(
        storage_type='file',
        storage_path='memory_state.json'
    )
    
    # Create chatbot
    chatbot = create_chatbot(config)
    
    # Load previous memory state if exists
    if storage.exists():
        print("Found existing memory state. Loading...")
        # TODO: Implement memory state restoration from storage
    
    # Run interactive chatbot
    run_interactive(chatbot, storage)

if __name__ == '__main__':
    main()
