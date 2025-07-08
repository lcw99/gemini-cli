#!/usr/bin/env python3
"""
Quick test script to validate the Python library functionality
"""

import asyncio
import sys
from gemini_core import GeminiClient, Config
from example_tools import register_example_tools

async def test_basic_functionality():
    """Test basic functionality of the library"""
    print("🧪 Testing Gemini CLI Python Library")
    print("="*40)
    
    # Initialize
    config = Config(
        api_key="test-key",
        model="gemini-pro",
        max_tokens=2000,
        user_memory="Test user for validation"
    )
    
    client = GeminiClient(config)
    register_example_tools(client.tool_registry)
    
    print("✅ Library initialized successfully")
    print(f"✅ Registered {len(client.tool_registry.get_all_tools())} tools")
    
    # Test tool execution
    test_cases = [
        ("Math tool", "calculate 5 * 6 + 2"),
        ("Echo tool", "echo 'Hello Python Library!'"),
        ("Memory tool", "remember my test value is 42")
    ]
    
    for test_name, message in test_cases:
        print(f"\n🔧 Testing {test_name}...")
        try:
            response = await client.send_message(message)
            print(f"   Response: {response[:100]}...")
            print(f"✅ {test_name} executed successfully")
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            return False
    
    # Test compression
    print(f"\n📊 Testing compression...")
    compression_info = await client.try_compress_chat(force=True)
    if compression_info:
        print(f"✅ Compression successful: {compression_info.original_token_count} → {compression_info.new_token_count} tokens")
    else:
        print("ℹ️ No compression needed")
    
    print(f"\n🎉 All tests passed!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1)