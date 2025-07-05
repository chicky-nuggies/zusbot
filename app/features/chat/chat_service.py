from __future__ import annotations as _annotations

import functools
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.settings import ModelSettings

import sys
import os
# Add parent directory to path to import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Database
from app.embedding import Embeddings
from ..config import config


def log_tool_call(func):
    """Decorator to log tool calls for debugging"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Tool called: {func.__name__}")
        print(f"Args: {args}")
        print(f"Kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"Result: {result}")
        return result
    return wrapper


class ChatService:
    def __init__(self):
        # Initialize database and embedding model
        self.database = Database(config.DB_URL)
        self.embedding_model = Embeddings(config.AWS_REGION, config.EMBEDDING_MODEL_ID)
        
        # Initialize the Bedrock model
        self.model = BedrockConverseModel(config.CHAT_MODEL_ID)
        
        # Model settings for parallel tool calls
        self.model_settings = ModelSettings(parallel_tool_calls=True)
        
        # System prompt
        self.system_prompt = """
You are a helpful assistant for Zus Coffee, a coffee chain. Your role is to answer customer questions *strictly* based on the tools and product data available to you.

You are responsible for assisting with:
- Product information about drinkwares sold by Zus Coffee (e.g. mugs, tumblers)
- Details about coffee outlet locations and their operational hours

You **do not** have access to information outside of the available product database and outlet information. If a question falls outside this scope, politely let the user know you cannot help.

When performing *any* numerical calculation (e.g. addition, multiplication), you must *always* call the appropriate tool. Do **not** do math in your head or inline in responses.

Use:
- `multiplication_calculator` for all multiplication (even simple values)
- `addition_calculator` for all addition

You are not allowed to perform arithmetic yourself. Think step-by-step, and *always* delegate calculations to the appropriate tool.

Use `get_products` and `get_similar_products` to retrieve product information about drinkwares.

Use `get_outlet` to get details about outlet branches and their operational hours.

Be clear, concise, and helpful. Always cite the information retrieved via tools when answering customer questions.
"""
        
        # Initialize the agent
        self.agent = Agent(
            name='zus_coffee_assistant',
            model=self.model,
            system_prompt=self.system_prompt,
            tools=[
                self.get_products,
                self.get_outlet,
                self.addition_calculator,
                self.multiplication_calculator,
                self.get_similar_products
            ],
        )
    
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
    
    async def chat(self, message: str, message_history: Optional[list] = None) -> tuple[str, list]:
        """
        Process a chat message and return the agent's response along with updated message history.
        
        Args:
            message: User's message
            message_history: Optional conversation history from previous messages
            
        Returns:
            tuple: (response_text, updated_message_history)
        """
        try:
            # Run the agent with message history
            result = await self.agent.run(
                message, 
                message_history=message_history,
                model_settings=self.model_settings
            )
            
            # Return response and updated message history
            return str(result.data), result.all_messages()
            
        except Exception as e:
            print(f"Error in chat service: {e}")
            raise Exception(f"Sorry, I encountered an error while processing your request: {str(e)}")
