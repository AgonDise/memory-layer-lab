#!/usr/bin/env python3
"""
Interactive Configuration Manager UI.

Provides a Gradio interface to easily adjust system parameters.
"""

import gradio as gr
import yaml
from utils.config_manager import ConfigManager
from pathlib import Path


class ConfigUI:
    """Configuration UI manager."""
    
    def __init__(self):
        self.config = ConfigManager()
    
    def get_compression_settings(self):
        """Get current compression settings."""
        comp = self.config.get_section('compression')
        return (
            comp.get('enabled', True),
            comp.get('strategy', 'score_based'),
            comp.get('max_tokens', 1000),
            comp.get('preserve_recent', 3),
            comp.get('importance_weight', 0.4),
            comp.get('recency_weight', 0.3),
            comp.get('relevance_weight', 0.3)
        )
    
    def update_compression_settings(self, enabled, strategy, max_tokens, preserve_recent,
                                   imp_weight, rec_weight, rel_weight):
        """Update compression settings."""
        self.config.update({
            'compression.enabled': enabled,
            'compression.strategy': strategy,
            'compression.max_tokens': int(max_tokens),
            'compression.preserve_recent': int(preserve_recent),
            'compression.importance_weight': float(imp_weight),
            'compression.recency_weight': float(rec_weight),
            'compression.relevance_weight': float(rel_weight)
        }, save=True)
        return "✅ Compression settings updated!"
    
    def get_memory_settings(self):
        """Get current memory settings."""
        stm = self.config.get_section('short_term_memory')
        mtm = self.config.get_section('mid_term_memory')
        return (
            stm.get('max_items', 10),
            stm.get('retention_time', 300),
            mtm.get('max_chunks', 100),
            mtm.get('chunk_size', 5),
            mtm.get('importance_threshold', 0.5)
        )
    
    def update_memory_settings(self, stm_max, stm_retention, mtm_max, mtm_chunk_size, mtm_threshold):
        """Update memory settings."""
        self.config.update({
            'short_term_memory.max_items': int(stm_max),
            'short_term_memory.retention_time': int(stm_retention),
            'mid_term_memory.max_chunks': int(mtm_max),
            'mid_term_memory.chunk_size': int(mtm_chunk_size),
            'mid_term_memory.importance_threshold': float(mtm_threshold)
        }, save=True)
        return "✅ Memory settings updated!"
    
    def get_semantic_search_settings(self):
        """Get semantic search settings."""
        ss = self.config.get_section('semantic_search')
        return (
            ss.get('enabled', True),
            ss.get('use_real_embeddings', True),
            ss.get('similarity_threshold', 0.6),
            ss.get('top_k_stm', 5),
            ss.get('top_k_mtm', 3)
        )
    
    def update_semantic_search_settings(self, enabled, use_real, threshold, top_k_stm, top_k_mtm):
        """Update semantic search settings."""
        self.config.update({
            'semantic_search.enabled': enabled,
            'semantic_search.use_real_embeddings': use_real,
            'semantic_search.similarity_threshold': float(threshold),
            'semantic_search.top_k_stm': int(top_k_stm),
            'semantic_search.top_k_mtm': int(top_k_mtm)
        }, save=True)
        return "✅ Semantic search settings updated!"
    
    def get_response_gen_settings(self):
        """Get response generation settings."""
        rg = self.config.get_section('response_generation')
        return (
            rg.get('model', 'gpt-4o-mini'),
            rg.get('temperature', 0.7),
            rg.get('max_tokens', 500)
        )
    
    def update_response_gen_settings(self, model, temperature, max_tokens):
        """Update response generation settings."""
        self.config.update({
            'response_generation.model': model,
            'response_generation.temperature': float(temperature),
            'response_generation.max_tokens': int(max_tokens)
        }, save=True)
        return "✅ Response generation settings updated!"
    
    def get_langfuse_settings(self):
        """Get Langfuse settings."""
        lf = self.config.get_section('langfuse')
        return (
            lf.get('enabled', False),
            lf.get('sample_rate', 1.0),
            lf.get('environment', 'development'),
            lf.get('trace_llm_calls', True),
            lf.get('trace_embeddings', True),
            lf.get('trace_retrievals', True)
        )
    
    def update_langfuse_settings(self, enabled, sample_rate, environment,
                                trace_llm, trace_embed, trace_retrieve):
        """Update Langfuse settings."""
        self.config.update({
            'langfuse.enabled': enabled,
            'langfuse.sample_rate': float(sample_rate),
            'langfuse.environment': environment,
            'langfuse.trace_llm_calls': trace_llm,
            'langfuse.trace_embeddings': trace_embed,
            'langfuse.trace_retrievals': trace_retrieve
        }, save=True)
        return "✅ Langfuse settings updated!"
    
    def export_config(self):
        """Export current config."""
        export_path = "config/exported_config.yaml"
        self.config.export_template(export_path)
        return f"✅ Config exported to {export_path}"
    
    def reset_to_defaults(self, section):
        """Reset a section to defaults."""
        self.config.reset_section(section)
        self.config.save()
        return f"✅ Reset {section} to defaults"
    
    def view_current_config(self):
        """View current configuration."""
        return yaml.dump(self.config.get_all(), default_flow_style=False, indent=2)
    
    def validate_config(self):
        """Validate configuration."""
        errors = self.config.validate()
        if errors:
            return "❌ Validation errors:\n" + "\n".join(f"  • {e}" for e in errors)
        return "✅ Configuration is valid!"


def create_ui():
    """Create Gradio interface."""
    config_ui = ConfigUI()
    
    with gr.Blocks(title="Memory Layer Lab - Configuration", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🎛️ Memory Layer Lab - Configuration Manager")
        gr.Markdown("Adjust system parameters in real-time")
        
        with gr.Tabs():
            # Compression Settings
            with gr.Tab("🗜️ Compression"):
                gr.Markdown("### Compression Settings")
                
                with gr.Row():
                    comp_enabled = gr.Checkbox(label="Enable Compression", value=True)
                    comp_strategy = gr.Dropdown(
                        choices=["score_based", "mmr", "truncate"],
                        label="Strategy",
                        value="score_based"
                    )
                
                with gr.Row():
                    comp_max_tokens = gr.Slider(100, 5000, step=100, label="Max Tokens", value=1000)
                    comp_preserve = gr.Slider(0, 10, step=1, label="Preserve Recent N", value=3)
                
                gr.Markdown("### Weight Distribution (should sum to 1.0)")
                with gr.Row():
                    comp_imp_weight = gr.Slider(0, 1, step=0.1, label="Importance Weight", value=0.4)
                    comp_rec_weight = gr.Slider(0, 1, step=0.1, label="Recency Weight", value=0.3)
                    comp_rel_weight = gr.Slider(0, 1, step=0.1, label="Relevance Weight", value=0.3)
                
                comp_update_btn = gr.Button("Update Compression Settings", variant="primary")
                comp_status = gr.Textbox(label="Status", interactive=False)
                
                comp_update_btn.click(
                    config_ui.update_compression_settings,
                    inputs=[comp_enabled, comp_strategy, comp_max_tokens, comp_preserve,
                           comp_imp_weight, comp_rec_weight, comp_rel_weight],
                    outputs=comp_status
                )
            
            # Memory Settings
            with gr.Tab("🧠 Memory Layers"):
                gr.Markdown("### Short-Term Memory")
                with gr.Row():
                    stm_max = gr.Slider(5, 50, step=1, label="Max Items", value=10)
                    stm_retention = gr.Slider(60, 3600, step=60, label="Retention Time (s)", value=300)
                
                gr.Markdown("### Mid-Term Memory")
                with gr.Row():
                    mtm_max = gr.Slider(10, 500, step=10, label="Max Chunks", value=100)
                    mtm_chunk_size = gr.Slider(3, 20, step=1, label="Chunk Size", value=5)
                    mtm_threshold = gr.Slider(0, 1, step=0.1, label="Importance Threshold", value=0.5)
                
                mem_update_btn = gr.Button("Update Memory Settings", variant="primary")
                mem_status = gr.Textbox(label="Status", interactive=False)
                
                mem_update_btn.click(
                    config_ui.update_memory_settings,
                    inputs=[stm_max, stm_retention, mtm_max, mtm_chunk_size, mtm_threshold],
                    outputs=mem_status
                )
            
            # Semantic Search Settings
            with gr.Tab("🔍 Semantic Search"):
                gr.Markdown("### Semantic Search Settings")
                
                with gr.Row():
                    ss_enabled = gr.Checkbox(label="Enable Semantic Search", value=True)
                    ss_real_embed = gr.Checkbox(label="Use Real Embeddings", value=True)
                
                with gr.Row():
                    ss_threshold = gr.Slider(0, 1, step=0.05, label="Similarity Threshold", value=0.6)
                
                gr.Markdown("### Top-K Settings")
                with gr.Row():
                    ss_top_k_stm = gr.Slider(1, 20, step=1, label="Top K (STM)", value=5)
                    ss_top_k_mtm = gr.Slider(1, 20, step=1, label="Top K (MTM)", value=3)
                
                ss_update_btn = gr.Button("Update Semantic Search Settings", variant="primary")
                ss_status = gr.Textbox(label="Status", interactive=False)
                
                ss_update_btn.click(
                    config_ui.update_semantic_search_settings,
                    inputs=[ss_enabled, ss_real_embed, ss_threshold, ss_top_k_stm, ss_top_k_mtm],
                    outputs=ss_status
                )
            
            # Response Generation
            with gr.Tab("💬 Response Generation"):
                gr.Markdown("### LLM Settings")
                
                rg_model = gr.Dropdown(
                    choices=["gpt-4", "gpt-4o-mini", "gpt-3.5-turbo", "claude-3-sonnet"],
                    label="Model",
                    value="gpt-4o-mini"
                )
                
                with gr.Row():
                    rg_temperature = gr.Slider(0, 2, step=0.1, label="Temperature", value=0.7)
                    rg_max_tokens = gr.Slider(50, 2000, step=50, label="Max Tokens", value=500)
                
                rg_update_btn = gr.Button("Update Response Settings", variant="primary")
                rg_status = gr.Textbox(label="Status", interactive=False)
                
                rg_update_btn.click(
                    config_ui.update_response_gen_settings,
                    inputs=[rg_model, rg_temperature, rg_max_tokens],
                    outputs=rg_status
                )
            
            # Langfuse Settings
            with gr.Tab("📊 Langfuse Tracing"):
                gr.Markdown("### Langfuse Settings")
                
                with gr.Row():
                    lf_enabled = gr.Checkbox(label="Enable Langfuse", value=False)
                    lf_sample = gr.Slider(0, 1, step=0.1, label="Sample Rate", value=1.0)
                    lf_env = gr.Dropdown(
                        choices=["development", "staging", "production"],
                        label="Environment",
                        value="development"
                    )
                
                gr.Markdown("### What to Trace")
                with gr.Row():
                    lf_llm = gr.Checkbox(label="LLM Calls", value=True)
                    lf_embed = gr.Checkbox(label="Embeddings", value=True)
                    lf_retrieve = gr.Checkbox(label="Retrievals", value=True)
                
                lf_update_btn = gr.Button("Update Langfuse Settings", variant="primary")
                lf_status = gr.Textbox(label="Status", interactive=False)
                
                lf_update_btn.click(
                    config_ui.update_langfuse_settings,
                    inputs=[lf_enabled, lf_sample, lf_env, lf_llm, lf_embed, lf_retrieve],
                    outputs=lf_status
                )
            
            # View & Export
            with gr.Tab("📋 View & Export"):
                gr.Markdown("### Current Configuration")
                
                view_btn = gr.Button("View Current Config")
                config_text = gr.Textbox(label="Configuration (YAML)", lines=20, interactive=False)
                
                view_btn.click(config_ui.view_current_config, outputs=config_text)
                
                gr.Markdown("### Actions")
                with gr.Row():
                    export_btn = gr.Button("Export Config")
                    validate_btn = gr.Button("Validate Config")
                
                action_status = gr.Textbox(label="Status", interactive=False)
                
                export_btn.click(config_ui.export_config, outputs=action_status)
                validate_btn.click(config_ui.validate_config, outputs=action_status)
                
                gr.Markdown("### Reset Sections")
                reset_section = gr.Dropdown(
                    choices=["compression", "short_term_memory", "mid_term_memory", 
                            "semantic_search", "response_generation", "langfuse"],
                    label="Section to Reset"
                )
                reset_btn = gr.Button("Reset to Defaults", variant="stop")
                reset_status = gr.Textbox(label="Status", interactive=False)
                
                reset_btn.click(
                    config_ui.reset_to_defaults,
                    inputs=reset_section,
                    outputs=reset_status
                )
        
        gr.Markdown("---")
        gr.Markdown("💡 **Tip:** All changes are saved automatically. Restart your application to apply new settings.")
    
    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False
    )
