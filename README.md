# HCP CRM Interaction Logger

This project is a full-stack application for logging and managing Healthcare Professional (HCP) interactions. It features a React-based frontend and a Python backend powered by FastAPI and a conversational AI agent.

## Features

*   **Conversational Interaction Logging:** Log new HCP interactions using natural language via an AI chat interface.
*   **Structured Data Extraction:** The AI agent extracts key details like HCP name, attendees, date, time, interaction type, topics, materials, outcomes, follow-up, and summary.
*   **AI-Generated Summaries:** Automatically generates concise summaries of interactions if not explicitly provided by the user.
*   **Robust Date/Time Handling:** The backend preprocesses natural language date/time inputs (e.g., "today", "not specified") for consistent database storage.
*   **Interaction Editing:** Tools for modifying existing logged interactions.
*   **HCP Search:** Functionality to search for HCP details.
*   **Follow-up Suggestions:** AI-driven suggestions for next steps based on interaction outcomes.
*   **Compliance Checks:** Basic checks for sensitive topics discussed.
*   **RESTful API:** Provides endpoints for logging, retrieving, and managing interactions.
*   **Containerized Backend:** The backend is containerized using Docker for easy setup and deployment.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── graph.py
│   │   │   └── tools.py
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── init_db.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── backend.Dockerfile
│   ├── docker-compose.yml
│   ├── README.md
│   └── requirements.txt
└── frontend/
    ├── public/
    │   └── vite.svg
    ├── src/
    │   ├── assets/
    │   ├── components/
    │   ├── pages/
    │   ├── redux/
    │   ├── App.jsx
    │   ├── index.css
    │   └── main.jsx
    ├── .gitignore
    ├── index.html
    ├── package.json
    ├── README.md
    └── vite.config.js
```

## Core Technologies

### Backend

*   **Framework:** Python with FastAPI
*   **AI Agent:** LangGraph
*   **LLMs:** Groq API (`llama-3.3-70b-versatile`, `gemma2-9b-it`)
*   **Database:** PostgreSQL
*   **Containerization:** Docker & Docker Compose

### Frontend

*   **Framework:** React
*   **State Management:** Redux
*   **Build Tool:** Vite
*   **Styling:** CSS

## Getting Started

### Prerequisites

*   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   [Node.js](https://nodejs.org/en/) (v18 or higher) and npm or yarn

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ManiGOo/hcp-crm-task.git
    cd hcp-crm-task
    ```

2.  **Create a `.env` file:**
    In the `backend` directory, create a file named `.env` and add your Groq API key:
    ```
    GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
    ```
    *You can obtain a Groq API key from [console.groq.com](https://console.groq.com/).*

3.  **Build and run the backend with Docker Compose:**
    ```bash
    cd backend
    docker compose up --build
    ```
    *   The backend will be accessible at `http://localhost:8000`.
    *   API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Run the development server:**
    ```bash
    npm run dev
    ```
    *   The frontend will be accessible at `http://localhost:5173` (or another port if 5173 is in use).

## API Usage

You can interact with the backend API using tools like cURL, Postman, or from the frontend application.

#### **Log an HCP Interaction (Conversational Interface)**

*   **Endpoint:** `POST /chat`
*   **Description:** Send natural language messages to the AI agent to log HCP interactions. The AI will extract structured data, generate summaries if needed, and save the interaction to the database.
*   **Example Request Body (JSON):**
    ```json
    {
      "message": "I had a meeting with Dr. Smith and Nurse Anne on 2026-01-20 at 10:30 AM. We discussed Product X efficacy and side effects. I distributed a brochure. The outcome was positive. Follow-up meeting tomorrow."
    }
    ```

#### **Retrieve Logged HCP Interactions**

*   **Endpoint:** `GET /interactions`
*   **Description:** Retrieve a list of all logged HCP interactions.

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.