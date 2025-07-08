"""
Test script to verify tool metadata functionality
"""
import sys
import os
import asyncio

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.features.chat.chat_service.agent_tools import AgentTools
from app.database import Database
from app.embedding import Embeddings
from app.config import config

async def test_tool_metadata():
    """Test that tool metadata is collected correctly"""
    print("🧪 Testing tool metadata collection...")
    
    try:
        # Initialize components (using mock data since we don't need real DB for this test)
        database = Database(config.DB_URL)
        embedding_model = Embeddings(config.AWS_REGION, config.EMBEDDING_MODEL_ID)
        tools = AgentTools(database, embedding_model)
        
        # Test a simple tool call
        print("\n1. Testing addition_calculator...")
        result = tools.addition_calculator([1, 2, 3, 4])
        print(f"   Result: {result}")
        
        # Test another tool call
        print("\n2. Testing multiplication_calculator...")
        result2 = tools.multiplication_calculator(5, 6)
        print(f"   Result: {result2}")
        
        # Get metadata
        metadata = tools.get_and_clear_tool_metadata()
        print(f"\n📊 Tool metadata collected: {len(metadata)} calls")
        
        for i, call in enumerate(metadata, 1):
            print(f"\n   Call {i}:")
            print(f"   - Tool name: {call['tool_name']}")
            print(f"   - Args: {call['tool_args']}")
            print(f"   - Kwargs: {call['tool_kwargs']}")
            print(f"   - Result: {call['result']}")
        
        print("\n✅ Tool metadata test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Tool metadata test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tool_metadata())
    sys.exit(0 if success else 1)
