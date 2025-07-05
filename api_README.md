# Zus Coffee Chatbot API

A FastAPI backend for the Zus Coffee customer service chatbot.

## Setup

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Copy `.env.example` to `.env` and modify as needed:

   ```bash
   copy .env.example .env
   ```

3. **AWS Configuration**
   Ensure your AWS CLI is configured with proper credentials for Bedrock access.

4. **Database**
   Make sure your PostgreSQL database is running and accessible.

## Running the API

### Option 1: Using the startup script

```bash
python run_api.py
```

### Option 2: Using uvicorn directly

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

- **GET /** - Welcome message with API info
- **GET /health** - Health check endpoint
- **POST /session/new** - Create a new chat session
- **POST /chat** - Chat with the assistant (supports multi-turn conversations)

### Session Management

The API supports multi-turn conversations within a session. Users can have ongoing conversations, but sessions are not persisted between server restarts.

#### Create New Session

**URL:** `POST /session/new`

**Response:**

```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "New chat session created"
}
```

### Chat Endpoint

**URL:** `POST /chat`

**Request Body (New Conversation):**

```json
{
  "message": "What coffee mugs do you have?"
}
```

**Request Body (Continue Conversation):**

```json
{
  "message": "Tell me more about the first one",
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response:**

```json
{
  "response": "Based on our product catalog...",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "success"
}
```

### Frontend Integration

For a typical frontend implementation:

1. **New User Visit**: Call `/chat` without `session_id` - API will create new session
2. **Continue Conversation**: Include the `session_id` from previous response in subsequent requests
3. **User Leaves/Returns**: Don't store `session_id` - let API create a new session

## API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## CORS Configuration

The API is configured to allow requests from:

- http://localhost:5173 (Vite default)
- http://localhost:3000 (React default)
- http://127.0.0.1:5173
- http://127.0.0.1:3000

## Architecture

- `api/main.py` - FastAPI application and routes
- `api/chat_service.py` - Chat logic and agent management
- `api/config.py` - Configuration and environment variables
- `run_api.py` - Startup script
