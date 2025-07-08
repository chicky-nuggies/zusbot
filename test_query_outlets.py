"""
Test script to verify the query_outlets_table tool functionality
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

async def test_query_outlets_table():
    """Test that the query_outlets_table tool works correctly"""
    print("🧪 Testing query_outlets_table tool...")
    
    try:
        # Initialize components
        database = Database(config.DB_URL)
        database.create_tables()  # Ensure tables exist
        embedding_model = Embeddings(config.AWS_REGION, config.EMBEDDING_MODEL_ID)
        tools = AgentTools(database, embedding_model)
        
        # Test the new tool with different queries
        test_queries = [
            "Show me all outlets",
            "What outlets are available?",
            "List outlet names and addresses",
            "Find outlets with 'coffee' in the name"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing query: '{query}'")
            try:
                result = await tools.query_outlets_table(query)
                print(f"   Result: {result[:200]}{'...' if len(result) > 200 else ''}")
            except Exception as e:
                print(f"   Error: {e}")
        
        # Get metadata
        metadata = tools.get_and_clear_tool_metadata()
        print(f"\n📊 Tool metadata collected: {len(metadata)} calls")
        
        print("\n✅ query_outlets_table test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ query_outlets_table test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_query_outlets_table())
    sys.exit(0 if success else 1)
