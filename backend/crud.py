from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
import models, schemas, auth
from datetime import datetime, timedelta
import uuid

def create_audit_log(db: Session, user_id: int, action: str, target_type: str, target_id: int = None):
    log = models.AuditLog(user_id=user_id, action=action, target_type=target_type, target_id=target_id)
    db.add(log)
    db.commit()

def create_notification(db: Session, user_id: int, message: str):
    notif = models.Notification(user_id=user_id, message=message)
    db.add(notif)
    db.commit()

# --- Users ---
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        name=user.name, 
        email=user.email, 
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    create_audit_log(db, db_user.id, "USER_CREATED", "User", db_user.id)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(models.User)
    if search:
        query = query.filter(models.User.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# --- Books ---
def create_book(db: Session, book: schemas.BookCreate, current_user_id: int):
    db_book = models.Book(
        isbn=book.isbn, title=book.title, author=book.author,
        category=book.category, publisher=book.publisher,
        year=book.year, description=book.description,
        total_copies=book.total_copies, available_copies=book.total_copies
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    # Create copies
    for i in range(book.total_copies):
        copy = models.BookCopy(
            book_id=db_book.id,
            copy_number=f"{book.isbn}-{i+1}-{str(uuid.uuid4())[:4]}"
        )
        db.add(copy)
    db.commit()
    create_audit_log(db, current_user_id, "BOOK_CREATED", "Book", db_book.id)
    return db_book

def get_books(db: Session, skip: int = 0, limit: int = 100, search: str = None, category: str = None):
    query = db.query(models.Book)
    if search:
        query = query.filter(
            or_(
                models.Book.title.ilike(f"%{search}%"),
                models.Book.author.ilike(f"%{search}%"),
                models.Book.isbn.ilike(f"%{search}%")
            )
        )
    if category:
        query = query.filter(models.Book.category == category)
    return query.offset(skip).limit(limit).all()

def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def add_book_copy(db: Session, book_id: int, current_user_id: int):
    book = get_book(db, book_id)
    if not book:
        return None
    copy = models.BookCopy(
        book_id=book.id,
        copy_number=f"{book.isbn}-{book.total_copies+1}-{str(uuid.uuid4())[:4]}"
    )
    db.add(copy)
    book.total_copies += 1
    book.available_copies += 1
    db.commit()
    create_audit_log(db, current_user_id, "COPY_ADDED", "Book", book.id)
    return copy

# --- Loans ---
def issue_book(db: Session, user_id: int, copy_id: int, current_user_id: int):
    copy = db.query(models.BookCopy).filter(models.BookCopy.id == copy_id).first()
    if not copy or copy.status != models.CopyStatus.AVAILABLE:
        return None, "Copy not available"
    
    user = get_user(db, user_id)
    if not user:
        return None, "User not found"
        
    # Check max books limit (e.g., 3)
    active_loans = db.query(models.Loan).filter(models.Loan.user_id == user_id, models.Loan.status == models.LoanStatus.ACTIVE).count()
    if active_loans >= 3:
        return None, "Borrowing limit exceeded"

    due_date = datetime.utcnow() + timedelta(days=14) # 14 days loan period
    
    loan = models.Loan(
        user_id=user_id,
        copy_id=copy_id,
        due_date=due_date
    )
    db.add(loan)
    copy.status = models.CopyStatus.ISSUED
    copy.book.available_copies -= 1
    db.commit()
    db.refresh(loan)
    
    create_audit_log(db, current_user_id, "BOOK_ISSUED", "Loan", loan.id)
    create_notification(db, user_id, f"You have been issued '{copy.book.title}'. Due date: {due_date.strftime('%Y-%m-%d')}")
    
    return loan, None

def return_book(db: Session, loan_id: int, current_user_id: int):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan or loan.status != models.LoanStatus.ACTIVE:
        return None, "Active loan not found"
        
    loan.status = models.LoanStatus.RETURNED
    loan.return_date = datetime.utcnow()
    loan.copy.status = models.CopyStatus.AVAILABLE
    loan.copy.book.available_copies += 1
    
    # Calculate fine
    fine_amount = 0
    if loan.return_date > loan.due_date:
        days_overdue = (loan.return_date - loan.due_date).days
        if days_overdue > 0:
            fine_amount = days_overdue * 5.0 # Rs 5 per day
            fine = models.Fine(loan_id=loan.id, user_id=loan.user_id, amount=fine_amount)
            db.add(fine)
            create_notification(db, loan.user_id, f"A fine of Rs {fine_amount} has been added for overdue book '{loan.copy.book.title}'.")
            
    db.commit()
    
    create_audit_log(db, current_user_id, "BOOK_RETURNED", "Loan", loan.id)
    create_notification(db, loan.user_id, f"You successfully returned '{loan.copy.book.title}'.")
    
    # Check for reservations
    check_reservations(db, loan.copy.book.id)
    
    return loan, None

def renew_book(db: Session, loan_id: int, user_id: int):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id, models.Loan.user_id == user_id).first()
    if not loan or loan.status != models.LoanStatus.ACTIVE:
        return None, "Active loan not found"
        
    if loan.renewals >= 2:
        return None, "Maximum renewals reached"
        
    # Check if there are reservations for this book
    reservations = db.query(models.Reservation).filter(models.Reservation.book_id == loan.copy.book_id, models.Reservation.status == models.ReservationStatus.PENDING).count()
    if reservations > 0:
        return None, "Cannot renew, book is reserved by another member"
        
    loan.due_date = loan.due_date + timedelta(days=14)
    loan.renewals += 1
    db.commit()
    db.refresh(loan)
    create_audit_log(db, user_id, "BOOK_RENEWED", "Loan", loan.id)
    return loan, None

def get_member_loans(db: Session, user_id: int):
    return db.query(models.Loan).filter(models.Loan.user_id == user_id).order_by(desc(models.Loan.issue_date)).all()

# --- Reservations ---
def reserve_book(db: Session, book_id: int, user_id: int):
    book = get_book(db, book_id)
    if not book:
        return None, "Book not found"
    
    if book.available_copies > 0:
        return None, "Copies are available, you can issue directly"
        
    # Check if already reserved
    existing = db.query(models.Reservation).filter(models.Reservation.book_id == book_id, models.Reservation.user_id == user_id, models.Reservation.status == models.ReservationStatus.PENDING).first()
    if existing:
        return None, "You already have a pending reservation for this book"
        
    reservation = models.Reservation(user_id=user_id, book_id=book_id)
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    create_audit_log(db, user_id, "BOOK_RESERVED", "Reservation", reservation.id)
    return reservation, None

def check_reservations(db: Session, book_id: int):
    book = get_book(db, book_id)
    if book.available_copies > 0:
        oldest_res = db.query(models.Reservation).filter(models.Reservation.book_id == book_id, models.Reservation.status == models.ReservationStatus.PENDING).order_by(models.Reservation.created_at).first()
        if oldest_res:
            create_notification(db, oldest_res.user_id, f"The book '{book.title}' you reserved is now available!")

# --- Misc ---
def get_dashboard_stats(db: Session):
    total_books = db.query(models.Book).count()
    total_copies = sum([b.total_copies for b in db.query(models.Book).all()])
    available_copies = sum([b.available_copies for b in db.query(models.Book).all()])
    issued_copies = total_copies - available_copies
    total_members = db.query(models.User).filter(models.User.role == models.Role.MEMBER).count()
    overdue_books = db.query(models.Loan).filter(models.Loan.status == models.LoanStatus.ACTIVE, models.Loan.due_date < datetime.utcnow()).count()
    active_res = db.query(models.Reservation).filter(models.Reservation.status == models.ReservationStatus.PENDING).count()
    fine_total = sum([f.amount for f in db.query(models.Fine).filter(models.Fine.status == models.FineStatus.UNPAID).all()])
    
    return {
        "total_books": total_books,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "issued_copies": issued_copies,
        "total_members": total_members,
        "overdue_books": overdue_books,
        "active_reservations": active_res,
        "outstanding_fines": fine_total
    }
