from typing import Optional, Dict, Any
from core.orchestrator import MemoryOrchestrator
from core.synthesizer import ResponseSynthesizer
from .response import ResponseGenerator
import logging

logger = logging.getLogger(__name__)

class ChatBot:
    """
    Main chatbot class that integrates memory layers and response generation.
    """
    
    def __init__(self, 
                 orchestrator: MemoryOrchestrator,
                 response_generator: ResponseGenerator,
                 synthesizer: Optional[ResponseSynthesizer] = None,
                 bot_name: str = "Assistant",
                 use_advanced_workflow: bool = True):
        """
        Initialize the chatbot.
        
        Args:
            orchestrator: Memory orchestrator instance
            response_generator: Response generator instance
            synthesizer: Response synthesizer instance
            bot_name: Name of the bot
            use_advanced_workflow: Use advanced memory workflow
        """
        self.orchestrator = orchestrator
        self.response_generator = response_generator
        self.synthesizer = synthesizer or ResponseSynthesizer()
        self.bot_name = bot_name
        self.use_advanced_workflow = use_advanced_workflow
        self.conversation_active = False
    
    def start(self) -> str:
        """
        Start a new conversation.
        
        Returns:
            Greeting message
        """
        self.conversation_active = True
        greeting = f"Hello! I'm {self.bot_name}. How can I help you today?"
        logger.info("Conversation started")
        return greeting
    
    def chat(self, user_message: str, use_embedding_search: bool = False) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: The user's input message
            use_embedding_search: Use embedding-based context retrieval
            
        Returns:
            Bot's response
        """
        if not self.conversation_active:
            self.start()
        
        # Preprocess input
        if self.use_advanced_workflow:
            query_obj = self.orchestrator.preprocessor.preprocess(user_message)
            logger.debug(f"Query intent: {query_obj['intent']}")
            
            # Add user message with embedding
            self.orchestrator.add_message(
                'user', 
                user_message,
                embedding=query_obj['embedding'],
                intent=query_obj['intent'],
                keywords=query_obj['keywords']
            )
        else:
            # Simple mode
            self.orchestrator.add_message('user', user_message)
        
        logger.debug(f"User: {user_message}")
        
        # Get context from memory layers
        if self.use_advanced_workflow:
            context_result = self.orchestrator.get_context(
                query=user_message,
                use_embedding_search=use_embedding_search
            )
            context_string = self.orchestrator.compressor.get_context_string(
                context_result['compressed']
            )
            context_metadata = context_result['compressed']
        else:
            context_string = self.orchestrator.get_context_string()
            context_metadata = None
        
        # Generate response
        raw_response = self.response_generator.generate(user_message, context_string)
        
        # Synthesize final response
        if self.use_advanced_workflow and context_metadata:
            query_info = query_obj if self.use_advanced_workflow else None
            response_dict = self.synthesizer.synthesize(
                raw_response,
                context_metadata=context_metadata,
                query_info=query_info
            )
            response = response_dict['response']
        else:
            response = raw_response
        
        # Add assistant response to memory
        self.orchestrator.add_message('assistant', response)
        logger.debug(f"Assistant: {response}")
        
        return response
    
    def end(self) -> str:
        """
        End the conversation.
        
        Returns:
            Farewell message
        """
        self.conversation_active = False
        farewell = "Thank you for chatting with me. Goodbye!"
        logger.info("Conversation ended")
        return farewell
    
    def reset(self) -> None:
        """Reset the chatbot and clear all memory."""
        self.orchestrator.clear_all()
        self.conversation_active = False
        logger.info("Chatbot reset - all memory cleared")
    
    def get_memory_snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of the current memory state.
        
        Returns:
            Dictionary containing memory state
        """
        return self.orchestrator.to_dict()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current conversation.
        
        Returns:
            Dictionary with conversation statistics
        """
        memory_state = self.orchestrator.to_dict()
        
        return {
            'bot_name': self.bot_name,
            'conversation_active': self.conversation_active,
            'short_term_messages': len(memory_state['short_term']['messages']),
            'mid_term_chunks': len(memory_state['mid_term']['chunks']),
            'message_count': memory_state['message_count'],
        }
