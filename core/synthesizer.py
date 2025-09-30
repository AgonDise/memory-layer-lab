from typing import Dict, Any, Optional, List
import json
import re
from datetime import datetime

class ResponseSynthesizer:
    """
    Synthesizes and formats final responses for users.
    
    Handles:
    - Response formatting (markdown, JSON, code)
    - Post-processing
    - Error handling
    - Metadata injection
    """
    
    def __init__(self, output_format: str = 'markdown'):
        """
        Initialize response synthesizer.
        
        Args:
            output_format: Output format ('markdown', 'json', 'plain')
        """
        self.output_format = output_format
    
    def synthesize(self,
                   raw_response: str,
                   context_metadata: Optional[Dict[str, Any]] = None,
                   query_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Synthesize final response from raw LLM output.
        
        Args:
            raw_response: Raw response from LLM/reasoner
            context_metadata: Metadata from context (compression info, sources, etc.)
            query_info: Information about the original query
            
        Returns:
            Synthesized response dictionary
        """
        # Post-process response
        processed_response = self._post_process(raw_response)
        
        # Format according to output format
        formatted_response = self._format_response(processed_response)
        
        # Add metadata
        response_dict = {
            'response': formatted_response,
            'raw_response': raw_response,
            'format': self.output_format,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        # Add context metadata if provided
        if context_metadata:
            response_dict['context_info'] = {
                'total_tokens': context_metadata.get('total_tokens', 0),
                'compression_ratio': context_metadata.get('compression_ratio', 0.0),
                'items_used': context_metadata.get('items_kept', 0),
            }
        
        # Add query info if provided
        if query_info:
            response_dict['query_info'] = {
                'intent': query_info.get('intent', 'general'),
                'keywords': query_info.get('keywords', []),
            }
        
        return response_dict
    
    def _post_process(self, response: str) -> str:
        """
        Post-process response text.
        
        Args:
            response: Raw response text
            
        Returns:
            Processed response
        """
        # Remove excessive whitespace
        response = re.sub(r'\n{3,}', '\n\n', response)
        response = re.sub(r' {2,}', ' ', response)
        
        # Trim
        response = response.strip()
        
        return response
    
    def _format_response(self, response: str) -> str:
        """
        Format response according to output format.
        
        Args:
            response: Processed response
            
        Returns:
            Formatted response
        """
        if self.output_format == 'markdown':
            return self._format_markdown(response)
        elif self.output_format == 'json':
            return self._format_json(response)
        else:
            return response
    
    def _format_markdown(self, response: str) -> str:
        """Format response as markdown."""
        # Already in markdown format, just enhance
        lines = response.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Auto-detect code blocks
            if line.strip().startswith('```'):
                formatted_lines.append(line)
            # Auto-detect lists
            elif line.strip().startswith(('- ', '* ', '1. ')):
                formatted_lines.append(line)
            # Regular text
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _format_json(self, response: str) -> str:
        """Format response as JSON."""
        try:
            # Try to parse as JSON
            parsed = json.loads(response)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            # Wrap in JSON structure
            return json.dumps({
                'response': response,
                'type': 'text'
            }, indent=2, ensure_ascii=False)
    
    def add_citations(self, 
                      response_dict: Dict[str, Any],
                      sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add source citations to response.
        
        Args:
            response_dict: Response dictionary
            sources: List of source items from memory layers
            
        Returns:
            Response with citations
        """
        if not sources:
            return response_dict
        
        citations = []
        for i, source in enumerate(sources, 1):
            citation = {
                'id': i,
                'source': source.get('source', 'unknown'),
                'content_preview': source.get('content', '')[:100],
                'score': source.get('final_score', 0.0),
            }
            citations.append(citation)
        
        response_dict['citations'] = citations
        
        # Add citation markers to response text if markdown
        if self.output_format == 'markdown' and citations:
            response_dict['response'] += '\n\n---\n**Sources:**\n'
            for cite in citations:
                response_dict['response'] += f"\n[{cite['id']}] {cite['source']}: {cite['content_preview']}..."
        
        return response_dict
    
    def add_error_handling(self, 
                          response_dict: Dict[str, Any],
                          error: Optional[Exception] = None) -> Dict[str, Any]:
        """
        Add error information to response.
        
        Args:
            response_dict: Response dictionary
            error: Exception if any
            
        Returns:
            Response with error info
        """
        if error:
            response_dict['error'] = {
                'type': type(error).__name__,
                'message': str(error),
            }
            
            # Format user-friendly error message
            if self.output_format == 'markdown':
                response_dict['response'] = f"⚠️ **Error:** {str(error)}\n\n{response_dict.get('response', '')}"
        
        return response_dict
    
    def format_for_display(self, response_dict: Dict[str, Any]) -> str:
        """
        Format response dictionary for display to user.
        
        Args:
            response_dict: Complete response dictionary
            
        Returns:
            Display-ready string
        """
        return response_dict.get('response', '')
    
    def to_json(self, response_dict: Dict[str, Any]) -> str:
        """
        Convert response to JSON string.
        
        Args:
            response_dict: Response dictionary
            
        Returns:
            JSON string
        """
        return json.dumps(response_dict, indent=2, ensure_ascii=False)
