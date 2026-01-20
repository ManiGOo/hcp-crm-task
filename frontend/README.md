# HCP CRM Task Frontend

This is the frontend application for the HCP CRM Task, built with React and Redux. It provides an interface for logging interactions with Healthcare Professionals (HCPs) and viewing a list of all logged interactions. The logging process is flexible, allowing users to input data via a structured form or through a conversational AI chat interface.

## Tech Stack

*   **Framework:** React (Vite for fast development)
*   **State Management:** Redux Toolkit
*   **Routing:** React Router DOM
*   **HTTP Client:** Axios
*   **Styling:** Inline styles (for simplicity and direct component control)
*   **Font:** Google Inter (as per project requirements)

## Features

*   **Log HCP Interactions:**
    *   **Structured Form:** Manually enter details for HCP Name, Date, Time, Interaction Type, Attendees, Topics Discussed, Materials Shared, HCP Sentiment & Outcomes, AI Generated Summary, and Follow-up Actions.
    *   **AI Assistant Chat:** Describe an interaction in natural language, and the AI assistant will extract relevant data to pre-fill the form fields.
*   **View Logged Interactions:** A dedicated route (`/interactions`) to display a list of all interactions fetched from the backend.
*   **Frontend Routing:** Navigate between the logging screen and the interactions list.

## Prerequisites

Before running this application, ensure you have the following installed:

*   Node.js (LTS version recommended)
*   npm (Node Package Manager) or Yarn
*   A running backend API (expected to be at `http://localhost:8000`). This frontend is designed to interact with the FastAPI backend of this project.

## Installation

1.  **Clone the repository:**
    ```bash
    # If part of a larger monorepo, clone the main repository
    git clone <your-repository-url>
    cd <your-repository-directory>/frontend
    ```
    (Or `cd` into the frontend directory if already cloned)

2.  **Install dependencies:**
    ```bash
    npm install
    # or
    yarn install
    ```

## Usage

### Development Mode

To run the application in development mode with hot-reloading:

```bash
npm run dev
# or
yarn dev
```

The application will typically be accessible at `http://localhost:5173`. Ensure your backend API is running concurrently at `http://localhost:8000`.

### Build for Production

To build the application for production:

```bash
npm run build
# or
yarn build
```

This will compile the application into the `dist/` directory, ready for deployment.

## Frontend Routes

*   `/`: The main screen for logging new HCP interactions.
*   `/interactions`: Displays a list of all logged HCP interactions.

## Configuration

The backend API URL is currently hardcoded within `src/pages/Interactions.jsx` and `src/pages/LogInteractionScreen.jsx` to `http://localhost:8000`. For production or different environments, consider externalizing this configuration (e.g., via environment variables or a configuration file).

## Known Issues & Notes

*   **Date/Time Format in Logging Form:** The `<input type="date">` and `<input type="time">` elements in the logging form expect specific `YYYY-MM-DD` and `HH:mm` formats respectively. If the AI Assistant extracts non-standard values like "today" or "not specified" for these fields, React will issue warnings. This is primarily a backend data extraction and normalization issue that should be handled before sending data to the frontend.
*   **Date Display in Interactions List:** Dates fetched from the backend are expected to be ISO 8601 strings. The display component includes logic to parse and format these into `YYYY-MM-DD` format, handling potential `null` or invalid values gracefully.

---

Feel free to contribute or report issues!