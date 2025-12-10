
import logging
import traceback
from functools import wraps
from typing import Any, Callable, Optional
from pathlib import Path
import config


# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger("research_agent")
logger.setLevel(getattr(logging, config.LOG_LEVEL))

# File handler
file_handler = logging.FileHandler(log_dir / "research_agent.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(file_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
console_formatter = logging.Formatter(
    '%(levelname)s - %(message)s'
)
console_handler.setFormatter(console_formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


# Custom Exceptions
class ResearchAgentError(Exception):
    """Base exception for research agent"""
    pass


class APIError(ResearchAgentError):
    """API request failed"""
    pass


class PDFProcessingError(ResearchAgentError):
    """PDF processing failed"""
    pass


class LLMError(ResearchAgentError):
    """LLM operation failed"""
    pass


class ValidationError(ResearchAgentError):
    """Data validation failed"""
    pass


class ErrorContext:
    """Context manager for error handling with logging"""
    
    # def __init__(self, operation: str):
    #     self.operation = operation
        
    def __init__(self, operation: str, context_id: Optional[str] = None):
        self.operation = operation
        self.context_id = context_id
    
    def __enter__(self):
        logger.debug(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"Failed: {self.operation} - {exc_type.__name__}: {exc_val}")
            # Don't suppress the exception
            return False
        logger.debug(f"Completed: {self.operation}")
        return False


def handle_errors(func: Callable) -> Callable:
    """
    Decorator for consistent error handling and logging
    
    Usage:
        @handle_errors
        def my_function():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except APIError as e:
            logger.error(f"API Error in {func.__name__}: {str(e)}")
            raise
        except PDFProcessingError as e:
            logger.error(f"PDF Processing Error in {func.__name__}: {str(e)}")
            raise
        except LLMError as e:
            logger.error(f"LLM Error in {func.__name__}: {str(e)}")
            raise
        except ValidationError as e:
            logger.error(f"Validation Error in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            logger.debug(traceback.format_exc())
            raise ResearchAgentError(f"Operation failed: {str(e)}") from e
    
    return wrapper


def log_function_call(func: Callable) -> Callable:
    """
    Decorator to log function calls with arguments
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"{func_name} completed successfully")
        return result
    
    return wrapper