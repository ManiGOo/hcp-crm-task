# HCP CRM Interaction Logger

This project implements a backend service for logging and managing Healthcare Professional (HCP) interactions within a CRM system. It leverages a conversational AI agent to process natural language input, extract structured data, and automate various CRM-related tasks.

## Core Technologies

*   **Backend:** Python with FastAPI
*   **AI Agent Framework:** LangGraph
*   **LLMs:** Groq API (specifically `llama-3.3-70b-versatile` for context and `gemma2-9b-it` can be configured as primary)
*   **Database:** PostgreSQL
*   **Containerization:** Docker & Docker Compose
*   **Frontend (Conceptual):** React UI with Redux for state management (not included in this repository, but the backend is designed to support it).

## Features

*   **Conversational Interaction Logging:** Log new HCP interactions using natural language via an AI chat interface.
*   **Structured Data Extraction:** AI agent extracts key details like HCP name, attendees, date, time, interaction type, topics, materials, outcomes, follow-up, and summary.
*   **AI-Generated Summaries:** Automatically generates concise summaries of interactions if not explicitly provided by the user.
*   **Robust Date/Time Handling:** Backend preprocesses natural language date/time inputs (e.g., "today", "not specified") for consistent database storage.
*   **Interaction Editing:** Tools for modifying existing logged interactions.
*   **HCP Search:** Functionality to search for HCP details.
*   **Follow-up Suggestions:** AI-driven suggestions for next steps based on interaction outcomes.
*   **Compliance Checks:** Basic checks for sensitive topics discussed.
*   **RESTful API:** Provides endpoints for logging, retrieving, and managing interactions.
*   **Containerized Development:** Easy setup and deployment using Docker Compose.

## Project Structure

```
.
├── backend/                  # Backend application code
│   ├── app/                  # FastAPI application modules
│   │   ├── agent/            # LangGraph AI agent and tools
│   │   │   ├── graph.py      # LangGraph workflow definition
│   │   │   └── tools.py      # AI agent's callable tools
│   │   ├── crud.py           # Database CRUD operations
│   │   ├── database.py       # SQLAlchemy database setup
│   │   ├── init_db.py        # Database initialization script
│   │   ├── main.py           # FastAPI application entry point, API endpoints
│   │   ├── models.py         # SQLAlchemy ORM models
│   │   └── schemas.py        # Pydantic data models
│   ├── backend.Dockerfile    # Dockerfile for the backend service
│   ├── README.md             # Backend-specific README
│   └── requirements.txt      # Python dependencies
├── .env                      # Environment variables (e.g., GROQ_API_KEY, DB credentials)
├── docker-compose.yml        # Docker Compose configuration for services
└── README.md                 # Project root README (this file)
```

## Getting Started

These instructions will get you a copy of the project up and running on your local machine using Docker Compose.

### Prerequisites

*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Engine and Docker Compose)

### Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/hcp-crm-task.git
    cd hcp-crm-task
    ```

2.  **Create a `.env` file:**
    In the root directory of the project, create a file named `.env` and add your Groq API key:
    ```
    GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
    ```
    *   *Note:* You can obtain a Groq API key from [console.groq.com](https://console.groq.com/).

3.  **Build and run the services with Docker Compose:**
    Navigate to the project root directory in your terminal and run:
    ```bash
    docker-compose up --build
    ```
    This command will:
    *   Build the Docker image for the backend application (using `backend/backend.Dockerfile`).
    *   Start a PostgreSQL database container.
    *   Start the FastAPI backend container, connected to the database.

4.  **Verify Services:**
    *   The PostgreSQL database will be accessible on port `5432` of your host.
    *   The FastAPI backend will be accessible on `http://localhost:8000`.
    *   You can visit `http://localhost:8000/health` in your browser to check if the backend is running. It should return `{"status": "ok"}`.
    *   FastAPI's interactive API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.

### Using the Application (Backend API)

You can interact with the backend API using tools like cURL, Postman, or directly from a frontend application.

#### **Log an HCP Interaction (Conversational Interface)**

*   **Endpoint:** `POST /chat`
*   **Description:** Send natural language messages to the AI agent to log HCP interactions. The AI will extract structured data, generate summaries if needed, and save the interaction to the database.
*   **Example Request Body (JSON):**
    ```json
    {
      "message": "I had a meeting with Dr. Smith and Nurse Anne on 2026-01-20 at 10:30 AM. We discussed Product X efficacy and side effects. I distributed a brochure. The outcome was positive. Follow-up meeting tomorrow."
    }
    ```
    *   *Note:* Even if you omit details like "summary" or "time", the backend's AI agent will attempt to generate them or use defaults based on context.

#### **Retrieve Logged HCP Interactions**

*   **Endpoint:** `GET /interactions`
*   **Description:** Retrieve a list of all logged HCP interactions.
*   **Example Response (JSON):**
    ```json
    [
      {
        "hcp_name": "Dr. Smith",
        "attendees": "Nurse Anne",
        "date": "2026-01-20T00:00:00",
        "time": "10:30",
        "interaction_type": "Meeting",
        "topics": "Product X efficacy and side effects",
        "attachments": null,
        "materials_distributed": "brochure",
        "outcomes": "Positive",
        "follow_up": "follow-up meeting tomorrow",
        "summary": "Met Dr. Smith and Nurse Anne to discuss Product X efficacy and side effects. Distributed brochure. Positive outcome.",
        "id": 1,
        "created_at": "2026-01-20T10:30:00.123456+00:00",
        "updated_at": "2026-01-20T10:30:00.123456+00:00"
      }
    ]
    ```
    *   *Note:* The `date` field is returned as an ISO 8601 formatted string (e.g., `"YYYY-MM-DDTHH:MM:SS"`). Your frontend will need to parse and format this string for display.

### Shutting Down

To stop and remove the Docker containers:

```bash
docker-compose down
```

---
