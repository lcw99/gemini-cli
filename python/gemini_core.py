"""
Gemini CLI Core Python Library

This module provides the core functionality of Gemini-CLI in Python, including:
- API client for Gemini communication (mock/placeholder)
- Tool registration and execution logic
- State management for conversations/sessions
- Chat history compression and memory management
- Prompt construction and management

Based on the architecture described in docs/architecture.md
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Union, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum


# Type definitions
ToolParams = Dict[str, Any]
ToolResult = Dict[str, Any]

TParams = TypeVar('TParams')
TResult = TypeVar('TResult')


class ToolConfirmationOutcome(Enum):
    """Tool confirmation outcomes matching the TypeScript interface"""
    PROCEED_ONCE = "proceed_once"
    PROCEED_ALWAYS = "proceed_always" 
    PROCEED_ALWAYS_SERVER = "proceed_always_server"
    PROCEED_ALWAYS_TOOL = "proceed_always_tool"
    MODIFY_WITH_EDITOR = "modify_with_editor"
    CANCEL = "cancel"


@dataclass
class ToolCallConfirmationDetails:
    """Details for tool call confirmation"""
    type: str
    title: str
    command: Optional[str] = None
    server_name: Optional[str] = None
    tool_name: Optional[str] = None
    prompt: Optional[str] = None


@dataclass
class Content:
    """Represents a piece of conversation content"""
    role: str  # 'user', 'model', 'system'
    parts: List[Dict[str, Any]]
    
    @classmethod
    def from_text(cls, role: str, text: str) -> 'Content':
        """Create content from simple text"""
        return cls(role=role, parts=[{'text': text}])


@dataclass
class ChatCompressionInfo:
    """Information about chat compression operation"""
    original_token_count: int
    new_token_count: int
    compression_ratio: float = field(init=False)
    
    def __post_init__(self):
        if self.original_token_count > 0:
            self.compression_ratio = self.new_token_count / self.original_token_count
        else:
            self.compression_ratio = 1.0


class BaseTool(ABC, Generic[TParams, TResult]):
    """
    Abstract base class for tools, mirroring the TypeScript BaseTool interface
    """
    
    def __init__(
        self,
        name: str,
        display_name: str,
        description: str,
        parameter_schema: Dict[str, Any],
        is_output_markdown: bool = True,
        can_update_output: bool = False
    ):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.parameter_schema = parameter_schema
        self.is_output_markdown = is_output_markdown
        self.can_update_output = can_update_output
    
    @property
    def schema(self) -> Dict[str, Any]:
        """Function declaration schema for the Gemini API"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.parameter_schema
        }
    
    def validate_tool_params(self, params: TParams) -> Optional[str]:
        """
        Validates the parameters for the tool
        Returns an error message string if invalid, None otherwise
        """
        # Basic validation - can be overridden by subclasses
        if not isinstance(params, dict):
            return "Parameters must be a dictionary"
        return None
    
    def get_description(self, params: TParams) -> str:
        """
        Gets a pre-execution description of the tool operation
        """
        return f"Executing {self.display_name} with parameters: {json.dumps(params, indent=2)}"
    
    async def should_confirm_execute(
        self, 
        params: TParams
    ) -> Union[ToolCallConfirmationDetails, bool]:
        """
        Determines if the tool should prompt for confirmation before execution
        Returns confirmation details if confirmation needed, False otherwise
        """
        return False
    
    @abstractmethod
    async def execute(
        self, 
        params: TParams,
        update_output: Optional[Callable[[str], None]] = None
    ) -> TResult:
        """
        Execute the tool with the given parameters
        Must be implemented by subclasses
        """
        pass


class ToolRegistry:
    """
    Registry for managing tools, similar to the TypeScript ToolRegistry
    """
    
    def __init__(self, config: 'Config'):
        self.config = config
        self.tools: Dict[str, BaseTool] = {}
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool in the registry"""
        if self.tools.get(tool.name):
            print(f"Warning: Tool with name '{tool.name}' is already registered. Overwriting.")
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def get_function_declarations(self) -> List[Dict[str, Any]]:
        """Get function declarations for all registered tools"""
        return [tool.schema for tool in self.tools.values()]
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    async def discover_tools(self) -> None:
        """
        Discover tools from project (placeholder implementation)
        In a real implementation, this would scan for tool definitions
        """
        print("Tool discovery not implemented in this example")


class PromptManager:
    """
    Manages prompt construction and system prompts
    """
    
    @staticmethod
    def get_core_system_prompt(user_memory: Optional[str] = None) -> str:
        """
        Generate the core system prompt for Gemini
        Based on the TypeScript getCoreSystemPrompt function
        """
        base_prompt = """You are a helpful AI assistant with access to various tools. 

# Operational Guidelines

## Tone and Style
- Be concise and direct in your responses
- Focus on being helpful and accurate
- Use tools when appropriate to accomplish tasks

## Tool Usage
- You have access to various tools that can help you accomplish tasks
- Always validate tool parameters before use
- Provide clear descriptions of what tools will do before execution
"""
        
        if user_memory:
            return f"{base_prompt}\n\n# User Context\n{user_memory}"
        
        return base_prompt
    
    @staticmethod
    def get_compression_prompt() -> str:
        """
        Generate prompt for chat history compression
        """
        return """Please create a concise summary of the conversation history so far.

Focus on:
- Key topics discussed
- Important decisions made
- Tools used and their outcomes
- Any ongoing context that should be preserved

Provide the summary in a clear, structured format that preserves the essential information while reducing the overall length."""


@dataclass 
class Config:
    """
    Configuration management for the Gemini client
    """
    api_key: Optional[str] = None
    model: str = "gemini-pro"
    max_tokens: int = 8192
    compression_threshold: float = 0.8  # Compress when 80% of token limit reached
    compression_preserve_threshold: float = 0.3  # Preserve last 30% of conversation
    user_memory: Optional[str] = None
    
    def get_model(self) -> str:
        return self.model
    
    def get_user_memory(self) -> Optional[str]:
        return self.user_memory
    
    def set_user_memory(self, memory: str) -> None:
        self.user_memory = memory


class MockGeminiAPI:
    """
    Mock Gemini API client for demonstration purposes
    In a real implementation, this would use the actual Gemini API
    """
    
    def __init__(self, config: Config):
        self.config = config
    
    async def generate_content(
        self,
        contents: List[Content],
        tools: Optional[List[Dict[str, Any]]] = None,
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mock content generation
        Returns a simple response or tool call for demonstration
        """
        # Simulate API delay
        await self._simulate_delay(0.5)
        
        # Get the last user message
        user_messages = [c for c in contents if c.role == 'user']
        if not user_messages:
            return {'text': "I'm ready to help! What would you like to do?"}
        
        last_message = user_messages[-1]
        text = ""
        for part in last_message.parts:
            if 'text' in part:
                text += part['text']
        
        text_lower = text.lower()
        
        # Check for math operations
        if any(word in text_lower for word in ['calculate', 'math', '+', '-', '*', '/', 'compute']):
            # Return a tool call
            return {
                'tool_calls': [{
                    'name': 'math_calculator',
                    'parameters': {'expression': text}
                }]
            }
        
        # Check for echo requests  
        elif 'echo' in text_lower:
            return {
                'tool_calls': [{
                    'name': 'echo_tool',
                    'parameters': {'message': text.replace('echo', '').strip()}
                }]
            }
        
        # Default response
        return {
            'text': f"I understand you said: '{text}'. I can help with math calculations or echo messages. Try asking me to calculate something or echo a message!"
        }
    
    async def count_tokens(self, contents: List[Content]) -> int:
        """Mock token counting - rough estimate based on character count"""
        total_chars = 0
        for content in contents:
            for part in content.parts:
                if 'text' in part:
                    total_chars += len(part['text'])
        
        # Rough approximation: 4 characters per token
        return total_chars // 4
    
    async def _simulate_delay(self, seconds: float):
        """Simulate API delay"""
        time.sleep(seconds)


class GeminiClient:
    """
    Main client for interacting with Gemini API and managing conversations
    Based on the TypeScript GeminiClient class
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.api = MockGeminiAPI(config)
        self.tool_registry = ToolRegistry(config)
        self.history: List[Content] = []
        self.compression_token_threshold = 0.8
        self.compression_preserve_threshold = 0.3
        
        # Initialize with system message
        system_prompt = PromptManager.get_core_system_prompt(config.get_user_memory())
        self.history.append(Content.from_text('system', system_prompt))
    
    def get_history(self) -> List[Content]:
        """Get conversation history"""
        return self.history.copy()
    
    def set_history(self, history: List[Content]) -> None:
        """Set conversation history"""
        self.history = history.copy()
    
    async def reset_chat(self) -> None:
        """Reset the chat history"""
        system_prompt = PromptManager.get_core_system_prompt(self.config.get_user_memory())
        self.history = [Content.from_text('system', system_prompt)]
    
    async def send_message(self, message: str) -> str:
        """
        Send a message and get response, handling tool calls automatically
        """
        # Add user message to history
        user_content = Content.from_text('user', message)
        self.history.append(user_content)
        
        # Check if compression is needed
        await self._check_and_compress_if_needed()
        
        # Get tools for API call
        tools = self.tool_registry.get_function_declarations()
        tool_config = [{'function_declarations': tools}] if tools else None
        
        # Generate response
        response = await self.api.generate_content(
            self.history,
            tools=tool_config,
            system_instruction=PromptManager.get_core_system_prompt(self.config.get_user_memory())
        )
        
        # Handle response
        if 'tool_calls' in response:
            # Execute tool calls
            tool_results = []
            for tool_call in response['tool_calls']:
                result = await self._execute_tool_call(tool_call)
                tool_results.append(result)
            
            # Add tool results to history and get final response
            tool_content = Content.from_text('function', json.dumps(tool_results))
            self.history.append(tool_content)
            
            # Generate final response
            final_response = await self.api.generate_content(self.history)
            response_text = final_response.get('text', 'Tool execution completed.')
        else:
            response_text = response.get('text', 'No response generated.')
        
        # Add model response to history
        model_content = Content.from_text('model', response_text)
        self.history.append(model_content)
        
        return response_text
    
    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool call"""
        tool_name = tool_call['name']
        tool_params = tool_call.get('parameters', {})
        
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return {
                'tool_name': tool_name,
                'error': f"Tool '{tool_name}' not found"
            }
        
        # Validate parameters
        validation_error = tool.validate_tool_params(tool_params)
        if validation_error:
            return {
                'tool_name': tool_name,
                'error': f"Parameter validation failed: {validation_error}"
            }
        
        # Check if confirmation is needed
        confirmation = await tool.should_confirm_execute(tool_params)
        if confirmation and confirmation is not False:
            # In a real implementation, this would prompt the user
            print(f"Tool execution requires confirmation: {tool.get_description(tool_params)}")
            # For demo purposes, auto-approve
            print("Auto-approving for demo...")
        
        try:
            # Execute the tool
            result = await tool.execute(tool_params)
            return {
                'tool_name': tool_name,
                'result': result
            }
        except Exception as e:
            return {
                'tool_name': tool_name,
                'error': str(e)
            }
    
    async def _check_and_compress_if_needed(self) -> Optional[ChatCompressionInfo]:
        """Check if compression is needed and compress if so"""
        if len(self.history) < 5:  # Don't compress very short conversations
            return None
            
        token_count = await self.api.count_tokens(self.history)
        max_tokens = self.config.max_tokens
        
        if token_count < (self.compression_token_threshold * max_tokens):
            return None
        
        return await self.try_compress_chat()
    
    async def try_compress_chat(self, force: bool = False) -> Optional[ChatCompressionInfo]:
        """
        Compress chat history to reduce token count
        Based on the TypeScript tryCompressChat method
        """
        if len(self.history) < 2:
            return None
            
        original_token_count = await self.api.count_tokens(self.history)
        
        # Find split point - preserve recent conversation
        preserve_count = max(2, int(len(self.history) * self.compression_preserve_threshold))
        split_index = len(self.history) - preserve_count
        
        history_to_compress = self.history[:split_index]
        history_to_keep = self.history[split_index:]
        
        if len(history_to_compress) < 2:
            return None
        
        # Generate summary
        summary_prompt = f"""Please summarize this conversation history:

{self._format_history_for_summary(history_to_compress)}

{PromptManager.get_compression_prompt()}"""
        
        summary_response = await self.api.generate_content([
            Content.from_text('user', summary_prompt)
        ])
        
        summary = summary_response.get('text', 'Summary not available')
        
        # Replace compressed history with summary
        new_history = [
            self.history[0],  # Keep system message
            Content.from_text('user', f"Previous conversation summary: {summary}"),
            Content.from_text('model', "Got it. Thanks for the additional context!"),
            *history_to_keep
        ]
        
        self.history = new_history
        new_token_count = await self.api.count_tokens(self.history)
        
        return ChatCompressionInfo(
            original_token_count=original_token_count,
            new_token_count=new_token_count
        )
    
    def _format_history_for_summary(self, history: List[Content]) -> str:
        """Format history for summarization"""
        formatted = []
        for content in history:
            role = content.role.upper()
            text_parts = []
            for part in content.parts:
                if 'text' in part:
                    text_parts.append(part['text'])
            if text_parts:
                formatted.append(f"{role}: {' '.join(text_parts)}")
        return '\n'.join(formatted)


# Export main classes for easy import
__all__ = [
    'GeminiClient',
    'ToolRegistry', 
    'BaseTool',
    'Config',
    'PromptManager',
    'Content',
    'ChatCompressionInfo',
    'ToolConfirmationOutcome',
    'ToolCallConfirmationDetails'
]