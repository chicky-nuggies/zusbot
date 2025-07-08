#!/usr/bin/env python3
"""
Test script to verify the full agent integration with query_outlets_table tool
"""
import sys
import os
import asyncio

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.features.chat.chat_service.agent_run import ChatAgent
from app.config import config

async def test_full_agent():
    """Test that the full agent works with query_outlets_table tool"""
    print("🧪 Testing full agent integration with query_outlets_table...")
    
    try:
        # Initialize the agent
        agent = ChatAgent(config.CHAT_MODEL_ID)
        
        # Test with a query that should use the new tool
        test_query = "List all outlet names that contain the word 'mall'"
        print(f"\n🔍 Testing query: '{test_query}'")
        
        response, history, tool_calls = await agent.chat(test_query)
        
        print(f"\n📝 Response: {response[:300]}{'...' if len(response) > 300 else ''}")
        print(f"\n🔧 Tool calls: {len(tool_calls)}")
        
        for tool_call in tool_calls:
            print(f"  - {tool_call['tool_name']}: {tool_call['tool_args']}")
        
        print("\n✅ Full agent integration test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Full agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_agent())
    sys.exit(0 if success else 1)
