# ============================================
# Configuration Settings
# ============================================
# This file loads environment variables and provides
# configuration values to other parts of the application.

import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# --------------------------------------------
# Groq LLM Configuration
# --------------------------------------------
# Groq is a fast, free LLM API service
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"  # Fast and capable model


# --------------------------------------------
# MySQL Database Configuration
# --------------------------------------------
# MySQL stores our support tickets
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "customer_support")

# SQLAlchemy connection string
# Format: mysql+pymysql://user:password@host:port/database
# We use quote_plus to encode special characters in password (like @, #, etc.)
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"


# --------------------------------------------
# Qdrant Vector Database Configuration
# --------------------------------------------
# Qdrant stores document embeddings for semantic search
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)  # Optional for Qdrant Cloud
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "support_docs")


# --------------------------------------------
# Embedding Model Configuration
# --------------------------------------------
# This model converts text to vectors (numbers)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # Size of vectors this model produces


# --------------------------------------------
# Document Processing Configuration
# --------------------------------------------
# Where PDF documents are stored
DOCS_DIRECTORY = "data/docs"

# Chunk size for splitting documents
# Smaller chunks = more precise search, but less context
CHUNK_SIZE = 500  # characters per chunk
CHUNK_OVERLAP = 50  # overlap between chunks to maintain context


# --------------------------------------------
# RAG Configuration
# --------------------------------------------
# How many document chunks to retrieve for each query
TOP_K_RESULTS = 3
