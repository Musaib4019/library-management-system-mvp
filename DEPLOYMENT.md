# Deployment Guide

This project is prepared for deployment on modern cloud platforms (like Render, Vercel, or Heroku).

## Architecture

*   **Frontend**: React (Vite) Single Page Application (SPA).
*   **Backend**: FastAPI REST API.
*   **Database**: SQLite (using SQLAlchemy ORM).

## Deployment Instructions (Render)

We recommend using Render (render.com) for a free and easy deployment.

### 1. Web Service (FastAPI Backend)

1.  Connect your GitHub repository to Render.
2.  Create a new **Web Service**.
3.  Select your repository.
4.  Set the following settings:
    *   **Root Directory**: `backend`
    *   **Environment**: `Python`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5.  *Important Limitation*: Because we are using SQLite in a cloud environment, Render's free tier uses an ephemeral filesystem. This means the database might reset when the server spins down. For an academic demo, this is usually fine, but you can upgrade to a Render "Disk" if you need persistent storage, or migrate to PostgreSQL.
6.  Once deployed, copy the backend URL (e.g., `https://library-backend.onrender.com`).

### 2. Static Site (React Frontend)

1.  Create a new **Static Site** on Render.
2.  Select the same repository.
3.  Set the following settings:
    *   **Root Directory**: `frontend`
    *   **Build Command**: `npm install && npm run build`
    *   **Publish Directory**: `frontend/dist`
4.  Add an **Environment Variable**:
    *   Key: `VITE_API_URL`
    *   Value: Your backend URL from step 1 (e.g., `https://library-backend.onrender.com`).
5.  Deploy the static site.

### 3. Verification

1.  Visit your Frontend URL.
2.  Log in using the demo accounts:
    *   **Admin**: `admin@library.edu`
    *   **Librarian**: `librarian@library.edu`
    *   **Member**: `musaib@library.edu`
    *   *(Password for all: `password123`)*

## Local Development

If you need to run the project locally again:

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Frontend (in a new terminal)
cd frontend
npm run dev
```
