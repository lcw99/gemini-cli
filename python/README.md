# Gemini CLI Python Library

This directory contains a Python implementation of the core Gemini CLI functionality, based on the architecture described in `docs/architecture.md`. The library provides a clean, extensible way to interact with Gemini AI, manage tools, and handle conversation state and memory.

## Architecture Overview

The Python library follows the same modular design principles as the main TypeScript implementation:

- **Core Logic Separation**: Clean separation between core functionality and UI/CLI code
- **Extensible Tool System**: Easy registration and execution of custom tools
- **State Management**: Conversation history and session management
- **Memory Management**: Chat history compression and context preservation
- **Modularity**: Components can be used independently or together

## Files

### `gemini_core.py`
The main library module containing:

- **`GeminiClient`**: Main client for API communication and conversation management
- **`ToolRegistry`**: Tool registration, discovery, and execution management
- **`BaseTool`**: Abstract base class for creating custom tools
- **`Config`**: Configuration management for API settings and behavior
- **`PromptManager`**: System prompt construction and management
- **`MockGeminiAPI`**: Mock API client for demonstration (replace with real Gemini API)

### `example_tools.py`
Example tool implementations demonstrating the tool pattern:

- **`MathCalculatorTool`**: Evaluates mathematical expressions safely
- **`EchoTool`**: Simple echo tool for testing and demonstration
- **`MemoryTool`**: Manages user memory/context across conversations

### `example_chat.py`
Interactive chat demonstration script showcasing:

- Text-based chat loop with Gemini AI
- Tool activation and execution
- Memory usage and context retention
- Automatic history summarization
- Interactive commands for managing the chat session

## Key Features

### 🔧 Tool System
- **Easy Extension**: Create tools by inheriting from `BaseTool`
- **Parameter Validation**: Built-in parameter validation with detailed error messages
- **Confirmation Support**: Tools can require user confirmation before execution
- **Async Execution**: Non-blocking tool execution with progress updates

### 💭 Memory Management
- **Conversation History**: Maintains full conversation context
- **Automatic Compression**: Compresses long conversations to stay within token limits
- **Context Preservation**: Preserves recent conversation while summarizing older parts
- **User Memory**: Persistent memory storage across conversations

### ⚙️ Configuration
- **Flexible Settings**: Configurable token limits, compression thresholds, and behavior
- **Memory Integration**: Built-in user memory support
- **Model Selection**: Support for different Gemini models

### 🔄 State Management
- **Session Persistence**: Maintains conversation state across interactions
- **History Management**: Full conversation history with compression support
- **Reset Capability**: Easy conversation reset and cleanup

## Usage

### Basic Usage

```python
from gemini_core import GeminiClient, Config
from example_tools import register_example_tools

# Initialize configuration
config = Config(
    api_key="your-api-key",
    model="gemini-pro",
    max_tokens=8192
)

# Create client and register tools
client = GeminiClient(config)
register_example_tools(client.tool_registry)

# Start chatting
response = await client.send_message("Calculate 15 + 27 * 3")
print(response)
```

### Creating Custom Tools

```python
from gemini_core import BaseTool
from typing import Dict, Any, Optional, Callable

class MyCustomTool(BaseTool[Dict[str, Any], Dict[str, Any]]):
    def __init__(self):
        super().__init__(
            name="my_tool",
            display_name="My Custom Tool",
            description="Description of what this tool does",
            parameter_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "First parameter"}
                },
                "required": ["param1"]
            }
        )
    
    async def execute(self, params: Dict[str, Any], 
                     update_output: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        # Your tool logic here
        return {
            "llmContent": "Tool execution result for LLM",
            "returnDisplay": "Display result for user"
        }

# Register the tool
client.tool_registry.register_tool(MyCustomTool())
```

### Running the Examples

#### Interactive Chat
```bash
cd python
python example_chat.py
```

#### Automated Demo
```bash
cd python  
python example_chat.py --demo
```

## Demo Commands

When running the interactive chat, you can use these commands:

- `/help` - Show available commands
- `/history` - View conversation history
- `/stats` - Show conversation statistics
- `/tools` - List available tools
- `/reset` - Reset chat history
- `/compress` - Force compress chat history
- `/quit` - Exit the chat

## Example Tool Usage

Try these examples in the chat:

- `"calculate 2 + 3 * 4"` - Test the math calculator
- `"echo hello world"` - Test the echo tool
- `"remember my name is John"` - Store information in memory
- `"what was my name?"` - Retrieve stored information

## Architecture Alignment

This Python implementation closely follows the architecture described in `docs/architecture.md`:

### Core Components
- **API Client**: `GeminiClient` handles Gemini API communication
- **Tool Management**: `ToolRegistry` manages tool registration and execution
- **State Management**: Conversation history and session state management
- **Prompt Construction**: `PromptManager` handles system prompts and context

### Design Principles
- **Modularity**: Core logic separated from UI/example code
- **Extensibility**: Easy tool addition through the `BaseTool` interface
- **User Experience**: Rich interactive features and clear feedback

### Chat History Compression
Implements the same compression strategy as the main TypeScript implementation:
- Monitors token usage against configurable thresholds
- Preserves recent conversation context
- Summarizes older conversation parts
- Maintains conversation continuity

## Future Enhancements

This implementation provides a solid foundation that could be extended with:

- Real Gemini API integration (replacing the mock API)
- File system tools (read/write files)
- Web search and fetching capabilities
- Shell command execution tools
- Advanced memory persistence (file/database storage)
- Tool discovery from external sources
- Integration with Model Context Protocol (MCP) servers

## Dependencies

The implementation uses only Python standard library modules:
- `asyncio` - Async/await support
- `json` - JSON parsing and serialization
- `time` - Time-related utilities
- `abc` - Abstract base classes
- `typing` - Type hints
- `dataclasses` - Data structures
- `enum` - Enumerations
- `re` - Regular expressions

This minimal dependency approach makes the library easy to integrate and deploy.