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

## AI Search Functionality

The application features a sophisticated AI-powered search system that allows you to find journal entries using natural language queries.

### 🧠 How AI Search Works

```mermaid
graph TD
    A[User Query: "What did I write on 9th Aug 2025?"] --> B[Frontend SearchBar]
    B --> C[POST /api/ai/search]
    C --> D{Generate Query Embedding}
    
    D -->|Success| E[Vector Similarity Search]
    D -->|Fail| F[Date-Based Search Fallback]
    
    E --> G[DatabaseService.find_similar_entries]
    F --> H[DatabaseService.find_entries_by_date_query]
    
    G --> I{Found Entries?}
    H --> I
    
    I -->|No| J[Return "No entries found"]
    I -->|Yes| K[Prepare Context with Entry Dates]
    
    K --> L[Generate AI Prompt with Context]
    L --> M[Groq API: llama-3.1-8b-instant]
    M --> N[AI Generated Response]
    N --> O[Return Response to Frontend]
    
    subgraph "Database Layer"
        P[Entry Table]
        P --> Q[entry_date: 2025-08-09]
        P --> R[content: "Today I worked on..."]
        P --> S[embedding: [0.1, 0.3, -0.2, ...]]
    end
    
    G --> P
    H --> P
```

### 🔍 Search Strategy Flow

```mermaid
flowchart LR
    A[User Query] --> B{Contains Date Pattern?}
    
    B -->|Yes| C[Extract Dates:<br/>• "9th aug 2025"<br/>• "august 9, 2025"<br/>• "2025-08-09"<br/>• "8/9/2025"]
    B -->|No| D[Generate Embedding<br/>Vector: [768 dimensions]]
    
    C --> E[Query by entry_date]
    D --> F[Cosine Similarity Search]
    
    E --> G{Entries Found?}
    F --> G
    
    G -->|Yes| H[Build Context for AI]
    G -->|No| I[Search by created_at date]
    
    I --> J{Entries Found?}
    J -->|Yes| H
    J -->|No| K[Return "No entries found"]
    
    H --> L[AI Response Generation]
```

### 📊 Vector Embedding Process

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant G as Groq API
    participant D as Database
    
    Note over U,D: Entry Creation with Embedding
    U->>F: Submit journal entry
    F->>B: POST /api/entries {content, entry_date}
    B->>G: Generate embedding for content
    G-->>B: Vector [768 dimensions]
    B->>D: Store entry + embedding
    D-->>B: Entry saved
    B-->>F: Success response
    
    Note over U,D: AI Search Process
    U->>F: Search query: "9th aug 2025"
    F->>B: POST /api/ai/search {query}
    B->>G: Generate query embedding
    G-->>B: Query vector [768 dimensions]
    B->>D: Cosine similarity search
    D-->>B: Relevant entries
    
    alt Entries found via embedding
        B->>G: Generate response with context
        G-->>B: AI response
    else No embedding matches
        B->>D: Date-based search fallback
        D-->>B: Date-matched entries
        B->>G: Generate response with context
        G-->>B: AI response
    end
    
    B-->>F: Search results + AI response
    F-->>U: Display results
```

### 🎯 Search Features

#### **1. Vector Similarity Search**
- Converts your query into a 768-dimensional vector
- Finds entries with similar semantic meaning
- Uses cosine similarity for relevance scoring

#### **2. Date-Based Search Fallback**
- Parses various date formats from queries:
  - Natural: "9th august 2025", "august 9th 2025"
  - ISO: "2025-08-09"
  - US Format: "8/9/2025"
  - Other: "9-8-2025"
- Searches both `entry_date` and `created_at` fields

#### **3. Smart Context Building**
- Includes relevant entry dates in AI context
- Formats dates in IST for user familiarity
- Limits context to prevent token overflow

#### **4. Robust Error Handling**
- Graceful fallbacks when AI services fail
- Hash-based embeddings when Groq is unavailable
- Date parsing with multiple format support

### 🕐 Time Zone Handling

All timestamps are converted to **Indian Standard Time (IST, UTC+5:30)**:

```python
# Backend conversion
ist = timezone(timedelta(hours=5, minutes=30))
created_at_ist = utc_time.astimezone(ist)

# Frontend display
"Updated: 2025-08-09 02:30:45 PM IST"
```

### 🏗️ Technical Architecture

```mermaid
graph TB
    subgraph "Frontend (React + Vite)"
        A[SearchBar Component]
        B[JournalEntryForm]
        C[JournalEntriesList]
        D[Zustand Store]
        E[API Service Layer]
    end
    
    subgraph "Backend (Flask)"
        F[Auth Routes]
        G[Entry Routes]
        H[AI Routes]
        I[LLM Service Factory]
        J[Database Service]
    end
    
    subgraph "AI Services"
        K[Groq API<br/>llama-3.1-8b-instant]
        L[Embedding Generation<br/>Hash-based fallback]
    end
    
    subgraph "Database (SQLite)"
        M[Users Table]
        N[Entries Table<br/>+ Vector Embeddings]
    end
    
    A --> E
    B --> E
    C --> E
    E --> H
    E --> G
    G --> J
    H --> I
    I --> K
    I --> L
    J --> N
    F --> M
    G --> N
    
    style K fill:#e1f5fe
    style L fill:#f3e5f5
    style N fill:#e8f5e8
```

## Usage

1. **Register/Login:** Create an account or sign in to an existing one
2. **Write Entries:** Use the journal entry form to create new entries
3. **AI Search:** Ask natural language questions about your entries:
   - "What did I write about work last week?"
   - "How was I feeling in March?"
   - "What activities did I do with friends?"
4. **Manage Entries:** Edit or delete existing entries

## Troubleshooting AI Search

### Common Issues and Solutions

#### 🔍 "No entries found" for specific dates
```bash
# Check if entries exist with debug endpoint
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:5000/api/entries/debug

# Check AI search debug
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:5000/api/ai/debug/entries
```

#### 🤖 AI service unavailable
- **Groq Model Issues**: Check if `llama-3.1-8b-instant` is still supported
- **API Key**: Verify `GROQ_API_KEY` in `.env` file
- **Fallback Mode**: App continues with hash-based embeddings when AI fails

#### 📅 Date Search Not Working
Supported date formats in queries:
- Natural: "9th august 2025", "august 9th 2025"
- ISO: "2025-08-09"
- US: "8/9/2025"
- Alternative: "9-8-2025"

#### 🔧 Debug Commands
```python
# Test AI service
GET /api/ai/search/test

# View all entries with dates
GET /api/entries/debug

# Manual date search test
POST /api/ai/search
{
  "query": "2025-08-09"
}
```

### 💡 Example Search Queries

#### Date-Specific Searches
```
"What did I write on 9th aug 2025?"
"Show me my entry for august 9, 2025"
"What happened on 2025-08-09?"
```

#### Semantic Searches
```
"How was I feeling last week?"
"What work projects did I mention?"
"When did I write about traveling?"
"What activities did I do with friends?"
```

#### Response Format
```json
{
  "response": "On August 9th, 2025, you wrote about working on the journal app project...",
  "relevant_entries_count": 1,
  "ai_available": true
}
```

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Bcrypt hashed password
- `created_at`: Account creation timestamp

### Entries Table
- `id`: Primary key
- `content`: Journal entry text content
- `entry_date`: Date for the journal entry (user-selected, defaults to today)
- `created_at`: System timestamp when entry was created
- `updated_at`: System timestamp when entry was last modified
- `user_id`: Foreign key to users table
- `embedding_json`: Vector embedding for AI search (768 dimensions, stored as JSON)

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
- `GET /api/entries` - Get all user entries sorted by entry_date, updated_at (protected)
- `POST /api/entries` - Create new entry with entry_date and embedding (protected)
- `PUT /api/entries/<id>` - Update entry content and/or entry_date (protected)
- `DELETE /api/entries/<id>` - Delete entry (protected)
- `GET /api/entries/debug` - Debug view of all entries with IST times (protected)

### AI Search
- `POST /api/ai/search` - Search entries with natural language (protected)
  ```json
  {
    "query": "What did I write on 9th aug 2025?"
  }
  ```
- `GET /api/ai/search/test` - Test AI service connectivity (protected)
- `GET /api/ai/debug/entries` - Debug AI search with entry analysis (protected)

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
