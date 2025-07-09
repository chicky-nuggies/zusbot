# Zus Coffee Chatbot API

A FastAPI backend for the Zus Coffee customer service chatbot powered by AWS Bedrock (Claude 3.5 Sonnet) with intelligent tool integration for product search and outlet queries.

## Features

- 🤖 **AI-Powered Chat**: Uses Claude 3.5 Sonnet via AWS Bedrock for intelligent responses
- 🔍 **Product Search**: Vector-based semantic search for Zus Coffee drinkware products
- 📍 **Outlet Queries**: Natural language to SQL conversion for outlet location searches
- 💬 **Session Management**: Multi-turn conversation support with session persistence
- 🛠️ **Tool Integration**: Specialized agents for different query types (general chat, products, outlets)
- 🗄️ **Vector Database**: PostgreSQL with pgvector for efficient similarity search
- 🐳 **Docker Support**: Containerized deployment ready
- 🔒 **CORS Configuration**: Frontend-ready with proper CORS settings

## Tech Stack

- **Backend**: FastAPI with async/await support
- **AI Model**: AWS Bedrock (Claude 3.5 Sonnet, Titan Embeddings)
- **Database**: PostgreSQL with pgvector extension
- **Vector Search**: Amazon Titan Embed Text v2 for embeddings
- **Session Management**: In-memory session storage with cleanup
- **Containerization**: Docker with health checks

## Setup

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Configure the following environment variables:

   ```bash
   # Database
   DB_URL=postgresql+psycopg2://username:password@host:port/database

   # AWS Configuration
   AWS_REGION=ap-southeast-5
   BEDROCK_REGION=us-east-1

   # AI Models
   EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
   CHAT_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0

   # API Configuration
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

3. **AWS Configuration**
   Ensure your AWS CLI is configured with proper credentials for Bedrock access.

4. **Database Setup**
   - PostgreSQL with pgvector extension
   - Tables are auto-created on startup
   - Run ingestion scripts to populate data:
     ```bash
     python "ingestion scripts/ingest_products.py"
     python "ingestion scripts/ingest_outlets.py"
     ```

## Running the API

### Option 1: Using the startup script

```bash
python run_api.py
```

### Option 2: Using uvicorn directly

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using Docker

```bash
docker build -t zus-coffee-api .
docker run -p 8000:8000 zus-coffee-api
```

## API Endpoints

- **GET /health** - Health check endpoint
- **POST /api/chat** - Main chat endpoint with multi-turn conversation support
- **GET /api/products** - Product search with AI-powered summaries
- **GET /api/outlets** - Natural language outlet queries

### Main Chat Endpoint

**URL:** `POST /api/chat`

**Description:** Main conversational endpoint that handles general queries, automatically routing to appropriate tools for product or outlet information.

**Request Body (New Conversation):**

```json
{
  "message": "What coffee mugs do you have available?"
}
```

**Request Body (Continue Conversation):**

```json
{
  "message": "Tell me more about the blue ones",
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response:**

```json
{
  "response": "Based on our product catalog, I found several coffee mugs in blue colors...",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "success",
  "tool_calls": [
    {
      "tool_name": "get_similar_products",
      "tool_kwargs": {"query": "blue coffee mugs", "top_k": 5},
      "tool_args": [],
      "result": [...],
      "generated_sql": null
    }
  ]
}
```

### Products Endpoint

**URL:** `GET /api/products?query=your_query`

**Description:** Specialized endpoint for product searches with detailed retrieval information.

**Query Parameters:**

- `query` (required): Natural language product query

**Response:**

```json
{
  "query": "coffee tumblers",
  "summary": "AI-generated summary of relevant products...",
  "retrieved_products": [
    {
      "id": "product_1",
      "content": "Product details...",
      "similarity_score": 0.85
    }
  ],
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "success",
  "tool_calls": [...]
}
```

### Outlets Endpoint

**URL:** `GET /api/outlets?query=your_query`

**Description:** Natural language queries about outlet locations, translated to SQL queries.

**Query Parameters:**

- `query` (required): Natural language outlet query (e.g., "outlets in Kuala Lumpur")

**Response:**

```json
{
  "query": "outlets in Kuala Lumpur",
  "response": "I found 15 outlets in Kuala Lumpur...",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "success",
  "tool_calls": [
    {
      "tool_name": "text_to_sql_query",
      "tool_kwargs": {...},
      "tool_args": [...],
      "generated_sql": "SELECT * FROM outlet WHERE address LIKE '%Kuala Lumpur%'",
      "result": [...]
    }
  ]
}
```

## Architecture

The application follows a modular architecture with the following key components:

### Core Components

- `app/main.py` - FastAPI application setup and main router configuration
- `app/config.py` - Configuration management with environment variables
- `app/database.py` - Database connection and operations (PostgreSQL + pgvector)
- `app/embedding.py` - AWS Bedrock embedding model integration
- `app/dependencies.py` - Dependency injection for services

### Features

- `app/features/chat/router.py` - API endpoints for chat, products, and outlets
- `app/features/chat/chat_service/agent_run.py` - Main chat agent with Claude 3.5 Sonnet
- `app/features/chat/chat_service/agent_tools.py` - Tool implementations for AI agent
- `app/features/sessions/session_manager.py` - Session management and cleanup

### Models

- `app/models/db_models.py` - Database models (Product, Outlet)
- `app/models/endpoint_models.py` - API request/response models

### Data Management

- `data/zus_coffee_products.json` - Product catalog (259 drinkware items)
- `data/zus_coffee_outlets.csv` - Outlet locations (259 locations)
- `ingestion scripts/` - Data ingestion utilities

## Agent Tools

The AI agent has access to specialized tools:

1. **get_similar_products**: Vector similarity search for product queries
2. **text_to_sql_query**: Natural language to SQL conversion for outlet queries
3. **Session Management**: Automatic session creation and conversation history

## Data

### Products

- 259 Zus Coffee drinkware products
- Categories: Cups, Tumblers, Mugs, Collections (Aqua, Mountain, etc.)
- Attributes: Name, price, colors, descriptions, specifications
- Vector embeddings for semantic search

### Outlets

- 259 Zus Coffee outlet locations
- Data: ID, name, full address
- Supports location-based queries via SQL

## Session Management

The API supports multi-turn conversations within sessions:

- **Automatic Session Creation**: New session created if none provided
- **Session Persistence**: Conversation history maintained during session
- **Session Cleanup**: Automatic cleanup of old inactive sessions
- **Session Expiry**: Sessions expire after inactivity period

### Frontend Integration

For frontend implementations:

1. **New User**: Call `/api/chat` without `session_id` - API creates new session
2. **Continue Conversation**: Include `session_id` from previous response
3. **Session Management**: Sessions are automatically managed - no manual creation needed

## Development

### API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### CORS Configuration

The API is configured to allow requests from:

- http://localhost:5173 (Vite default)
- http://localhost:3000 (React default)
- http://127.0.0.1:5173
- http://127.0.0.1:3000
- https://zus.weishen.studio (Production frontend)

### Environment Configuration

The app uses different AWS regions for infrastructure and Bedrock:

- **Main Infrastructure**: ap-southeast-5 (Jakarta)
- **Bedrock Services**: us-east-1 (N. Virginia) - for model availability

### Database Schema

**Products Table:**

- `id` (Primary Key)
- `data` (JSON) - Product information
- `embedding` (Vector[512]) - Semantic search embeddings

**Outlets Table:**

- `id` (Primary Key)
- `name` (String) - Outlet name
- `address` (String) - Full address

## Deployment

### Docker Deployment

The application includes a production-ready Dockerfile with:

- Python 3.12 slim base image
- Non-root user for security
- Health checks
- Optimized layer caching

Build and run:

```bash
docker build -t zus-coffee-api .
docker run -p 8000:8000 \
  -e DB_URL="your_db_url" \
  -e AWS_REGION="ap-southeast-5" \
  -e BEDROCK_REGION="us-east-1" \
  zus-coffee-api
```

### AWS ECR Push

Use the included batch script for ECR deployment:

```bash
pushtoecr.bat
```

## Contributing

1. Follow the modular architecture patterns
2. Add new tools to `agent_tools.py` for extending AI capabilities
3. Update endpoint models when adding new API features
4. Ensure proper error handling and logging
5. Test with both product and outlet queries

## License

Private project for Zus Coffee chatbot implementation.
