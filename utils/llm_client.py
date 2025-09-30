"""
LLM Client for integrating with OpenAI, Anthropic, etc.
"""

from typing import Dict, Any, List, Optional
import os
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """Base class for LLM clients."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM client."""
        self.api_key = api_key
        self.enabled = api_key is not None
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt."""
        raise NotImplementedError


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model to use (gpt-3.5-turbo, gpt-4, etc.)
        """
        super().__init__(api_key or os.getenv('OPENAI_API_KEY'))
        self.model = model
        
        if self.enabled:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI client initialized with model: {model}")
            except ImportError:
                logger.warning("openai package not installed. Install with: pip install openai")
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.enabled = False
    
    def generate(self, 
                prompt: str,
                system_prompt: Optional[str] = None,
                max_tokens: int = 500,
                temperature: float = 0.7,
                **kwargs) -> str:
        """
        Generate response using OpenAI.
        
        Args:
            prompt: User prompt
            system_prompt: System message (optional)
            max_tokens: Max tokens to generate
            temperature: Sampling temperature (0-2)
            
        Returns:
            Generated response text
        """
        if not self.enabled:
            return "[OpenAI not available - using mock response]"
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"[Error: {str(e)}]"


class AnthropicClient(LLMClient):
    """Anthropic Claude API client."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Model to use (claude-3-opus, claude-3-sonnet, etc.)
        """
        super().__init__(api_key or os.getenv('ANTHROPIC_API_KEY'))
        self.model = model
        
        if self.enabled:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info(f"Anthropic client initialized with model: {model}")
            except ImportError:
                logger.warning("anthropic package not installed. Install with: pip install anthropic")
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                self.enabled = False
    
    def generate(self,
                prompt: str,
                system_prompt: Optional[str] = None,
                max_tokens: int = 500,
                temperature: float = 0.7,
                **kwargs) -> str:
        """
        Generate response using Anthropic Claude.
        
        Args:
            prompt: User prompt
            system_prompt: System message (optional)
            max_tokens: Max tokens to generate
            temperature: Sampling temperature (0-1)
            
        Returns:
            Generated response text
        """
        if not self.enabled:
            return "[Anthropic not available - using mock response]"
        
        try:
            message_params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if system_prompt:
                message_params["system"] = system_prompt
            
            response = self.client.messages.create(**message_params)
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"[Error: {str(e)}]"


class MockLLMClient(LLMClient):
    """Mock LLM for testing without API keys."""
    
    def __init__(self):
        """Initialize mock client."""
        super().__init__(api_key="mock")
        self.enabled = True
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock response."""
        # Simple rule-based responses
        prompt_lower = prompt.lower()
        
        if "login" in prompt_lower or "auth" in prompt_lower:
            return """Based on the provided context, the login_user function handles user authentication by:
1. Validating user credentials
2. Creating a JWT token for authenticated sessions
3. Managing session state

Recent changes include OAuth2 integration for enhanced security."""
        
        elif "bug" in prompt_lower or "error" in prompt_lower:
            return """I found information about recent bug fixes:
- Fixed undefined variable error in checkpoints.rs
- Improved error handling in the authentication flow
- Updated validation logic

Would you like more details about any specific issue?"""
        
        elif "commit" in prompt_lower:
            return """Recent commits include:
- abc123: Fix bug in login_user - Added OAuth2 support
- Multiple changes to auth_service.py and related files

The commit history shows active development in the authentication module."""
        
        else:
            return f"""Thank you for your query. Based on the context provided, I can help you with:

Your question: {prompt[:100]}...

[This is a mock response. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable to use real LLM.]

Key points from memory:
- Recent activity in authentication modules
- Changes to login_user function
- OAuth2 integration updates

How can I assist you further?"""


def get_llm_client(provider: str = "openai", **kwargs) -> LLMClient:
    """
    Factory function to get LLM client.
    
    Args:
        provider: 'openai', 'anthropic', or 'mock'
        **kwargs: Additional arguments for the client
        
    Returns:
        LLM client instance
    """
    if provider == "openai":
        return OpenAIClient(**kwargs)
    elif provider == "anthropic":
        return AnthropicClient(**kwargs)
    elif provider == "mock":
        return MockLLMClient()
    else:
        logger.warning(f"Unknown provider: {provider}, using mock")
        return MockLLMClient()


# Example usage
if __name__ == '__main__':
    print("=" * 60)
    print("LLM Client Demo")
    print("=" * 60)
    
    # Try OpenAI
    print("\n1. OpenAI Client")
    openai_client = OpenAIClient()
    if openai_client.enabled:
        response = openai_client.generate("What is Python?", max_tokens=50)
        print(f"Response: {response}")
    else:
        print("OpenAI not available (no API key)")
    
    # Try Anthropic
    print("\n2. Anthropic Client")
    anthropic_client = AnthropicClient()
    if anthropic_client.enabled:
        response = anthropic_client.generate("What is Python?", max_tokens=50)
        print(f"Response: {response}")
    else:
        print("Anthropic not available (no API key)")
    
    # Mock client
    print("\n3. Mock Client")
    mock_client = MockLLMClient()
    response = mock_client.generate("Tell me about login authentication")
    print(f"Response: {response}")
    
    print("\n✅ Demo complete!")
