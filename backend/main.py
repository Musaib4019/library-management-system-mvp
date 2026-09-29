from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from database import engine, get_db
import models, schemas, auth, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management System")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since it's local academic project
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# -----------------
# USERS API
# -----------------
@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(search: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_librarian_or_admin)):
    return crud.get_users(db, skip=skip, limit=limit, search=search)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_librarian_or_admin)):
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -----------------
# BOOKS API
# -----------------
@app.post("/books", response_model=schemas.BookResponse)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_librarian_or_admin)):
    return crud.create_book(db=db, book=book, current_user_id=current_user.id)

@app.get("/books", response_model=list[schemas.BookResponse])
def get_books(search: str = None, category: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_books(db, skip=skip, limit=limit, search=search, category=category)

@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books/{book_id}/copies", response_model=schemas.BookCopyResponse)
def add_book_copy(book_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_admin)):
    copy = crud.add_book_copy(db, book_id=book_id, current_user_id=current_user.id)
    if not copy:
        raise HTTPException(status_code=404, detail="Book not found")
    return copy

@app.get("/books/{book_id}/copies", response_model=list[schemas.BookCopyResponse])
def get_book_copies(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book.copies

# -----------------
# LOANS API
# -----------------
@app.post("/loans/issue", response_model=schemas.LoanResponse)
def issue_book(loan: schemas.LoanCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_librarian_or_admin)):
    new_loan, error = crud.issue_book(db, user_id=loan.user_id, copy_id=loan.copy_id, current_user_id=current_user.id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return new_loan

@app.post("/loans/{loan_id}/return", response_model=schemas.LoanResponse)
def return_book(loan_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_librarian_or_admin)):
    loan, error = crud.return_book(db, loan_id=loan_id, current_user_id=current_user.id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return loan

@app.post("/loans/{loan_id}/renew", response_model=schemas.LoanResponse)
def renew_book(loan_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    loan, error = crud.renew_book(db, loan_id=loan_id, user_id=current_user.id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return loan

@app.get("/users/{user_id}/loans", response_model=list[schemas.LoanDetails])
def get_member_loans(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == models.Role.MEMBER and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view other members' loans")
    return crud.get_member_loans(db, user_id)

@app.get("/loans/active", response_model=list[schemas.LoanDetails])
def get_all_active_loans(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_librarian_or_admin)):
    return db.query(models.Loan).filter(models.Loan.status == models.LoanStatus.ACTIVE).all()

# -----------------
# RESERVATIONS API
# -----------------
@app.post("/reservations", response_model=schemas.ReservationResponse)
def reserve_book(reservation: schemas.ReservationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    res, error = crud.reserve_book(db, book_id=reservation.book_id, user_id=current_user.id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return res

@app.get("/users/{user_id}/reservations", response_model=list[schemas.ReservationResponse])
def get_user_reservations(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == models.Role.MEMBER and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(models.Reservation).filter(models.Reservation.user_id == user_id).all()

# -----------------
# FINES & NOTIFICATIONS API
# -----------------
@app.get("/users/{user_id}/fines", response_model=list[schemas.FineResponse])
def get_user_fines(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == models.Role.MEMBER and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(models.Fine).filter(models.Fine.user_id == user_id).all()

@app.get("/users/{user_id}/notifications", response_model=list[schemas.NotificationResponse])
def get_user_notifications(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == models.Role.MEMBER and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    notifs = db.query(models.Notification).filter(models.Notification.user_id == user_id).order_by(models.Notification.created_at.desc()).all()
    # Mark as read
    for n in notifs:
        if not n.is_read:
            n.is_read = True
    db.commit()
    return notifs

# -----------------
# DASHBOARD / REPORTS API
# -----------------
@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_admin)):
    return crud.get_dashboard_stats(db)

@app.get("/audit", response_model=list[schemas.AuditLogResponse])
def get_audit_logs(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_admin)):
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(100).all()

