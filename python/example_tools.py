"""
Example tools for the Gemini CLI Python library

This module provides simple example tools that demonstrate how to extend
the Gemini CLI with custom functionality. These tools show the basic patterns
for creating tools that can be registered and executed by the Gemini client.
"""

import asyncio
import re
from typing import Dict, Any, Optional, Callable
from gemini_core import BaseTool


class MathCalculatorTool(BaseTool[Dict[str, Any], Dict[str, Any]]):
    """
    A simple math calculator tool that can evaluate basic mathematical expressions
    """
    
    def __init__(self):
        super().__init__(
            name="math_calculator",
            display_name="Math Calculator", 
            description="Calculates the result of mathematical expressions. Supports basic arithmetic operations (+, -, *, /, **, %, parentheses).",
            parameter_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate (e.g., '2 + 3 * 4', '(10 + 5) / 3')"
                    }
                },
                "required": ["expression"]
            },
            is_output_markdown=False
        )
    
    def validate_tool_params(self, params: Dict[str, Any]) -> Optional[str]:
        """Validate the math expression parameter"""
        base_validation = super().validate_tool_params(params)
        if base_validation:
            return base_validation
            
        if 'expression' not in params:
            return "Missing required parameter: expression"
            
        expression = params['expression']
        if not isinstance(expression, str):
            return "Expression must be a string"
            
        if not expression.strip():
            return "Expression cannot be empty"
            
        # Check for potentially unsafe operations
        unsafe_patterns = [
            r'import\s+',
            r'__\w+__',
            r'exec\s*\(',
            r'eval\s*\(',
            r'open\s*\(',
            r'file\s*\(',
        ]
        
        for pattern in unsafe_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return f"Expression contains potentially unsafe operations: {expression}"
        
        return None
    
    def get_description(self, params: Dict[str, Any]) -> str:
        """Get description of the calculation operation"""
        expression = params.get('expression', 'unknown')
        return f"Calculating the result of: {expression}"
    
    async def execute(
        self, 
        params: Dict[str, Any],
        update_output: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Execute the math calculation"""
        expression = params['expression'].strip()
        
        if update_output:
            update_output(f"Calculating: {expression}")
        
        try:
            # Use eval with restricted globals for safety
            # In production, you might want to use a proper math expression parser
            allowed_names = {
                "__builtins__": {},
                "abs": abs,
                "max": max,
                "min": min,
                "round": round,
                "pow": pow,
                "sum": sum,
            }
            
            result = eval(expression, allowed_names, {})
            
            return {
                "llmContent": f"The result of {expression} is {result}",
                "returnDisplay": f"**Calculation Result:**\n\n`{expression} = {result}`",
                "expression": expression,
                "result": result
            }
            
        except Exception as e:
            error_msg = f"Error calculating '{expression}': {str(e)}"
            return {
                "llmContent": f"Failed to calculate {expression}: {str(e)}",
                "returnDisplay": f"**Calculation Error:**\n\n```\n{error_msg}\n```",
                "expression": expression,
                "error": str(e)
            }


class EchoTool(BaseTool[Dict[str, Any], Dict[str, Any]]):
    """
    A simple echo tool that repeats the input message
    Useful for testing tool execution and demonstrating basic tool patterns
    """
    
    def __init__(self):
        super().__init__(
            name="echo_tool",
            display_name="Echo Tool",
            description="Echoes back the provided message. Useful for testing and debugging.",
            parameter_schema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to echo back"
                    },
                    "repeat_count": {
                        "type": "integer",
                        "description": "Number of times to repeat the message (default: 1, max: 5)",
                        "minimum": 1,
                        "maximum": 5,
                        "default": 1
                    }
                },
                "required": ["message"]
            },
            is_output_markdown=True
        )
    
    def validate_tool_params(self, params: Dict[str, Any]) -> Optional[str]:
        """Validate the echo parameters"""
        base_validation = super().validate_tool_params(params)
        if base_validation:
            return base_validation
            
        if 'message' not in params:
            return "Missing required parameter: message"
            
        message = params['message']
        if not isinstance(message, str):
            return "Message must be a string"
            
        repeat_count = params.get('repeat_count', 1)
        if not isinstance(repeat_count, int) or repeat_count < 1 or repeat_count > 5:
            return "repeat_count must be an integer between 1 and 5"
            
        return None
    
    def get_description(self, params: Dict[str, Any]) -> str:
        """Get description of the echo operation"""
        message = params.get('message', 'unknown')
        repeat_count = params.get('repeat_count', 1)
        
        if repeat_count == 1:
            return f"Echoing message: '{message}'"
        else:
            return f"Echoing message '{message}' {repeat_count} times"
    
    async def execute(
        self, 
        params: Dict[str, Any],
        update_output: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Execute the echo operation"""
        message = params['message']
        repeat_count = params.get('repeat_count', 1)
        
        if update_output:
            update_output(f"Echoing: {message}")
        
        # Simulate some processing time for demonstration
        await asyncio.sleep(0.1)
        
        # Create the repeated message
        repeated_messages = []
        for i in range(repeat_count):
            if repeat_count > 1:
                repeated_messages.append(f"{i+1}. {message}")
            else:
                repeated_messages.append(message)
        
        echoed_content = "\n".join(repeated_messages)
        
        return {
            "llmContent": f"Echoed: {echoed_content}",
            "returnDisplay": f"**Echo Output:**\n\n{echoed_content}",
            "original_message": message,
            "repeat_count": repeat_count,
            "echoed_content": echoed_content
        }


class MemoryTool(BaseTool[Dict[str, Any], Dict[str, Any]]):
    """
    A tool for managing user memory/context
    Allows storing and retrieving information across conversations
    """
    
    def __init__(self):
        super().__init__(
            name="memory_tool",
            display_name="Memory Tool",
            description="Manages user memory and context. Can store, retrieve, or update information that should be remembered across conversations.",
            parameter_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["store", "retrieve", "update", "clear"],
                        "description": "The action to perform: store new info, retrieve existing info, update existing info, or clear all memory"
                    },
                    "key": {
                        "type": "string", 
                        "description": "The key/identifier for the memory item (required for store, retrieve, update)"
                    },
                    "value": {
                        "type": "string",
                        "description": "The value to store or update (required for store and update actions)"
                    }
                },
                "required": ["action"]
            },
            is_output_markdown=True
        )
        self.memory_store: Dict[str, str] = {}
    
    def validate_tool_params(self, params: Dict[str, Any]) -> Optional[str]:
        """Validate memory tool parameters"""
        base_validation = super().validate_tool_params(params)
        if base_validation:
            return base_validation
            
        action = params.get('action')
        if not action:
            return "Missing required parameter: action"
            
        if action not in ['store', 'retrieve', 'update', 'clear']:
            return f"Invalid action: {action}. Must be one of: store, retrieve, update, clear"
            
        if action in ['store', 'retrieve', 'update'] and 'key' not in params:
            return f"Action '{action}' requires a 'key' parameter"
            
        if action in ['store', 'update'] and 'value' not in params:
            return f"Action '{action}' requires a 'value' parameter"
            
        return None
    
    def get_description(self, params: Dict[str, Any]) -> str:
        """Get description of the memory operation"""
        action = params.get('action', 'unknown')
        key = params.get('key', '')
        value = params.get('value', '')
        
        if action == 'store':
            return f"Storing memory item '{key}': {value[:50]}..."
        elif action == 'retrieve':
            return f"Retrieving memory item '{key}'"
        elif action == 'update':
            return f"Updating memory item '{key}': {value[:50]}..."
        elif action == 'clear':
            return "Clearing all memory"
        else:
            return f"Performing memory action: {action}"
    
    async def execute(
        self, 
        params: Dict[str, Any],
        update_output: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Execute the memory operation"""
        action = params['action']
        key = params.get('key')
        value = params.get('value')
        
        if update_output:
            update_output(f"Memory operation: {action}")
        
        if action == 'store':
            self.memory_store[key] = value
            return {
                "llmContent": f"Stored memory item '{key}'",
                "returnDisplay": f"**Memory Stored:**\n\n- **Key:** {key}\n- **Value:** {value}",
                "action": action,
                "key": key,
                "value": value,
                "success": True
            }
            
        elif action == 'retrieve':
            if key in self.memory_store:
                stored_value = self.memory_store[key]
                return {
                    "llmContent": f"Retrieved memory item '{key}': {stored_value}",
                    "returnDisplay": f"**Memory Retrieved:**\n\n- **Key:** {key}\n- **Value:** {stored_value}",
                    "action": action,
                    "key": key,
                    "value": stored_value,
                    "success": True
                }
            else:
                return {
                    "llmContent": f"Memory item '{key}' not found",
                    "returnDisplay": f"**Memory Not Found:**\n\nNo memory item found with key '{key}'",
                    "action": action,
                    "key": key,
                    "success": False,
                    "error": "Key not found"
                }
                
        elif action == 'update':
            if key in self.memory_store:
                old_value = self.memory_store[key]
                self.memory_store[key] = value
                return {
                    "llmContent": f"Updated memory item '{key}' from '{old_value}' to '{value}'",
                    "returnDisplay": f"**Memory Updated:**\n\n- **Key:** {key}\n- **Old Value:** {old_value}\n- **New Value:** {value}",
                    "action": action,
                    "key": key,
                    "old_value": old_value,
                    "new_value": value,
                    "success": True
                }
            else:
                # Store as new if doesn't exist
                self.memory_store[key] = value
                return {
                    "llmContent": f"Memory item '{key}' didn't exist, stored as new item",
                    "returnDisplay": f"**Memory Created:**\n\n- **Key:** {key}\n- **Value:** {value}\n\n*Note: Key didn't exist, so it was created as a new item.*",
                    "action": action,
                    "key": key,
                    "value": value,
                    "success": True
                }
                
        elif action == 'clear':
            cleared_count = len(self.memory_store)
            self.memory_store.clear()
            return {
                "llmContent": f"Cleared all memory ({cleared_count} items)",
                "returnDisplay": f"**Memory Cleared:**\n\nRemoved {cleared_count} memory items.",
                "action": action,
                "cleared_count": cleared_count,
                "success": True
            }
        
        else:
            return {
                "llmContent": f"Unknown memory action: {action}",
                "returnDisplay": f"**Error:**\n\nUnknown memory action: {action}",
                "action": action,
                "success": False,
                "error": f"Unknown action: {action}"
            }


def register_example_tools(tool_registry) -> None:
    """
    Register all example tools with the provided tool registry
    
    Args:
        tool_registry: The ToolRegistry instance to register tools with
    """
    tools = [
        MathCalculatorTool(),
        EchoTool(),
        MemoryTool()
    ]
    
    for tool in tools:
        tool_registry.register_tool(tool)
    
    print(f"Registered {len(tools)} example tools:")
    for tool in tools:
        print(f"  - {tool.display_name} ({tool.name})")


# Export tools for easy import
__all__ = [
    'MathCalculatorTool',
    'EchoTool', 
    'MemoryTool',
    'register_example_tools'
]