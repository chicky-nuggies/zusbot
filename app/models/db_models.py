from sqlalchemy import Column, Integer, JSON, String
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    chunk = Column(JSON, nullable=False)
    embedding = Column(Vector(512), nullable=False)

class Outlet(Base):
    __tablename__ = "outlet"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    