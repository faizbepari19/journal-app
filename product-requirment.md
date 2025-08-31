# AI-Powered Journal Application Specification

## 1. Project Overview 📝

This project is a full-stack web application that functions as a personal digital journal. Users can create, read, update, and delete daily entries. The standout feature is an AI-powered natural language search that allows users to ask questions about their past entries and receive summarized, human-like answers.

Make sure to use best practices and use factory design pattern for the LLM api integration. I should be able to easily toggle between gemini/openai/groq.

**Tech Stack:**
- **Frontend:** React (using Vite)
- **Backend:** Python with Flask
- **Database:** PostgreSQL with the `pgvector` extension (hosted on Supabase)
- **AI/NLP:** Google AI API (Gemini and Embedding models)

---

## 2. Core Features & Requirements

### 2.1. Backend (Flask API)

#### **a. Project Setup & Configuration**
- Initialize a Flask project with a `requirements.txt` file.
- Required libraries: `Flask`, `Flask-SQLAlchemy`, `Flask-Migrate`, `Flask-Bcrypt`, `Flask-JWT-Extended`, `python-dotenv`, `psycopg2-binary`, `google-generativeai`, `Flask-Cors`.
- Set up environment variables (`.env`) for database URL, JWT secret key, and Google AI API key.
- Configure SQLAlchemy to connect to the PostgreSQL database.
- Implement Flask-Migrate for database schema management.
- Configure CORS to allow requests from the React frontend.

#### **b. Database Models (`models.py`)**
- **User Model:**
    - `id` (Integer, Primary Key)
    - `username` (String, Unique, Not Nullable)
    - `email` (String, Unique, Not Nullable)
    - `password_hash` (String, Not Nullable)
- **Entry Model:**
    - `id` (Integer, Primary Key)
    - `content` (Text, Not Nullable)
    - `created_at` (DateTime, Default to current time)
    - `user_id` (Integer, Foreign Key to `User.id`)
    - `embedding` (Vector, using `pgvector` type) - This will store the text embedding.

#### **c. Authentication API Endpoints (`auth_routes.py`)**
- `POST /api/auth/register`: Takes `username`, `email`, `password`. Hashes the password using Bcrypt. Creates a new user. Returns a success message.
- `POST /api/auth/login`: Takes `email`, `password`. Verifies credentials. Returns a JWT access token upon success.
- `GET /api/auth/profile`: A protected route that requires a valid JWT. Returns the current logged-in user's information (`id`, `username`, `email`).

#### **d. Journal Entry API Endpoints (`entry_routes.py`)**
- All routes must be protected and require a valid JWT.
- `POST /api/entries`:
    - Takes `content` and `date` in the request body.
    - Generates a text embedding for the `content` using the Google AI Embedding API.
    - Saves the new entry, including its `content`, `date`, `user_id`, and the generated `embedding`, to the database.
    - Returns the newly created entry object.
- `GET /api/entries`:
    - Fetches all journal entries for the currently logged-in user, sorted by date.
    - Returns a list of entry objects.
- `PUT /api/entries/<entry_id>`:
    - Takes `content` and `date` in the request body to update an existing entry.
    - Regenerates the embedding for the new content.
    - Updates the entry in the database.
    - Returns the updated entry object.
- `DELETE /api/entries/<entry_id>`:
    - Deletes a specific entry by its ID.
    - Returns a success message.

#### **e. AI Search API Endpoint (`ai_routes.py`)**
- `POST /api/search`:
    1.  This is a protected route.
    2.  Takes a natural language `query` from the user (e.g., "What did I discuss with Alex last month?").
    3.  Generate an embedding for the user's `query` using the Google AI Embedding API.
    4.  Perform a vector similarity search in the `Entry` table's `embedding` column to find the top 5-10 most relevant journal entries for the logged-in user.
    5.  Construct a prompt for the Gemini LLM. The prompt should include the user's original query and the content of the relevant entries found in the previous step.
        - **Prompt Template:** `Based on the following journal entries: [CONTEXT_ENTRIES], please answer the user's question: [USER_QUERY]. Provide a concise, summary-style answer.`
    6.  Send the prompt to the Gemini API.
    7.  Return the generated text response from the LLM as a JSON object.

---

### 2.2. Frontend (React)

#### **a. Project Setup**
- Initialize a React project using Vite.
- Install necessary libraries: `axios` for API requests, `react-router-dom` for routing, `date-fns` for date formatting, and a state management library like `zustand` or `react-query`.
- Set up a base `axios` instance with the API base URL.

#### **b. Components & Pages**
- **Authentication Pages:**
    - `LoginPage`: Form with email and password fields. Handles login API calls and stores the JWT in local storage.
    - `RegisterPage`: Form for username, email, and password. Handles registration.
- **Routing (`App.js`)**
    - Implement public routes (`/login`, `/register`) and private/protected routes.
    - Protected routes should only be accessible if a valid JWT is present. If not, redirect to the login page.
- **Journal Components:**
    - `DashboardPage`: The main page after login.
        - Displays the AI search bar prominently at the top.
        - Contains a `JournalEntryForm` component to add new entries.
        - Contains a `JournalEntriesList` component to display existing entries.
    - `JournalEntryForm`: A component with a `textarea` for content and a date picker. Submits new entries to the backend.
    - `JournalEntriesList`: Fetches and displays a list of past entries, perhaps grouped by date. Each entry should have edit and delete buttons.
- **AI Search Components:**
    - `SearchBar`: An input field where the user types their natural language query.
    - When the form is submitted, it sends the query to the `/api/search` endpoint.
    - `SearchResultsDisplay`: A component that displays a loading state while waiting for the AI's response and then shows the formatted answer received from the backend.

#### **c. State Management**
- Manage global state for the authenticated user and their JWT.
- Manage state for the list of journal entries, loading states, and error messages.

---

## 3. Deployment

- **Backend:** Deploy the Flask application as a Web Service on Render. Configure environment variables in the Render dashboard.
- **Frontend:** Deploy the React application as a Static Site on Render.
- **Database:** Create a free PostgreSQL instance on Supabase and ensure the `pgvector` extension is enabled. Use the database connection string in the Flask app's environment variables.

---
