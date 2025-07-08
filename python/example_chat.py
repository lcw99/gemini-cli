#!/usr/bin/env python3
"""
Example Chat Script for Gemini CLI Python Library

This script demonstrates the core functionality of the Python Gemini CLI library:
- Text-based chat loop with the Gemini AI
- Tool activation (math calculator, echo, memory)
- Memory usage and conversation context retention
- Automatic history summarization when conversations get long

Run this script to see the library in action!
"""

import asyncio
import sys
from typing import Optional

from gemini_core import GeminiClient, Config, Content
from example_tools import register_example_tools


class ChatInterface:
    """
    Simple text-based chat interface for demonstrating the Gemini CLI library
    """
    
    def __init__(self):
        # Initialize configuration
        self.config = Config(
            api_key="demo-key",  # Mock API key for demonstration
            model="gemini-pro",
            max_tokens=4000,  # Lower limit to demonstrate compression
            compression_threshold=0.7,  # Compress at 70% of limit
            user_memory="User prefers concise explanations and enjoys testing new features."
        )
        
        # Initialize Gemini client
        self.client = GeminiClient(self.config)
        
        # Register example tools
        register_example_tools(self.client.tool_registry)
        
        # Chat state
        self.running = True
        self.message_count = 0
        
        print("🤖 Gemini CLI Python Library Demo")
        print("="*50)
        print()
    
    async def start_chat(self):
        """Start the interactive chat loop"""
        print("Welcome to the Gemini CLI Python demo!")
        print()
        print("Available commands:")
        print("  - Type any message to chat with Gemini")
        print("  - Try: 'calculate 2 + 3 * 4' to test the math tool")
        print("  - Try: 'echo hello world' to test the echo tool") 
        print("  - Try: 'remember my name is John' to test memory")
        print("  - Type '/help' for more commands")
        print("  - Type '/quit' to exit")
        print()
        
        try:
            while self.running:
                await self._handle_user_input()
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
        except Exception as e:
            print(f"\n\nError: {e}")
            print("Chat session ended unexpectedly.")
    
    async def _handle_user_input(self):
        """Handle a single user input"""
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                return
            
            # Handle special commands
            if user_input.startswith('/'):
                await self._handle_command(user_input)
                return
            
            # Send message to Gemini
            print("Gemini: ", end="", flush=True)
            response = await self.client.send_message(user_input)
            print(response)
            print()
            
            self.message_count += 1
            
            # Demonstrate compression after several messages
            if self.message_count % 5 == 0:
                await self._check_compression_demo()
                
        except EOFError:
            # Handle Ctrl+D
            self.running = False
        except Exception as e:
            print(f"Error processing input: {e}")
            print()
    
    async def _handle_command(self, command: str):
        """Handle special chat commands"""
        cmd = command[1:].lower()
        
        if cmd == 'quit' or cmd == 'exit':
            self.running = False
            print("Goodbye! 👋")
            
        elif cmd == 'help':
            await self._show_help()
            
        elif cmd == 'history':
            await self._show_history()
            
        elif cmd == 'stats':
            await self._show_stats()
            
        elif cmd == 'tools':
            await self._show_tools()
            
        elif cmd == 'reset':
            await self._reset_chat()
            
        elif cmd == 'compress':
            await self._force_compression()
            
        else:
            print(f"Unknown command: {command}")
            print("Type '/help' for available commands.")
        
        print()
    
    async def _show_help(self):
        """Show help information"""
        print("\n📖 Available Commands:")
        print("  /help      - Show this help message")
        print("  /history   - Show conversation history") 
        print("  /stats     - Show conversation statistics")
        print("  /tools     - Show available tools")
        print("  /reset     - Reset the chat history")
        print("  /compress  - Force compress the chat history")
        print("  /quit      - Exit the chat")
        print()
        print("🔧 Example Tool Usage:")
        print("  'calculate 10 + 5 * 2'")
        print("  'echo hello world'")
        print("  'remember my favorite color is blue'")
        print("  'what was my favorite color?'")
    
    async def _show_history(self):
        """Show conversation history"""
        history = self.client.get_history()
        
        print(f"\n📜 Conversation History ({len(history)} messages):")
        print("-" * 40)
        
        for i, content in enumerate(history):
            role = content.role.upper()
            text_parts = []
            for part in content.parts:
                if 'text' in part:
                    text = part['text']
                    # Truncate long messages for display
                    if len(text) > 100:
                        text = text[:100] + "..."
                    text_parts.append(text)
            
            if text_parts:
                print(f"{i+1}. {role}: {' '.join(text_parts)}")
    
    async def _show_stats(self):
        """Show conversation statistics"""
        history = self.client.get_history()
        token_count = await self.client.api.count_tokens(history)
        
        print(f"\n📊 Conversation Statistics:")
        print(f"  Messages: {len(history)}")
        print(f"  Estimated tokens: {token_count}")
        print(f"  Token limit: {self.config.max_tokens}")
        print(f"  Usage: {(token_count / self.config.max_tokens) * 100:.1f}%")
        print(f"  Compression threshold: {self.config.compression_threshold * 100:.0f}%")
    
    async def _show_tools(self):
        """Show available tools"""
        tools = self.client.tool_registry.get_all_tools()
        
        print(f"\n🔧 Available Tools ({len(tools)}):")
        for tool in tools:
            print(f"  • {tool.display_name} ({tool.name})")
            print(f"    {tool.description}")
            print()
    
    async def _reset_chat(self):
        """Reset the chat history"""
        await self.client.reset_chat()
        self.message_count = 0
        print("🔄 Chat history has been reset.")
    
    async def _force_compression(self):
        """Force compress the chat history"""
        compression_info = await self.client.try_compress_chat(force=True)
        
        if compression_info:
            ratio = compression_info.compression_ratio * 100
            print(f"📦 Chat compressed successfully!")
            print(f"  Original tokens: {compression_info.original_token_count}")
            print(f"  New tokens: {compression_info.new_token_count}")
            print(f"  Compression ratio: {ratio:.1f}%")
        else:
            print("📦 No compression was performed (history too short or already compressed).")
    
    async def _check_compression_demo(self):
        """Check if compression happened and show info"""
        history = self.client.get_history()
        token_count = await self.client.api.count_tokens(history)
        threshold = self.config.compression_threshold * self.config.max_tokens
        
        if token_count >= threshold:
            print(f"\n💡 Note: Conversation is getting long ({token_count} tokens).")
            print("    Automatic compression may occur on the next message.")
            print("    Use '/compress' to force compression now, or '/stats' to see details.")
            print()


async def main():
    """Main entry point for the chat demo"""
    print("Starting Gemini CLI Python Demo...")
    print()
    
    try:
        chat = ChatInterface()
        await chat.start_chat()
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


def demo_scenario():
    """
    Run a predefined demo scenario to showcase features
    """
    print("🎬 Running Demo Scenario...")
    print("="*50)
    
    async def run_demo():
        config = Config(
            api_key="demo-key",
            model="gemini-pro", 
            max_tokens=2000,  # Small limit to show compression
            user_memory="Demo user testing the Python library"
        )
        
        client = GeminiClient(config)
        register_example_tools(client.tool_registry)
        
        # Demo conversation
        scenarios = [
            "Hello! Can you help me test this library?",
            "Calculate 15 + 27 * 3",
            "Echo the message 'Hello from Python!'",
            "Remember that my favorite programming language is Python",
            "What's my favorite programming language?",
            "Calculate (100 + 50) / 3",
            "Echo 'Testing tool execution' 3 times"
        ]
        
        for i, message in enumerate(scenarios):
            print(f"\n{i+1}. User: {message}")
            response = await client.send_message(message)
            print(f"   Gemini: {response}")
            
            # Show stats periodically
            if i == 3:
                history = client.get_history()
                token_count = await client.api.count_tokens(history)
                print(f"\n   [Stats: {len(history)} messages, ~{token_count} tokens]")
        
        # Demonstrate compression
        print("\n🗜️ Demonstrating chat compression...")
        compression_info = await client.try_compress_chat(force=True)
        if compression_info:
            print(f"   Compressed from {compression_info.original_token_count} to {compression_info.new_token_count} tokens")
            print(f"   Compression ratio: {compression_info.compression_ratio:.2%}")
        
        print("\n✅ Demo scenario completed!")
    
    return asyncio.run(run_demo())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Run automated demo
        try:
            demo_scenario()
        except Exception as e:
            print(f"Demo failed: {e}")
            sys.exit(1)
    else:
        # Run interactive chat
        exit_code = asyncio.run(main())
        sys.exit(exit_code)