# 🚀 FastAPI Backend

This project provides the core API layer, built with FastAPI for high performance. It was migrated from a previous Node.js backend and is designed to integrate smoothly with outbreakx frontend.

---

## 📖 Table of Contents

- [🚀 FastAPI Backend](#-fastapi-backend)
  - [📖 Table of Contents](#-table-of-contents)
  - [📁 Project Structure](#-project-structure)
  - [🔧 Prerequisites](#-prerequisites)
  - [⚙️ Setup Instructions](#️-setup-instructions)
  - [▶️ Running the Development Server](#️-running-the-development-server)
  - [🔑 Environment Variables](#-environment-variables)
  - [📦 Core Dependencies](#-core-dependencies)
  - [📚 API Documentation](#-api-documentation)
  - [🧪 Testing](#-testing)
  - [🚀 Deployment](#-deployment)
  - [🧑‍💻 Author](#-author)
  - [📄 License](#-license)

---

## 📁 Project Structure

```text
backend-fastapi/
│
├── app/                 # Contains the core application logic
│   ├── api/             # API endpoint routers/modules
│   ├── core/            # Core components like config, settings
│   ├── crud/            # CRUD (Create, Read, Update, Delete) database operations
│   ├── db/              # Database session setup, base models
│   ├── models/          # Pydantic models (request/response schemas)
│   ├── schemas/         # Pydantic schemas (can be merged with models or kept separate)
│   └── main.py          # FastAPI application entry point
│
├── tests/               # Application tests (e.g., using pytest)
├── venv/                # Python virtual environment (should be in .gitignore)
├── .env                 # Environment variables (should be in .gitignore)
├── .gitignore           # Specifies intentionally untracked files that Git should ignore
├── requirements.txt     # Project dependencies
└── README.md            # This file
```

---

## 🔧 Prerequisites

- **Python 3.7+**: Check your version with `python3 --version` or `python --version`. [Download Python](https://www.python.org/downloads/).
- **Git**: For cloning the repository.
- **PostgreSQL with PostGIS**: Geometry columns require PostGIS to be installed on the PostgreSQL server.

---

## ⚙️ Setup Instructions

1.  **Clone the Repository**:

    ```bash
    git clone <your-repo-url>
    cd backend-fastapi
    ```

2.  **Create and Activate Virtual Environment**:
    - It's highly recommended to use a virtual environment to manage project dependencies separately.

    ```bash
    # Create the virtual environment (using 'venv' folder name is common)
    python3 -m venv venv
    ```

    - Activate it:
      - **macOS / Linux**:
        ```bash
        source venv/bin/activate
        ```
      - **Windows (PowerShell)**:
        ```powershell
        .\venv\Scripts\Activate.ps1
        # If script execution is disabled, you might need:
        # Set-ExecutionPolicy Unrestricted -Scope Process
        # then run the activation script again.
        ```
      - **Windows (CMD)**:
        ```cmd
        venv\Scripts\activate.bat
        ```
    - _(Your terminal prompt should now indicate that you are in the virtual environment, e.g., `(venv) ...`)_

3.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    - Create a `.env` file in the project root (`backend-fastapi/`).
    - Copy the contents of `.env.example` (if provided) or add the necessary variables (see [Environment Variables](#-environment-variables) section below).
    - Example `.env` content:
      ```env
      DATABASE_URL=postgresql://user:password@localhost:5432/dbname
      # Add other variables as needed
      ```
    - **Important**: Ensure `.env` and `venv/` are listed in your `.gitignore` file to avoid committing secrets and the environment folder.

5.  **Enable PostGIS (required)**:
    - If you use your own PostgreSQL instance, install PostGIS on that server and then run:
    ```sql
    CREATE EXTENSION IF NOT EXISTS postgis;
    ```

    - Easiest local option: use the included Docker Compose database service, which is already PostGIS-enabled.
    ```bash
    docker compose up -d db
    ```

---

## ▶️ Running the Development Server

Once the setup is complete, run the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- `main:app`: Tells Uvicorn where to find the FastAPI application instance (`app`) located in the `main.py` file inside the `app` directory.
- `--reload`: Automatically restarts the server when code changes are detected. Ideal for development.
- `--host 0.0.0.0`: Makes the server accessible on your local network (not just `localhost`).
- `--port 8000`: Specifies the port to run on.

You should be able to access the API at `http://localhost:8000` or `http://<your-local-ip>:8000`.

---

## 🔑 Environment Variables

The application requires certain environment variables to be set. These should be defined in a `.env` file in the project root.

| Variable       | Description                         | Example                                       | Required |
| -------------- | ----------------------------------- | --------------------------------------------- | -------- |
| `DATABASE_URL` | Connection string for the database. | `postgresql://user:password@host:port/dbname` | Yes      |

_(Add/remove variables as needed for your specific project)_

---

## 📦 Core Dependencies

This project relies on several key Python libraries:

- [FastAPI](https://fastapi.tiangolo.com/): The core web framework.
- [Uvicorn](https://www.uvicorn.org/): The ASGI server to run the application.
- [Pydantic](https://docs.pydantic.dev/): Used for data validation and settings management.
- [SQLAlchemy](https://www.sqlalchemy.org/): The ORM for database interaction (if applicable).
- [python-dotenv](https://pypi.org/project/python-dotenv/): For loading environment variables from the `.env` file.
- _(Add any other crucial dependencies, e.g., database drivers like `psycopg2-binary` for PostgreSQL)_

Refer to `requirements.txt` for the full, pinned list of dependencies.

---

## 📚 API Documentation

FastAPI automatically generates interactive API documentation. Once the development server is running, you can access:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testing

_(This section needs to be filled in based on your testing strategy)_

To run the tests:

```bash
# Example using pytest
pytest tests/
```

- Describe the testing framework used (e.g., `pytest`).
- Explain how to configure the test environment (e.g., test database).
- Mention any specific commands or coverage reporting.

---

## 🚀 Deployment

_(This section needs to be filled in based on your deployment strategy)_

Provide instructions or notes on how to deploy the application. Examples:

- **Docker**: Include steps to build and run the Docker image. Mention the `Dockerfile`.
- **Serverless**: Instructions for deploying to platforms like AWS Lambda, Google Cloud Run, etc.
- **Traditional Server**: Steps for setting up Uvicorn with Gunicorn behind a reverse proxy like Nginx.

---

## 🧑‍💻 Author

- Kavindu Hettiarachchi

---

## 📄 License

_(Specify the license for your project)_
