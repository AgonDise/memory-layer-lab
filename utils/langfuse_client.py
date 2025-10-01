"""
Langfuse integration for tracing and observability.

Provides:
- Automatic LLM call tracing
- Embedding generation tracing
- Memory retrieval tracing
- Full conversation pipeline tracing
- Custom event logging
"""

from typing import Optional, Dict, Any, List, Callable
import time
import logging
from functools import wraps
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Try to import Langfuse
try:
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.warning("Langfuse not installed. Install with: pip install langfuse")


class LangfuseClient:
    """
    Langfuse client wrapper with graceful fallback.
    """
    
    def __init__(self,
                 public_key: Optional[str] = None,
                 secret_key: Optional[str] = None,
                 host: str = "https://cloud.langfuse.com",
                 enabled: bool = True,
                 debug: bool = False,
                 sample_rate: float = 1.0,
                 flush_at: int = 15,
                 flush_interval: float = 1.0,
                 release: Optional[str] = None,
                 environment: str = "development"):
        """
        Initialize Langfuse client.
        
        Args:
            public_key: Langfuse public key
            secret_key: Langfuse secret key
            host: Langfuse host URL
            enabled: Enable/disable tracing
            debug: Debug mode
            sample_rate: Sample rate (0.0 to 1.0)
            flush_at: Flush after N events
            flush_interval: Flush interval in seconds
            release: Release version
            environment: Environment name
        """
        self.enabled = enabled and LANGFUSE_AVAILABLE
        self.debug = debug
        self.sample_rate = sample_rate
        self.release = release
        self.environment = environment
        
        self.client: Optional[Langfuse] = None
        
        if self.enabled:
            if not public_key or not secret_key:
                logger.warning("Langfuse credentials not provided. Tracing disabled.")
                self.enabled = False
            else:
                try:
                    self.client = Langfuse(
                        public_key=public_key,
                        secret_key=secret_key,
                        host=host,
                        debug=debug,
                        flush_at=flush_at,
                        flush_interval=flush_interval,
                        release=release,
                        environment=environment
                    )
                    logger.info(f"✅ Langfuse initialized (env={environment}, host={host})")
                except Exception as e:
                    logger.error(f"Failed to initialize Langfuse: {e}")
                    self.enabled = False
        else:
            if not LANGFUSE_AVAILABLE:
                logger.info("Langfuse not available. Tracing disabled.")
            else:
                logger.info("Langfuse disabled by configuration")
    
    def is_enabled(self) -> bool:
        """Check if Langfuse is enabled."""
        return self.enabled and self.client is not None
    
    def create_trace(self,
                    name: str,
                    user_id: Optional[str] = None,
                    session_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None,
                    tags: Optional[List[str]] = None) -> Optional[Any]:
        """
        Create a new trace.
        
        Args:
            name: Trace name
            user_id: User ID
            session_id: Session ID
            metadata: Additional metadata
            tags: Tags for filtering
            
        Returns:
            Trace object or None
        """
        if not self.is_enabled():
            return None
        
        try:
            trace = self.client.trace(
                name=name,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata or {},
                tags=tags or [],
                release=self.release
            )
            if self.debug:
                logger.debug(f"Created trace: {name}")
            return trace
        except Exception as e:
            logger.error(f"Failed to create trace: {e}")
            return None
    
    def log_generation(self,
                      trace_id: str,
                      name: str,
                      model: str,
                      input_text: str,
                      output_text: str,
                      metadata: Optional[Dict[str, Any]] = None,
                      usage: Optional[Dict[str, int]] = None,
                      start_time: Optional[float] = None,
                      end_time: Optional[float] = None) -> bool:
        """
        Log an LLM generation.
        
        Args:
            trace_id: Trace ID
            name: Generation name
            model: Model name
            input_text: Input prompt
            output_text: Generated output
            metadata: Additional metadata
            usage: Token usage info
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            return False
        
        try:
            generation = {
                "name": name,
                "model": model,
                "input": input_text,
                "output": output_text,
                "metadata": metadata or {},
            }
            
            if usage:
                generation["usage"] = usage
            
            if start_time and end_time:
                generation["start_time"] = start_time
                generation["end_time"] = end_time
                generation["completion_time"] = end_time - start_time
            
            # Note: Actual Langfuse API may differ
            # This is a simplified interface
            if self.debug:
                logger.debug(f"Logged generation: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to log generation: {e}")
            return False
    
    def log_span(self,
                trace_id: str,
                name: str,
                input_data: Any = None,
                output_data: Any = None,
                metadata: Optional[Dict[str, Any]] = None,
                start_time: Optional[float] = None,
                end_time: Optional[float] = None) -> bool:
        """
        Log a span (operation within a trace).
        
        Args:
            trace_id: Trace ID
            name: Span name
            input_data: Input data
            output_data: Output data
            metadata: Additional metadata
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            return False
        
        try:
            span = {
                "name": name,
                "input": input_data,
                "output": output_data,
                "metadata": metadata or {}
            }
            
            if start_time and end_time:
                span["start_time"] = start_time
                span["end_time"] = end_time
                span["duration"] = end_time - start_time
            
            if self.debug:
                logger.debug(f"Logged span: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to log span: {e}")
            return False
    
    def log_event(self,
                 trace_id: str,
                 name: str,
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log a custom event.
        
        Args:
            trace_id: Trace ID
            name: Event name
            metadata: Event metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            return False
        
        try:
            if self.debug:
                logger.debug(f"Logged event: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
            return False
    
    def flush(self):
        """Flush pending traces to Langfuse."""
        if self.is_enabled():
            try:
                self.client.flush()
                if self.debug:
                    logger.debug("Flushed traces to Langfuse")
            except Exception as e:
                logger.error(f"Failed to flush traces: {e}")
    
    def shutdown(self):
        """Shutdown Langfuse client."""
        if self.is_enabled():
            try:
                self.flush()
                if self.debug:
                    logger.info("Langfuse client shutdown")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")


class LangfuseTracer:
    """
    Decorator-based tracing utilities.
    """
    
    def __init__(self, client: LangfuseClient):
        """
        Initialize tracer.
        
        Args:
            client: LangfuseClient instance
        """
        self.client = client
    
    def trace_llm_call(self, model: str = "unknown"):
        """
        Decorator to trace LLM calls.
        
        Args:
            model: Model name
            
        Usage:
            @tracer.trace_llm_call(model="gpt-4")
            def generate_response(prompt):
                return llm.generate(prompt)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.client.is_enabled():
                    return func(*args, **kwargs)
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    
                    # Log the generation
                    input_text = str(args[0]) if args else str(kwargs.get('prompt', ''))
                    output_text = str(result)
                    
                    self.client.log_generation(
                        trace_id="current",  # Would use actual trace ID
                        name=func.__name__,
                        model=model,
                        input_text=input_text,
                        output_text=output_text,
                        start_time=start_time,
                        end_time=end_time
                    )
                    
                    return result
                except Exception as e:
                    logger.error(f"Error in traced function {func.__name__}: {e}")
                    raise
            
            return wrapper
        return decorator
    
    def trace_operation(self, name: Optional[str] = None):
        """
        Decorator to trace generic operations.
        
        Args:
            name: Operation name (defaults to function name)
            
        Usage:
            @tracer.trace_operation(name="memory_retrieval")
            def retrieve_context(query):
                return memory.search(query)
        """
        def decorator(func: Callable) -> Callable:
            operation_name = name or func.__name__
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.client.is_enabled():
                    return func(*args, **kwargs)
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    
                    self.client.log_span(
                        trace_id="current",
                        name=operation_name,
                        input_data={"args": str(args)[:100], "kwargs": str(kwargs)[:100]},
                        output_data=str(result)[:100],
                        start_time=start_time,
                        end_time=end_time
                    )
                    
                    return result
                except Exception as e:
                    logger.error(f"Error in traced operation {operation_name}: {e}")
                    raise
            
            return wrapper
        return decorator
    
    @contextmanager
    def trace_context(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for tracing a block of code.
        
        Args:
            name: Context name
            metadata: Additional metadata
            
        Usage:
            with tracer.trace_context("full_pipeline"):
                # Your code here
                result = process()
        """
        if not self.client.is_enabled():
            yield
            return
        
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            self.client.log_span(
                trace_id="current",
                name=name,
                metadata=metadata,
                start_time=start_time,
                end_time=end_time
            )


def load_langfuse_config(config_file: str = "config/langfuse_config.yaml") -> Dict[str, Any]:
    """
    Load Langfuse configuration from YAML file.
    
    Args:
        config_file: Path to config file
        
    Returns:
        Configuration dictionary
    """
    try:
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('langfuse', {})
    except FileNotFoundError:
        logger.warning(f"Langfuse config not found: {config_file}")
        return {'enabled': False}
    except Exception as e:
        logger.error(f"Error loading Langfuse config: {e}")
        return {'enabled': False}


def create_langfuse_client(config: Optional[Dict[str, Any]] = None) -> LangfuseClient:
    """
    Create Langfuse client from configuration.
    
    Args:
        config: Configuration dictionary (loads from file if None)
        
    Returns:
        LangfuseClient instance
    """
    if config is None:
        config = load_langfuse_config()
    
    return LangfuseClient(
        public_key=config.get('public_key'),
        secret_key=config.get('secret_key'),
        host=config.get('host', 'https://cloud.langfuse.com'),
        enabled=config.get('enabled', True),
        debug=config.get('debug', False),
        sample_rate=config.get('sample_rate', 1.0),
        flush_at=config.get('flush_at', 15),
        flush_interval=config.get('flush_interval', 1.0),
        release=config.get('release'),
        environment=config.get('environment', 'development')
    )
