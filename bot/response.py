from typing import Dict, Any, Optional
import random
import logging

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Generates responses for the chatbot.
    
    This can be configured to use different response strategies:
    - Mock responses (for testing)
    - LLM-based responses (OpenAI, Anthropic, etc.)
    - Rule-based responses
    """
    
    def __init__(self, mode: str = 'mock', llm_config: Optional[Dict[str, Any]] = None, llm_client=None):
        """
        Initialize the response generator.
        
        Args:
            mode: Response mode ('mock', 'llm', 'rule-based')
            llm_config: Configuration for LLM-based responses
            llm_client: LLM client instance (optional)
        """
        self.mode = mode
        self.llm_config = llm_config or {}
        self.llm_client = llm_client
    
    def generate(self, user_message: str, context: str = "") -> str:
        """
        Generate a response to the user's message.
        
        Args:
            user_message: The user's input message
            context: Context from memory layers
            
        Returns:
            Generated response string
        """
        if self.mode == 'mock':
            return self._mock_response(user_message, context)
        elif self.mode == 'llm':
            return self._llm_response(user_message, context)
        elif self.mode == 'rule-based':
            return self._rule_based_response(user_message, context)
        else:
            return self._mock_response(user_message, context)
    
    def _mock_response(self, user_message: str, context: str) -> str:
        """
        Generate a mock response for testing.
        
        Args:
            user_message: The user's input
            context: Memory context
            
        Returns:
            Mock response string
        """
        responses = [
            f"I understand you said: '{user_message}'. Let me think about that.",
            f"That's interesting! Regarding '{user_message}', here's what I think...",
            f"Thanks for sharing that. About '{user_message}', I can help with that.",
            f"I hear you. Let me process '{user_message}' in context of our conversation.",
        ]
        
        response = random.choice(responses)
        
        if context:
            response += f"\n\n(Context: I remember we discussed some things earlier.)"
        
        return response
    
    def _llm_response(self, user_message: str, context: str) -> str:
        """
        Generate a response using an LLM API.
        
        Args:
            user_message: The user's input
            context: Memory context
            
        Returns:
            LLM-generated response
        """
        if not self.llm_client:
            logger.warning("No LLM client configured, using mock response")
            return f"[LLM Response to: {user_message}] (LLM client not configured)"
        
        try:
            # Build prompt with context
            if context:
                prompt = f"""Context from memory:
{context}

User question: {user_message}

Please provide a helpful response based on the context above."""
            else:
                prompt = user_message
            
            # Get system prompt from config
            system_prompt = self.llm_config.get('system_prompt', 
                'You are a helpful AI assistant.')
            
            # Generate response using LLM
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=self.llm_config.get('max_tokens', 500),
                temperature=self.llm_config.get('temperature', 0.7)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"[Error generating response: {str(e)}]"
    
    def _rule_based_response(self, user_message: str, context: str) -> str:
        """
        Generate a response using rule-based logic.
        
        Args:
            user_message: The user's input
            context: Memory context
            
        Returns:
            Rule-based response
        """
        message_lower = user_message.lower()
        
        # Simple keyword matching
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! How can I help you today?"
        
        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
            return "Goodbye! Have a great day!"
        
        elif 'help' in message_lower:
            return "I'm here to help! What do you need assistance with?"
        
        elif '?' in user_message:
            return "That's a good question. Let me think about that..."
        
        else:
            return "I understand. Please tell me more."
