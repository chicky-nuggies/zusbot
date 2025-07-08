import functools
from typing import List, Dict, Any
import asyncio
import json

import sys
import os
# Add parent directory to path to import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import Database
from app.embedding import Embeddings
from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel
from app.config import config


# Text-to-SQL agent configuration
text_to_sql_prompt = """
You are a highly experienced SQL analyst. Your job is to translate natural language questions into safe, read-only SQL queries using the following database schema.

Database Schema:

Table: outlet

id (Integer, Primary Key): A unique identifier for each outlet.

name (String, max 255 chars): The name of the outlet.

address (String, max 500 chars): The physical address of the outlet.

Safety Rules — Must Follow:
Only generate SELECT queries.
Do not generate any queries that modify data, such as INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE.

No nested queries that modify the database, even within WITH clauses or subqueries.

Never use functions that write logs or perform server-side actions (e.g., pg_sleep, pg_notify, xp_cmdshell, etc.).

Do not use JOINs unless additional tables are added explicitly in the schema.

Only reference columns that exist in the schema.

Do not hallucinate tables or columns. Stick exactly to what is provided.

All user queries should be assumed to be case-insensitive unless specified.

If a user query is ambiguous, make a reasonable assumption and generate the most likely intended read-only query. Prefer clarity and specificity.

Do not add comments or explanations unless explicitly requested.

Output Format:
Always return only the raw SQL query.

No natural language explanations or summaries.

If the question cannot be answered safely with the given schema, return:
-- Cannot generate a safe query for this request.

Examples:
User: "Show me all outlets"
SQL: SELECT * FROM outlet;

User: "What's the address of the outlet named 'Blue Bean'?"
SQL: SELECT address FROM outlet WHERE name = 'Blue Bean';

User: "List outlet names in alphabetical order."
SQL: SELECT name FROM outlet ORDER BY name;

User: "Give me the full record of the outlet with ID 12."
SQL: SELECT * FROM outlet WHERE id = 12;

User: "Delete all outlets."
SQL: -- Cannot generate a safe query for this request.
"""


def log_tool_call(func):
    """Decorator to log tool calls for debugging and collect metadata"""
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            tool_name = func.__name__
            print(f"Tool called: {tool_name}")
            print(f"Args: {args}")
            print(f"Kwargs: {kwargs}")
            
            result = await func(self, *args, **kwargs)
            print(f"Result: {result}")
            
            # Collect metadata about this tool call
            tool_metadata = {
                "tool_name": tool_name,
                "tool_kwargs": kwargs,
                "tool_args": args,
                "result": result
            }
            
            # Store metadata in the instance
            if not hasattr(self, 'tool_calls_metadata'):
                self.tool_calls_metadata = []
            self.tool_calls_metadata.append(tool_metadata)
            
            return result
        return async_wrapper
    else:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            tool_name = func.__name__
            print(f"Tool called: {tool_name}")
            print(f"Args: {args}")
            print(f"Kwargs: {kwargs}")
            
            result = func(self, *args, **kwargs)
            print(f"Result: {result}")
            
            # Collect metadata about this tool call
            tool_metadata = {
                "tool_name": tool_name,
                "tool_kwargs": kwargs,
                "tool_args": args,
                "result": result
            }
            
            # Store metadata in the instance
            if not hasattr(self, 'tool_calls_metadata'):
                self.tool_calls_metadata = []
            self.tool_calls_metadata.append(tool_metadata)
            
            return result
        return wrapper


class AgentTools:
    """Class containing all agent tools with access to database and embedding model"""
    
    def __init__(self, database: Database, embedding_model: Embeddings):
        self.database = database
        self.embedding_model = embedding_model
        self.tool_calls_metadata = []  # Store metadata about tool calls
        
        # Initialize the text-to-SQL agent
        self.model = BedrockConverseModel(config.CHAT_MODEL_ID)
        self.text_to_sql_agent = Agent(
            name='text_to_sql_agent',
            model=self.model,
            system_prompt=text_to_sql_prompt
        )
    
    def get_and_clear_tool_metadata(self) -> List[Dict[str, Any]]:
        """Get all tool call metadata and clear the list"""
        metadata = self.tool_calls_metadata.copy()
        self.tool_calls_metadata.clear()
        return metadata
    
    @log_tool_call
    def get_products(self):
        """Gets information about products"""
        return self.database.get_all_products()

    @log_tool_call
    def get_similar_products(self, search_query: str):
        """Performs a semantic similarity search over Zus Coffee's drinkware catalog"""
        query_embedding = self.embedding_model.generate_embeddings(search_query)
        return self.database.search_similar_products(query_embedding, threshold=0.4)

    @log_tool_call
    def addition_calculator(self, numbers: list[int]):
        """Sums up numbers"""
        return sum(numbers)

    @log_tool_call
    def multiplication_calculator(self, num: int, multiplier: int):
        """Multiplies numbers"""
        return num * multiplier

    async def query_outlets_table(self, nl_query: str):
        """Takes Natural Language and performs SQL on a database to query outlet information"""
        try:
            # Generate SQL query using the text-to-SQL agent
            result = await self.text_to_sql_agent.run(nl_query)
            sql_query = result.data
            print(f'Generated SQL query: {sql_query}')
            
            # Check if the query is safe (should start with SELECT and not be an error)
            if sql_query.strip().startswith('--'):
                query_result = "Cannot generate a safe query for this request."
                generated_sql = sql_query
            else:
                # Execute the query on the database
                rows = self.database.execute_query(sql_query)
                
                # Convert results to JSON format
                query_result = json.dumps([dict(row._mapping) for row in rows], indent=2)
                generated_sql = sql_query
            
            # Collect metadata about this tool call with SQL query included
            tool_metadata = {
                "tool_name": "query_outlets_table",
                "tool_kwargs": {"nl_query": nl_query},
                "tool_args": (),
                "result": query_result,
                "generated_sql": generated_sql
            }
            
            # Store metadata in the instance
            if not hasattr(self, 'tool_calls_metadata'):
                self.tool_calls_metadata = []
            self.tool_calls_metadata.append(tool_metadata)
            
            return query_result
            
        except Exception as e:
            error_msg = f"Error executing query: {str(e)}"
            print(f"Error in query_outlets_table: {e}")
            
            # Collect metadata for error case too
            tool_metadata = {
                "tool_name": "query_outlets_table",
                "tool_kwargs": {"nl_query": nl_query},
                "tool_args": (),
                "result": error_msg,
                "generated_sql": None
            }
            
            # Store metadata in the instance
            if not hasattr(self, 'tool_calls_metadata'):
                self.tool_calls_metadata = []
            self.tool_calls_metadata.append(tool_metadata)
            
            return error_msg
