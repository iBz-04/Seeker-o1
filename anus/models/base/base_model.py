"""
Base Model module that defines the common interface for all language models.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable

class BaseModel(ABC):
    """
    Abstract base class for language model implementations.
    
    Provides a common interface for interacting with different LLM providers.
    """
    
    def __init__(
        self, 
        model_name: str, 
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize a BaseModel instance.
        
        Args:
            model_name: The name of the model to use.
            temperature: Controls randomness in outputs. Lower values are more deterministic.
            max_tokens: Maximum number of tokens to generate.
            **kwargs: Additional model-specific parameters.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.config = kwargs
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text based on a prompt.
        
        Args:
            prompt: The text prompt for generation.
            system_message: Optional system message for models that support it.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            The generated text response.
        """
        pass
    
    @abstractmethod
    def generate_with_tools(
        self, 
        prompt: str, 
        tools: List[Dict[str, Any]],
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text with tool calling capabilities.
        
        Args:
            prompt: The text prompt for generation.
            tools: List of tool schemas available for use.
            system_message: Optional system message for models that support it.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A dictionary with the response and any tool calls.
        """
        pass
    
    @abstractmethod
    def extract_json(
        self, 
        prompt: str, 
        schema: Dict[str, Any],
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract structured JSON data based on a prompt.
        
        Args:
            prompt: The text prompt for extraction.
            schema: JSON schema describing the expected structure.
            system_message: Optional system message for models that support it.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            The extracted JSON data.
        """
        pass
    
    @abstractmethod
    def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: The text to embed.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            The embedding vector as a list of floats.
        """
        pass
    
    def get_token_count(self, text: str) -> int:
        """
        Estimate the number of tokens in the given text.
        
        Args:
            text: The text to count tokens for.
            
        Returns:
            The approximate token count.
        """
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def get_model_details(self) -> Dict[str, Any]:
        """
        Get details about the model.
        
        Returns:
            A dictionary containing model information.
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "config": self.config
        } 