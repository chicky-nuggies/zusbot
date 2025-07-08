#!/usr/bin/env python3
"""
Test the API endpoints to verify query_outlets_table integration
"""
import requests
import json

def test_chat_endpoint():
    """Test the /chat endpoint with a query that should use query_outlets_table"""
    print("🧪 Testing /chat endpoint...")
    
    url = "http://localhost:8000/chat"
    payload = {
        "message": "Find outlets with 'mall' in the name",
        "session_id": None
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✅ Status: {data.get('status')}")
        print(f"📝 Response preview: {data.get('response', '')[:200]}...")
        print(f"🔧 Tool calls: {len(data.get('tool_calls', []))}")
        
        for tool_call in data.get('tool_calls', []):
            print(f"  - {tool_call.get('tool_name')}: {tool_call.get('tool_kwargs', {}).get('nl_query', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chat endpoint test failed: {e}")
        return False

def test_chat_stream_endpoint():
    """Test the /chat-stream endpoint with a query that should use query_outlets_table"""
    print("\n🧪 Testing /chat-stream endpoint...")
    
    url = "http://localhost:8000/chat-stream"
    payload = {
        "message": "How many outlets contain the word 'mall'?",
        "session_id": None
    }
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        response.raise_for_status()
        
        chunks = []
        tool_calls = []
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # Remove 'data: ' prefix
                    if data_str != '[DONE]':
                        try:
                            data = json.loads(data_str)
                            if data.get('chunk'):
                                chunks.append(data['chunk'])
                            if data.get('tool_calls'):
                                tool_calls = data['tool_calls']
                        except json.JSONDecodeError:
                            pass
        
        full_response = ''.join(chunks)
        print(f"✅ Streaming completed")
        print(f"📝 Response preview: {full_response[:200]}...")
        print(f"🔧 Tool calls: {len(tool_calls)}")
        
        for tool_call in tool_calls:
            print(f"  - {tool_call.get('tool_name')}: {tool_call.get('tool_kwargs', {}).get('nl_query', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Stream endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing API endpoints...")
    
    success1 = test_chat_endpoint()
    success2 = test_chat_stream_endpoint()
    
    if success1 and success2:
        print("\n✅ All API endpoint tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
