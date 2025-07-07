import functools
from typing import List

import sys
import os
# Add parent directory to path to import from root
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import Database
from app.embedding import Embeddings


def log_tool_call(func):
    """Decorator to log tool calls for debugging"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Tool called: {func.__name__}")
        print(f"Args: {args}")
        print(f"Kwargs: {kwargs}")
        
        # Store tool call info in the wrapper for later access
        wrapper._last_tool_call = {
            "tool_called": func.__name__,
            "args": args,
            "kwargs": kwargs
        }
        
        result = func(*args, **kwargs)
        print(f"Result: {result}")
        
        # Store result info
        wrapper._last_result = {
            "result": result,
            "tool_name": func.__name__
        }
        
        return result

    return wrapper


class AgentTools:
    """Class containing all agent tools with access to database and embedding model"""
    
    def __init__(self, database: Database, embedding_model: Embeddings):
        self.database = database
        self.embedding_model = embedding_model
    
    @log_tool_call
    def get_products(self):
        """Gets information about products"""
        return self.database.get_all_products()

    @log_tool_call
    def get_similar_products(self, search_query: str):
        """Performs a semantic similarity search over Zus Coffee's drinkware catalog"""
        query_embedding = self.embedding_model.generate_embeddings(search_query)
        return self.database.search_similar_products(query_embedding, threshold=0)

    @log_tool_call
    def get_outlet(self):
        """Gets information about store outlets"""
        return {
            'branch': 'ss2',
            'operational-hours': '9am-6pm'
        }

    @log_tool_call
    def addition_calculator(self, numbers: list[int]):
        """Sums up numbers"""
        return sum(numbers)

    @log_tool_call
    def multiplication_calculator(self, num: int, multiplier: int):
        """Multiplies numbers"""
        return num * multiplier

    def get_tool_call_info(self):
        """Get information about the last tool calls made"""
        tool_calls = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_last_tool_call'):
                tool_calls.append({
                    "tool_call": attr._last_tool_call,
                    "result": getattr(attr, '_last_result', None)
                })
        return tool_calls
    
    def clear_tool_call_info(self):
        """Clear stored tool call information"""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_last_tool_call'):
                delattr(attr, '_last_tool_call')
                if hasattr(attr, '_last_result'):
                    delattr(attr, '_last_result')
