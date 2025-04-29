"""
OpenAI Model implementation for the ANUS framework.
"""

from typing import Dict, List, Any, Optional, Union, Callable
import json
import logging
import os

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from anus.models.base.base_model import BaseModel

class OpenAIModel(BaseModel):
    """
    OpenAI language model implementation.
    
    Provides integration with OpenAI's API for text generation and embeddings.
    """
    
    def __init__(
        self, 
        model_name: str = "gpt-4", 
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize an OpenAIModel instance.
        
        Args:
            model_name: The name of the OpenAI model to use.
            temperature: Controls randomness in outputs. Lower values are more deterministic.
            max_tokens: Maximum number of tokens to generate.
            api_key: OpenAI API key. If None, it will be read from the OPENAI_API_KEY environment variable.
            base_url: Base URL for the OpenAI API. Useful for proxies or non-standard endpoints.
            **kwargs: Additional model-specific parameters.
        """
        super().__init__(model_name, temperature, max_tokens, **kwargs)
        
        if not OPENAI_AVAILABLE:
            logging.error("OpenAI package not installed. Please install it with 'pip install openai'.")
            raise ImportError("OpenAI package not installed")
        
        # Use provided API key or read from environment
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logging.error("OpenAI API key not provided and not found in environment.")
            raise ValueError("OpenAI API key required")
        
        self.base_url = base_url
        
        # Initialize client
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        # Set default embedding model
        self.embedding_model = kwargs.get("embedding_model", "text-embedding-ada-002")
    
    def generate(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text based on a prompt using OpenAI.
        
        Args:
            prompt: The text prompt for generation.
            system_message: Optional system message for the model.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional OpenAI-specific parameters.
            
        Returns:
            The generated text response.
        """
        # Prepare messages
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        # Set parameters
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            # Make the API call
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                **kwargs
            )
            
            # Extract and return the response text
            return response.choices[0].message.content
        
        except Exception as e:
            logging.error(f"Error generating with OpenAI: {e}")
            return f"Error: {str(e)}"
    
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
            system_message: Optional system message for the model.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional OpenAI-specific parameters.
            
        Returns:
            A dictionary with the response and any tool calls.
        """
        # Prepare messages
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        # Set parameters
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        # Convert tools to OpenAI format
        openai_tools = []
        for tool in tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                }
            }
            openai_tools.append(openai_tool)
        
        try:
            # Make the API call
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                tools=openai_tools,
                **kwargs
            )
            
            # Extract response
            choice = response.choices[0]
            message = choice.message
            
            # Check for tool calls
            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_calls = []
                for tool_call in message.tool_calls:
                    # Parse arguments as JSON
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except:
                        arguments = tool_call.function.arguments
                    
                    # Create a normalized tool call
                    normalized_tool_call = {
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": arguments
                    }
                    tool_calls.append(normalized_tool_call)
                
                return {
                    "content": message.content,
                    "tool_calls": tool_calls
                }
            else:
                # No tool calls, just text
                return {
                    "content": message.content,
                    "tool_calls": []
                }
        
        except Exception as e:
            logging.error(f"Error generating with tools using OpenAI: {e}")
            return {
                "content": f"Error: {str(e)}",
                "tool_calls": []
            }
    
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
            system_message: Optional system message for the model.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional OpenAI-specific parameters.
            
        Returns:
            The extracted JSON data.
        """
        # Set default system message if not provided
        if not system_message:
            system_message = "Extract the requested information and respond only with a valid JSON object according to the specified schema. Do not include any other text."
        
        # Set parameters
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        # Make the API call with response format JSON
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Schema: {json.dumps(schema)}\n\nPrompt: {prompt}"}
                ],
                temperature=temp,
                max_tokens=tokens,
                response_format={"type": "json_object"},
                **kwargs
            )
            
            # Extract and parse the response
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logging.error(f"Failed to parse JSON from response: {content}")
                return {"error": "Failed to parse JSON response"}
        
        except Exception as e:
            logging.error(f"Error extracting JSON with OpenAI: {e}")
            return {"error": str(e)}
    
    def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: The text to embed.
            **kwargs: Additional OpenAI-specific parameters.
            
        Returns:
            The embedding vector as a list of floats.
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
                **kwargs
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            logging.error(f"Error generating embedding with OpenAI: {e}")
            return [] 