#!/usr/bin/env python3
"""
Web UI for Memory Layer Lab Chatbot using Gradio.

Features:
- Clean chat interface
- Memory layer visualization
- Pipeline logging view
- Metrics dashboard
"""

import gradio as gr
import os
from datetime import datetime
from typing import List, Tuple, Dict, Any
import json

from config import get_config
from utils import FakeEmbeddingGenerator, get_llm_client
from core import (
    ShortTermMemory, MidTermMemory, LongTermMemory,
    InputPreprocessor, MemoryOrchestrator, Summarizer,
    ResponseSynthesizer
)
from bot import ResponseGenerator


class ChatbotUI:
    """Chatbot with UI and monitoring."""
    
    def __init__(self):
        """Initialize chatbot."""
        self.config = get_config()
        self.setup_components()
        self.conversation_logs = []
        self.metrics = {
            'total_queries': 0,
            'avg_response_time': 0,
            'memory_hits': {'stm': 0, 'mtm': 0, 'ltm': 0},
            'context_compression_ratio': []
        }
    
    def setup_components(self):
        """Setup all chatbot components."""
        # Memory layers
        self.stm = ShortTermMemory(max_size=20)
        self.mtm = MidTermMemory(max_size=100)
        self.ltm = LongTermMemory(enabled=False)
        self.summarizer = Summarizer()
        
        # Core components
        self.preprocessor = InputPreprocessor(embedding_dim=384)
        self.orchestrator = MemoryOrchestrator(
            self.stm, self.mtm, self.ltm, self.summarizer
        )
        self.synthesizer = ResponseSynthesizer(output_format='markdown')
        
        # LLM setup
        llm_config = self.config['llm']
        provider = llm_config['provider']
        
        api_key = None
        if provider == 'openai':
            api_key = llm_config['openai']['api_key'] or os.getenv('OPENAI_API_KEY')
        elif provider == 'anthropic':
            api_key = llm_config['anthropic']['api_key'] or os.getenv('ANTHROPIC_API_KEY')
        
        if api_key:
            self.llm_client = get_llm_client(provider, api_key=api_key)
        else:
            self.llm_client = get_llm_client('mock')
        
        self.response_generator = ResponseGenerator(
            mode='llm',
            llm_config=llm_config,
            llm_client=self.llm_client
        )
    
    def chat(self, message: str, history: List[Tuple[str, str]]) -> Tuple[str, str, str, Dict]:
        """
        Process chat message.
        
        Returns:
            (response, pipeline_log, memory_status, metrics)
        """
        start_time = datetime.now()
        log_entries = []
        
        try:
            # 1. Preprocess
            log_entries.append("🔍 Preprocessing query...")
            preprocessed = self.preprocessor.preprocess(message)
            log_entries.append(f"  ✓ Intent: {preprocessed['intent']}")
            log_entries.append(f"  ✓ Keywords: {', '.join(preprocessed['keywords'][:5])}")
            
            # 2. Retrieve context
            log_entries.append("\n💾 Retrieving from memory...")
            memory_context = self.orchestrator.get_context(
                query=message,
                n_recent=5,
                n_chunks=3
            )
            
            aggregated = memory_context['aggregated']
            compressed = memory_context['compressed']
            
            stm_count = aggregated.get('stm_count', 0)
            mtm_count = aggregated.get('mtm_count', 0)
            
            log_entries.append(f"  ✓ STM: {stm_count} items")
            log_entries.append(f"  ✓ MTM: {mtm_count} chunks")
            
            # Update metrics
            self.metrics['memory_hits']['stm'] += stm_count
            self.metrics['memory_hits']['mtm'] += mtm_count
            
            # 3. Build context
            log_entries.append("\n📝 Building context...")
            context_items = compressed.get('items', [])
            context_text = "\n".join([
                f"- {item.get('content', item.get('summary', 'N/A'))}"
                for item in context_items[:5]
            ])
            
            # Calculate compression ratio
            total_items = stm_count + mtm_count
            compressed_items = len(context_items)
            if total_items > 0:
                ratio = compressed_items / total_items
                self.metrics['context_compression_ratio'].append(ratio)
                log_entries.append(f"  ✓ Compression: {total_items} → {compressed_items} ({ratio:.2%})")
            
            # 4. Generate response
            log_entries.append(f"\n🤖 Generating with {self.llm_client.__class__.__name__}...")
            raw_response = self.response_generator.generate(
                user_message=message,
                context=context_text
            )
            log_entries.append(f"  ✓ Response generated ({len(raw_response)} chars)")
            
            # 5. Synthesize
            final_response = self.synthesizer.synthesize(
                raw_response=raw_response,
                context_metadata={
                    'stm_count': stm_count,
                    'mtm_count': mtm_count,
                    'compressed_items': compressed_items
                }
            )
            
            response_text = final_response['response']
            
            # 6. Save to memory
            log_entries.append("\n💿 Saving to memory...")
            self.orchestrator.add_message(
                role='user',
                content=message,
                embedding=preprocessed['embedding']
            )
            self.orchestrator.add_message(
                role='assistant',
                content=response_text,
                embedding=self.preprocessor.preprocess(response_text)['embedding']
            )
            log_entries.append("  ✓ Saved to memory")
            
            # Calculate response time
            elapsed = (datetime.now() - start_time).total_seconds()
            log_entries.append(f"\n⏱️  Response time: {elapsed:.2f}s")
            
            # Update metrics
            self.metrics['total_queries'] += 1
            self.metrics['avg_response_time'] = (
                (self.metrics['avg_response_time'] * (self.metrics['total_queries'] - 1) + elapsed) 
                / self.metrics['total_queries']
            )
            
            # Save conversation log
            self.conversation_logs.append({
                'timestamp': datetime.now().isoformat(),
                'query': message,
                'response': response_text,
                'intent': preprocessed['intent'],
                'memory_hits': {'stm': stm_count, 'mtm': mtm_count},
                'response_time': elapsed
            })
            
            # Format outputs
            pipeline_log = "\n".join(log_entries)
            memory_status = self.get_memory_status()
            metrics = self.get_metrics_display()
            
            return response_text, pipeline_log, memory_status, metrics
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            log_entries.append(f"\n{error_msg}")
            return error_msg, "\n".join(log_entries), "", {}
    
    def get_memory_status(self) -> str:
        """Get current memory status."""
        return f"""📊 Memory Status:
        
**Short-term Memory:**
- Messages: {len(self.stm.messages)}/{self.stm.max_size}
- Usage: {len(self.stm.messages)/self.stm.max_size*100:.1f}%

**Mid-term Memory:**
- Chunks: {len(self.mtm.chunks)}/{self.mtm.max_size}
- Usage: {len(self.mtm.chunks)/self.mtm.max_size*100:.1f}%

**Long-term Memory:**
- Status: {'Enabled' if self.ltm.enabled else 'Disabled'}
"""
    
    def get_metrics_display(self) -> Dict[str, Any]:
        """Get metrics for display."""
        avg_compression = (
            sum(self.metrics['context_compression_ratio']) / len(self.metrics['context_compression_ratio'])
            if self.metrics['context_compression_ratio'] else 0
        )
        
        return {
            'Total Queries': self.metrics['total_queries'],
            'Avg Response Time': f"{self.metrics['avg_response_time']:.2f}s",
            'STM Hits': self.metrics['memory_hits']['stm'],
            'MTM Hits': self.metrics['memory_hits']['mtm'],
            'Avg Compression Ratio': f"{avg_compression:.2%}"
        }
    
    def clear_memory(self):
        """Clear all memory."""
        self.stm.clear()
        self.mtm.clear()
        return "✅ Memory cleared!"


def create_ui():
    """Create Gradio UI."""
    chatbot_ui = ChatbotUI()
    
    with gr.Blocks(title="Memory Layer Lab", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🤖 Memory Layer Lab - AI Chatbot")
        gr.Markdown("Chat với AI có memory layers (STM, MTM, LTM) và context-aware responses")
        
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="💬 Conversation",
                    height=400,
                    show_copy_button=True,
                    type='messages'
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="Your Message",
                        placeholder="Type your message here...",
                        scale=4
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("🗑️ Clear Chat")
                    clear_memory_btn = gr.Button("💾 Clear Memory")
            
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Monitoring")
                
                with gr.Accordion("Pipeline Log", open=True):
                    pipeline_log = gr.Textbox(
                        label="Pipeline Steps",
                        lines=10,
                        interactive=False
                    )
                
                with gr.Accordion("Memory Status", open=False):
                    memory_status = gr.Markdown()
                
                with gr.Accordion("Metrics", open=True):
                    metrics_display = gr.JSON(label="Performance Metrics")
        
        gr.Markdown("""
        ### 💡 Tips:
        - Hệ thống sẽ nhớ context từ conversations trước
        - Pipeline log shows từng bước xử lý
        - Metrics track performance và memory usage
        """)
        
        # Event handlers
        def respond(message, chat_history):
            if not message.strip():
                return chat_history, "", "", {}
            
            response, log, mem_status, metrics = chatbot_ui.chat(message, chat_history)
            chat_history.append((message, response))
            return chat_history, log, mem_status, metrics
        
        msg.submit(
            respond,
            [msg, chatbot],
            [chatbot, pipeline_log, memory_status, metrics_display]
        ).then(lambda: "", None, msg)
        
        send_btn.click(
            respond,
            [msg, chatbot],
            [chatbot, pipeline_log, memory_status, metrics_display]
        ).then(lambda: "", None, msg)
        
        clear_btn.click(lambda: [], None, chatbot)
        
        clear_memory_btn.click(
            chatbot_ui.clear_memory,
            None,
            gr.Textbox(visible=False)
        )
    
    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
