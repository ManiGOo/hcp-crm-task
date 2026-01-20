# Backend Service for HCP CRM Interaction Logger

This directory contains the FastAPI backend service for the HCP CRM Interaction Logger application. It is responsible for handling API requests, orchestrating the AI agent, managing database interactions, and providing structured data to the frontend.

## Technologies Used

*   **Framework:** FastAPI (Python)
*   **AI Agent Framework:** LangGraph
*   **LLMs:** Groq API (`llama-3.3-70b-versatile` configured, others configurable)
*   **Database ORM:** SQLAlchemy with `asyncpg` (for asynchronous PostgreSQL interaction)
*   **Dependency Management:** `pip` (via `requirements.txt`)
*   **Containerization:** Docker

## Project Structure

```
backend/
├── app/                  # FastAPI application modules
│   ├── agent/            # LangGraph AI agent and tools definitions
│   │   ├── graph.py      # Defines the AgentState, LLM, tools, and the LangGraph workflow.
│   │   └── tools.py      # Implements the callable tools for the AI agent (e.g., log_interaction, edit_interaction).
│   ├── crud.py           # Contains asynchronous CRUD operations for the database.
│   ├── database.py       # Configures the SQLAlchemy engine and provides database session management.
│   ├── init_db.py        # Script to initialize/reset the database schema.
│   ├── main.py           # Main FastAPI application; defines API endpoints and orchestrates agent interaction.
│   ├── models.py         # Defines SQLAlchemy ORM models and database schema.
│   └── schemas.py        # Pydantic models for request/response data validation and serialization.
├── backend.Dockerfile    # Dockerfile for building the backend Docker image.
└── requirements.txt      # Lists Python dependencies required by the backend.
```

## Setup and Running the Backend

You can run the backend locally (with a local PostgreSQL instance or a Dockerized one) or entirely via Docker Compose. Using Docker Compose is the recommended approach for development and testing as it simplifies environment management.

### Recommended: Running with Docker Compose

Ensure you are in the project root directory (one level above this `backend/` directory).

1.  **Ensure `.env` file is set up:**
    *   Create a `.env` file in the project root with `GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE`.

2.  **Build and run services:**
    ```bash
    docker-compose up --build
    ```
    This will start the PostgreSQL database and the FastAPI backend.

3.  **Access:**
    *   FastAPI application: `http://localhost:8000`
    *   Interactive API docs (Swagger UI): `http://localhost:8000/docs`
    *   Health check: `http://localhost:8000/health`

### Local Development (without Docker for Backend)

1.  **Prerequisites:**
    *   Python 3.8+
    *   Poetry (if you prefer, otherwise `pip install -r requirements.txt`)
    *   A running PostgreSQL database instance (update `DATABASE_URL` if not using default `postgresql://postgres:postgres@localhost:5432/hcp_crm_db`).

2.  **Install Dependencies:**
    Navigate into the `backend/` directory:
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3.  **Environment Variables:**
    *   Make sure you have a `.env` file in the project root (not in `backend/`) with your `GROQ_API_KEY` and `DATABASE_URL`.
    *   Example `.env` (in project root):
        ```
        GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/hcp_crm_db"
        ```

4.  **Initialize the Database:**
    You need to run the `init_db.py` script to create the necessary tables.
    ```bash
    python -m app.init_db
    ```
    *Warning: This script drops and recreates all tables, erasing existing data.*

5.  **Run the FastAPI application:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The `--reload` flag is useful for local development to automatically restart the server on code changes.

## API Endpoints

*   **`POST /chat`**: The main endpoint for conversational interaction with the AI agent to log HCP interactions. Expects a JSON body with a `message` string.
*   **`GET /interactions`**: Retrieves a list of all logged HCP interactions. Returns a JSON array of interaction objects.
*   **`GET /health`**: A simple health check endpoint. Returns `{"status": "ok"}`.

## AI Agent (LangGraph) Details

The AI agent, defined in `app/agent/graph.py` and `app/agent/tools.py`, uses a sophisticated LangGraph workflow to:
*   **Extract Structured Data:** Convert natural language messages into a structured format for logging.
*   **Generate Summaries:** Automatically create concise summaries of interactions if not provided by the user.
*   **Utilize Tools:** The agent has access to several tools (e.g., `log_interaction`, `edit_interaction`, `search_hcp`, `suggest_follow_up`, `generate_summary`, `check_compliance`) to perform CRM tasks.
*   **Robust Data Handling:** The backend includes post-processing logic in `main.py` to handle common natural language date/time inputs (e.g., "today", "not specified") from the AI, ensuring data is always stored in valid formats.

---
