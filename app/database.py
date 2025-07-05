from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import create_engine, Column, Integer, JSON, text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as SQLSession
from sqlalchemy.exc import SQLAlchemyError
from pgvector.sqlalchemy import Vector
import logging

from app.models.db_models import Product, Outlet, Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    """Database class for managing products with embeddings using PostgreSQL and pgvector."""
    
    def __init__(self, db_url: str):
        """
        Initialize the ProductDatabase.
        
        Args:
            db_url: PostgreSQL connection string
            vector_dimension: Dimension of the embedding vectors
        """
        self.db_url = db_url
        self.vector_dimension = 512
        
        # Initialize database
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

        self.base = Base


    def create_tables(self):
        """Create database tables and enable pgvector extension."""
        try:
            # Enable pgvector extension
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
            
            # Create tables
            self.base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
            
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            raise

            
    def search_similar_products(self, query_embedding: List[float], limit: int = 10, threshold: float = 0.5) -> List[Tuple[int, Dict[Any, Any], float]]:
        """
        Search for similar products using cosine similarity.
        
        Args:
            query_embedding: Pre-computed embedding vector for the query
            limit: Maximum number of results
            threshold: Minimum similarity threshold (0-1)
            
        Returns:
            List of tuples (product_id, chunk, similarity_score)
        """
        session = self.Session()
        try:
            # Validate embedding dimension
            if len(query_embedding) != self.vector_dimension:
                raise ValueError(f"Query embedding dimension {len(query_embedding)} does not match expected {self.vector_dimension}")
            
            # Search using cosine similarity
            results = session.query(
                Product.id,
                Product.chunk,
                (1 - Product.embedding.cosine_distance(query_embedding)).label('similarity')
            ).filter(
                (1 - Product.embedding.cosine_distance(query_embedding)) >= threshold
            ).order_by(
                Product.embedding.cosine_distance(query_embedding)
            ).limit(limit).all()
            
            return [(r.id, r.chunk, r.similarity) for r in results]
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            raise
        finally:
            session.close()
    
    def search_similar_products_l2(self, query_embedding: List[float], limit: int = 10, max_distance: float = 1.0) -> List[Tuple[int, Dict[Any, Any], float]]:
        """
        Search for similar products using L2 (Euclidean) distance.
        
        Args:
            query_embedding: Pre-computed embedding vector for the query
            limit: Maximum number of results
            max_distance: Maximum L2 distance threshold
            
        Returns:
            List of tuples (product_id, chunk, l2_distance)
        """
        session = self.Session()
        try:
            # Validate embedding dimension
            if len(query_embedding) != self.vector_dimension:
                raise ValueError(f"Query embedding dimension {len(query_embedding)} does not match expected {self.vector_dimension}")
            
            # Search using L2 distance
            results = session.query(
                Product.id,
                Product.chunk,
                Product.embedding.l2_distance(query_embedding).label('distance')
            ).filter(
                Product.embedding.l2_distance(query_embedding) <= max_distance
            ).order_by(
                Product.embedding.l2_distance(query_embedding)
            ).limit(limit).all()
            
            return [(r.id, r.chunk, r.distance) for r in results]
            
        except Exception as e:
            logger.error(f"Error searching products with L2 distance: {e}")
            raise
        finally:
            session.close()
                
    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            True if deleted successfully, False if product not found
        """
        session = self.Session()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                return False
            
            session.delete(product)
            session.commit()
            logger.info(f"Deleted product {product_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting product {product_id}: {e}")
            raise
        finally:
            session.close()
    
    def get_all_products(self, limit: int = 100, offset: int = 0) -> List[Tuple[int, Dict[Any, Any]]]:
        """
        Get all products with pagination.
        
        Args:
            limit: Maximum number of products to return
            offset: Number of products to skip
            
        Returns:
            List of tuples (product_id, chunk)
        """
        session = self.Session()
        try:
            results = session.query(Product.id, Product.chunk).limit(limit).offset(offset).all()
            return [(r.id, r.chunk) for r in results]
        except Exception as e:
            logger.error(f"Error getting all products: {e}")
            raise
        finally:
            session.close()
    
    def get_all_products_with_embeddings(self, limit: int = 100, offset: int = 0) -> List[Tuple[int, Dict[Any, Any], List[float]]]:
        """
        Get all products with their embeddings and pagination.
        
        Args:
            limit: Maximum number of products to return
            offset: Number of products to skip
            
        Returns:
            List of tuples (product_id, chunk, embedding)
        """
        session = self.Session()
        try:
            results = session.query(Product.id, Product.chunk, Product.embedding).limit(limit).offset(offset).all()
            return [(r.id, r.chunk, r.embedding) for r in results]
        except Exception as e:
            logger.error(f"Error getting all products with embeddings: {e}")
            raise
        finally:
            session.close()
        
    def bulk_add_products(self, products: List[Tuple[Dict[Any, Any], List[float]]]) -> List[int]:
        """
        Add multiple products in bulk.
        
        Args:
            products: List of tuples (chunk, embedding)
            
        Returns:
            List of product IDs
        """
        session = self.Session()
        try:
            product_objects = []
            
            for chunk, embedding in products:
                # Validate embedding dimension
                if len(embedding) != self.vector_dimension:
                    raise ValueError(f"Embedding dimension {len(embedding)} does not match expected {self.vector_dimension}")
                
                product = Product(
                    chunk=chunk,
                    embedding=embedding
                )
                product_objects.append(product)
            
            session.bulk_save_objects(product_objects, return_defaults=True)
            session.commit()
            
            product_ids = [p.id for p in product_objects]
            logger.info(f"Added {len(product_ids)} products in bulk")
            return product_ids
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error bulk adding products: {e}")
            raise
        finally:
            session.close()
        

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None, fetch: bool = True) -> Optional[List[Any]]:
        """
        Execute a custom SQL query.
        
        Args:
            query: SQL query string
            params: Optional dictionary of parameters for parameterized queries
            fetch: Whether to fetch and return results (True) or just execute (False)
            
        Returns:
            List of results if fetch=True, None if fetch=False
        """
        session = self.Session()
        try:
            if params:
                result = session.execute(text(query), params)
            else:
                result = session.execute(text(query))
            
            if fetch:
                # Fetch all results
                rows = result.fetchall()
                session.commit()
                logger.info(f"Executed query successfully, returned {len(rows)} rows")
                return rows
            else:
                # Just execute without fetching (for INSERT, UPDATE, DELETE, etc.)
                session.commit()
                logger.info("Query executed successfully")
                return None
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error executing query: {e}")
            raise
        finally:
            session.close()


    def close(self):
        """Close database connections."""
        self.engine.dispose()
        logger.info("Database connections closed")

# Usage example
if __name__ == "__main__":
    # Initialize database
    db = Database()
    
    # Example product data and embedding (normally you'd get embedding from your embedding service)
    product_data = {
        "name": "Laptop",
        "description": "High-performance laptop for gaming and work",
        "category": "Electronics",
        "price": 1299.99
    }
    
    # Mock embedding (in real usage, you'd get this from your embedding service)
    mock_embedding = [0.1] * 512
    
    # Add a product
    product_id = db.add_product(product_data, mock_embedding)
    print(f"Added product with ID: {product_id}")
    
    # Search for similar products (using the same mock embedding for demonstration)
    results = db.search_similar_products(mock_embedding, limit=5)
    print(f"Found {len(results)} similar products")
    
    # Get product count
    count = db.count_products()
    print(f"Total products: {count}")
    
    # Close database
    db.close()