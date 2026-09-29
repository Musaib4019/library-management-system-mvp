# Software Engineering Syllabus Mapping

This document maps the concepts implemented in the Library Management System to standard B.Tech Software Engineering syllabus topics. This will assist during the academic demonstration and viva.

| Software Engineering Concept | How it is demonstrated in this project |
| :--- | :--- |
| **Requirement Analysis & SRS** | The system enforces strict business rules derived from typical library requirements (e.g., maximum borrow limit of 3, loan period of 14 days, fines for overdue returns). |
| **Modular Design / Cohesion / Coupling** | Code is strictly separated. Backend separates concerns into `models.py` (Database), `schemas.py` (Validation), `crud.py` (Business Logic), and `main.py` (Routing). Frontend separates UI components, routing, context (Auth), and API abstraction (`api.js`). |
| **Layered Architecture** | Client-Server Architecture. Frontend (Presentation Layer) -> REST API (Application Layer) -> SQLite (Data Layer). |
| **Database Design (ER / Normalization)** | Entities are properly normalized. `Book` represents the catalog entry, while `BookCopy` represents the physical item. `Loan` represents the transactional relationship between `User` and `BookCopy`. |
| **Software Quality Assurance** | Input validation is enforced at the API boundary using Pydantic schemas (e.g., Email validation, type checking). |
| **Security & Authentication** | Implemented using JSON Web Tokens (JWT). Passwords are never stored in plaintext (using bcrypt hashing). Route-level and component-level Role-Based Access Control (RBAC) ensures users only see what they are authorized to see. |
| **Configuration Management / Traceability** | The `AuditLog` tracks state changes (e.g., Book Issued, Book Returned, User Created), ensuring a traceable history of critical operations. |
| **Maintenance & Extensibility** | The use of ORM (SQLAlchemy) means the database can be easily swapped from SQLite to PostgreSQL without rewriting business logic, supporting future scalability. |
| **Agile / Iterative Development** | The project was built focusing on a core Minimum Viable Product (MVP) prioritizing essential workflows (Issue/Return) before expanding to edge cases like fines and reservations. |
