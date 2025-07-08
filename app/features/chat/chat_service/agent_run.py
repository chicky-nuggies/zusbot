from __future__ import annotations as _annotations

import functools
import json
from typing import Optional, AsyncGenerator, Dict, Any

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
- Database queries about outlet information using natural language

You **do not** have access to information outside of the available product database and outlet information. If a question falls outside this scope, politely let the user know you cannot help.

When performing *any* numerical calculation (e.g. addition, multiplication), you must *always* call the appropriate tool. Do **not** do math in your head or inline in responses.

Use:
- `multiplication_calculator` for all multiplication (even simple values)
- `addition_calculator` for all addition
- `query_outlets_table` for complex queries about outlet data using natural language

You are not allowed to perform arithmetic yourself. Think step-by-step, and *always* delegate calculations to the appropriate tool.

Use `get_products` and `get_similar_products` to retrieve product information about drinkwares.

Use `get_outlet` to get basic details about outlet branches and their operational hours.

Use `query_outlets_table` for more complex queries about outlet information, such as:
- Finding outlets by name or address
- Listing all outlets
- Searching for outlets in specific locations
- Any other database queries about outlet data

Be clear, concise, and helpful. Always cite the information retrieved via tools when answering customer questions.
"""
        
        # Initialize the agent
        self.agent = Agent(
            name='zus_coffee_assistant',
            model=self.model,
            model_settings=ModelSettings(parallel_tool_calls=True),
            system_prompt=self.system_prompt,
            tools=[
                self.tools.addition_calculator,
                self.tools.multiplication_calculator,
                self.tools.get_products,
                self.tools.get_similar_products,
                self.tools.query_outlets_table
            ],
        )
        
        # Create a separate agent for product summarization
        self.product_summary_agent = Agent(
            name='product_summary_agent',
            model=self.model,
            model_settings=ModelSettings(parallel_tool_calls=True),
            system_prompt="""
You are a product information specialist for Zus Coffee. Your role is to help customers find and understand product information about drinkwares sold by Zus Coffee.

IMPORTANT: You must ALWAYS use the `get_similar_products` tool first before providing any product information. You do not have any built-in knowledge about Zus Coffee products.

Your workflow:
1. FIRST: Always call `get_similar_products` with the user's query to search for relevant products
2. THEN: Analyze the results from the tool call
3. FINALLY: Provide a helpful summary based on the retrieved product data

Your responsibilities:
- Use the `get_similar_products` tool to search for relevant products based on user queries
- Analyze and summarize product information from the search results
- Create clear, informative summaries that highlight key features
- Focus on relevant details like product names, prices, descriptions, materials, and specifications
- Present information in a customer-friendly manner
- Be concise but comprehensive in your summaries

NEVER say you don't have information about products. Instead, ALWAYS use the `get_similar_products` tool first to search for relevant products, then provide a summary based on what the tool returns.

If the tool returns no results, then you can say no relevant products were found for the query.

Be helpful and informative, focusing on answering the user's specific question about Zus Coffee drinkware products.
""",
            tools=[
                self.tools.get_similar_products,
            ],
        )
    
    
    async def chat(self, message: str, message_history: Optional[list] = None) -> tuple[str, list, list]:
        """
        Process a chat message and return the agent's response along with updated message history and tool metadata.
        
        Args:
            message: User's message
            message_history: Optional conversation history from previous messages
            
        Returns:
            tuple: (response_text, updated_message_history, tool_calls_metadata)
        """
        try:
            # Clear any previous tool metadata
            self.tools.tool_calls_metadata.clear()
            
            # Run the agent with message history
            result = await self.agent.run(
                message, 
                message_history=message_history,
            )
            
            # Get tool metadata
            tool_metadata = self.tools.get_and_clear_tool_metadata()
            
            # Return response, updated message history, and tool metadata
            return str(result.data), result.all_messages(), tool_metadata
            
        except Exception as e:
            print(f"Error in chat service: {e}")
            raise Exception(f"Sorry, I encountered an error while processing your request: {str(e)}")
        

    async def chat_stream(self, message: str, message_history: Optional[list] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a chat message and return the agent's response along with updated message history and tool metadata.
        
        Args:
            message: User's message
            message_history: Optional conversation history from previous messages
            
        Returns:
            AsyncGenerator yielding chunks and final response with tool metadata
        """
        try:
            print(f"[AGENT_STREAM] Starting chat_stream with message: '{message[:50]}...' and history length: {len(message_history) if message_history else 0}")
            
            # Clear any previous tool metadata
            self.tools.tool_calls_metadata.clear()
            
            async with self.agent.run_stream(
                message, 
                message_history=message_history, 
            ) as response:
                full_response = ""
                async for chunk in response.stream_text(delta=True):
                    # Yield each chunk
                    yield {'chunk': chunk}
                    full_response += chunk
                
            final_messages = response.all_messages()
            
            # Get tool metadata
            tool_metadata = self.tools.get_and_clear_tool_metadata()
            
            print(f"[AGENT_STREAM] Stream complete. Full response length: {len(full_response)}, final history length: {len(final_messages)}, tool calls: {len(tool_metadata)}")
            
            yield {
                'response': full_response,
                'message_history': final_messages,
                'tool_calls': tool_metadata
            }

            
        except Exception as e:
            print(f"Error in chat service: {e}")
            raise Exception(f"Sorry, I encountered an error while processing your request: {str(e)}")
    
    async def product_chat(self, message: str, message_history: Optional[list] = None) -> tuple[str, list, list]:
        """
        Process a product-related chat message using the dedicated product summary agent.
        
        Args:
            message: User's message about products
            message_history: Optional conversation history from previous messages
            
        Returns:
            tuple: (response_text, updated_message_history, tool_calls_metadata)
        """
        try:
            # Clear any previous tool metadata
            self.tools.tool_calls_metadata.clear()
            
            # Run the product summary agent with message history
            result = await self.product_summary_agent.run(
                message, 
                message_history=message_history,
            )
            
            # Get tool metadata
            tool_metadata = self.tools.get_and_clear_tool_metadata()
            
            # Return response, updated message history, and tool metadata
            return str(result.data), result.all_messages(), tool_metadata
            
        except Exception as e:
            print(f"Error in product chat service: {e}")
            raise Exception(f"Sorry, I encountered an error while processing your product request: {str(e)}")
