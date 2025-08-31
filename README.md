# 📔 AI-Powered Journal Application

A full-stack web application that functions as a personal digital journal with AI-powered natural language search capabilities.

## Features

- 🔐 User authentication (register/login)
- 📝 Create, read, update, delete journal entries
- 🤖 AI-powered natural language search across entries
- 🔍 Vector similarity search using hash-based embeddings
- 📱 Responsive web design
- 🏗️ Groq AI integration for intelligent responses
- 🛡️ SSL bypass for corporate network environments

## Tech Stack

### Backend
- **Framework:** Flask (Python)
- **Database:** SQLite (development) / PostgreSQL-ready
- **AI/ML:** Groq API (Llama 3 models)
- **Authentication:** JWT tokens
- **ORM:** SQLAlchemy

### Frontend
- **Framework:** React with Vite
- **Routing:** React Router
- **State Management:** Zustand
- **HTTP Client:** Axios
- **Date Handling:** date-fns

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL with pgvector extension
- Google AI API key

## Setup Instructions

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Update the `.env` file with your configuration:
   ```env
   DATABASE_URL=postgresql://username:password@localhost/journal_db
   JWT_SECRET_KEY=your-very-secure-secret-key
   GOOGLE_AI_API_KEY=your-google-ai-api-key
   LLM_PROVIDER=gemini  # Options: gemini, openai, groq
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

6. Set up the database:
   ```bash
   # Create database
   createdb journal_db
   
   # Run migrations
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. Run the Flask application:
   ```bash
   python app.py
   ```

The backend will be available at `http://localhost:5000`

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Update the `.env` file if needed:
   ```env
   VITE_API_URL=http://localhost:5000/api
   ```

4. Run the React application:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## Usage

1. **Register/Login:** Create an account or sign in to an existing one
2. **Write Entries:** Use the journal entry form to create new entries
3. **AI Search:** Ask natural language questions about your entries:
   - "What did I write about work last week?"
   - "How was I feeling in March?"
   - "What activities did I do with friends?"
4. **Manage Entries:** Edit or delete existing entries

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Bcrypt hashed password
- `created_at`: Account creation timestamp

### Entries Table
- `id`: Primary key
- `content`: Journal entry text
- `created_at`: Entry creation timestamp
- `user_id`: Foreign key to users table
- `embedding`: Vector embedding for AI search (768 dimensions)

## LLM Provider Factory Pattern

The application uses a factory pattern to easily switch between different LLM providers:

```python
# Switch providers by changing the LLM_PROVIDER environment variable
LLM_PROVIDER=gemini    # Default: Google Gemini
LLM_PROVIDER=openai    # OpenAI GPT (requires implementation)
LLM_PROVIDER=groq      # Groq (requires implementation)
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile (protected)

### Journal Entries
- `GET /api/entries` - Get all user entries (protected)
- `POST /api/entries` - Create new entry (protected)
- `PUT /api/entries/<id>` - Update entry (protected)
- `DELETE /api/entries/<id>` - Delete entry (protected)

### AI Search
- `POST /api/search` - Search entries with natural language (protected)
- `GET /api/search/test` - Test AI service (protected)

## Deployment

### Backend (Render)
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `python app.py`
5. Add environment variables in the Render dashboard

### Frontend (Render)
1. Create a new Static Site on Render
2. Connect your GitHub repository
3. Set the build command: `cd frontend && npm install && npm run build`
4. Set the publish directory: `frontend/dist`

### Database (Supabase)
1. Create a new Supabase project
2. Enable the pgvector extension in the SQL editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Use the connection string in your backend environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
