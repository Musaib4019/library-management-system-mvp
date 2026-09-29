# Library Management System

A polished, realistic, and functional MVP for a Library Management System built as a B.Tech Software Engineering academic project.

## Technology Stack
- **Frontend**: React, Vite, Tailwind CSS, React Router, Axios
- **Backend**: FastAPI, Python 3
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT, bcrypt password hashing

## Features
- **Role-based Access Control**: Distinct dashboards for Admin, Librarian, and Members.
- **Book Catalogue**: Add, edit, and browse books and multiple physical copies.
- **Circulation Desk**: Issue and return books. Checks availability and member limits.
- **Member Dashboard**: Visually appealing UI for members to see active loans, notifications, and fines.
- **Renewals & Reservations**: Renew eligible books, and reserve books that are currently checked out.
- **Fines**: Automatic fine calculation for overdue books.
- **Audit Logging**: Logs important events (book creation, issuing, returns) for traceability.

## Project Structure
The project uses a clean client-server architecture.
- `backend/`: FastAPI application, database models, schemas, and routes.
- `frontend/`: React + Vite application, Tailwind styling, and role-based views.

## Installation & Running Locally

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install fastapi "uvicorn[standard]" sqlalchemy "passlib[bcrypt]" "python-jose[cryptography]" "pydantic[email]" python-multipart
python seed.py        # Seed the database with initial demo data
uvicorn main:app --reload --port 8000
```
Backend will be available at `http://localhost:8000`
API Documentation available at `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at `http://localhost:3000` (or the port Vite provides)

## Demo Accounts
All passwords are: `password123`
- **Admin**: admin@library.edu
- **Librarian**: librarian@library.edu
- **Member**: member1@library.edu (or musaib@library.edu)

## Testing Core Workflows
For your demonstration, follow this path:
1. Log in as **Admin** (`admin@library.edu`) -> View dashboard stats -> Go to "Manage Books" -> Add a new book.
2. Log in as **Librarian** (`librarian@library.edu`) -> Go to Circulation Desk -> Search for member "Musaib" -> Search for the new book -> Issue it.
3. Log in as **Member** (`musaib@library.edu`) -> See the newly issued book -> Try to renew it -> Browse catalog.
4. Back to **Librarian** -> Select member -> Return the book.

## Future Improvements
- Pagination for large lists.
- Email/SMS notifications via third-party providers.
- Advanced reporting and charts.
- Export to CSV/PDF features.
