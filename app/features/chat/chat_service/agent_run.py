from __future__ import annotations as _annotations

import functools
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.settings import ModelSettings

import sys
import os
# Add parent directory to path to import from root
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Database
from app.embedding import Embeddings
from app.config import config

from .agent_tools import AgentTools


class ChatAgent:
    def __init__(self, model_id):
        
        # Initialize the Bedrock model
        self.model = BedrockConverseModel(model_id)
        
        # Initialize database and embedding model
        self.database = Database(config.DB_URL)
        self.database.create_tables()  # Ensure tables exist
        self.embedding_model = Embeddings(config.AWS_REGION, config.EMBEDDING_MODEL_ID)
        
        # Initialize agent tools with database and embedding access
        self.tools = AgentTools(self.database, self.embedding_model)
        
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
                self.tools.get_products,
                self.tools.get_outlet,
                self.tools.addition_calculator,
                self.tools.multiplication_calculator,
                self.tools.get_similar_products
            ],
        )
    
    
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
                model_settings=ModelSettings(parallel_tool_calls=True)
            )
            
            # Return response and updated message history
            return str(result.data), result.all_messages()
            
        except Exception as e:
            print(f"Error in chat service: {e}")
            raise Exception(f"Sorry, I encountered an error while processing your request: {str(e)}")

    async def chat_stream(self, message: str, message_history: Optional[list] = None):
        """
        Stream chat response with tool call information.
        
        Args:
            message: User's message
            message_history: Optional conversation history from previous messages
            
        Yields:
            dict: Stream of information including tool calls and final response
        """
        try:
            # Clear previous tool call information
            self.tools.clear_tool_call_info()
            
            # Yield initial message
            yield {"type": "message_start", "message": message}
            
            # Run the agent with message history
            result = await self.agent.run(
                message, 
                message_history=message_history,
                model_settings=ModelSettings(parallel_tool_calls=True)
            )
            
            # Get tool call information
            tool_calls = self.tools.get_tool_call_info()
            
            # Yield tool call information
            for tool_call in tool_calls:
                yield {
                    "type": "tool_call",
                    "tool_name": tool_call["tool_call"]["tool_called"],
                    "args": tool_call["tool_call"]["args"],
                    "kwargs": tool_call["tool_call"]["kwargs"],
                    "result": tool_call["result"]["result"] if tool_call["result"] else None
                }
            
            # Yield final response
            yield {
                "type": "response",
                "response": str(result.data),
                "message_history": result.all_messages()
            }
            
        except Exception as e:
            print(f"Error in chat service: {e}")
            yield {
                "type": "error",
                "error": f"Sorry, I encountered an error while processing your request: {str(e)}"
            }
