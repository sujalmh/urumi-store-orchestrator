# How to Run the Store Provisioning Platform

This guide outlines the steps to run the "Store Provisioning Platform" (FastAPI Backend + Next.js Frontend) locally.

## Prerequisites

Ensure you have the following installed:
-   **Python 3.11+**
-   **Node.js 18+** & **npm**
-   **PostgreSQL** (running on port 5432)
-   **Redis** (running on port 6379)
-   **Kubernetes Cluster** (e.g., k3s, Rancher Desktop, or Docker Desktop with K8s enabled)
-   **Helm**

## 1. Database & Redis Setup

Ensure PostgreSQL and Redis are running.
-   Create a database named `provisioning`.
    ```sql
    CREATE DATABASE provisioning;
    ```

## 2. Backend Setup (FastAPI)

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Create a virtual environment:
    ```bash
    python -m venv .venv
    ```

3.  Activate the virtual environment:
    -   **Windows (Command Prompt):** `.venv\Scripts\activate.bat`
    -   **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
    -   **Linux/Mac:** `source .venv/bin/activate`

4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5.  Configure Environment Variables:
    The application uses default values suited for local development (see `app/core/config.py`).
    You can override them by setting environment variables prefixed with `APP_` (e.g., `APP_DATABASE_URL`).
    
    *Defaults:*
    -   `APP_DATABASE_URL`: `postgresql+psycopg://postgres:postgres@localhost:5432/provisioning`
    -   `APP_REDIS_URL`: `redis://localhost:6379/0`
    -   `APP_KUBECONFIG_PATH`: `None` (Uses default kubeconfig)

    If your DB credentials differ, set `APP_DATABASE_URL` accordingly.

6.  Run the Backend:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://localhost:8000`.
    API Documentation: `http://localhost:8000/docs`.

7.  **Run Celery Worker (Required for background tasks):**
    Open a new terminal in the `backend` directory, activate the venv, and run:
    
    *Windows users must use `--pool=solo` to avoid multiprocessing issues:*
    ```bash
    celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
    ```
    
    *Alternatively, run the helper script:*
    ```cmd
    run_worker.bat
    ```

## 3. Frontend Setup (Next.js)

1.  Open a new terminal and navigate to the backend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Run the development server:
    ```bash
    npm run dev
    ```
    The frontend will be available at `http://localhost:3000`.

## 4. Helper Scripts

There is a `scripts` directory, but it currently contains placeholders. You can add your own convenience scripts there.

## Troubleshooting

-   **Database Connection:** Ensure the `APP_DATABASE_URL` matches your local PostgreSQL credentials.
-   **Kubernetes:** Ensure your `kubectl` is configured and points to a valid cluster. The app needs this to provision resources.
