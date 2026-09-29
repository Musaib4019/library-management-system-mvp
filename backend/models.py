from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from database import Base

class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    LIBRARIAN = "LIBRARIAN"
    MEMBER = "MEMBER"

class CopyStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ISSUED = "ISSUED"
    LOST = "LOST"

class LoanStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"

class ReservationStatus(str, enum.Enum):
    PENDING = "PENDING"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"

class FineStatus(str, enum.Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=Role.MEMBER)
    created_at = Column(DateTime, default=datetime.utcnow)

    loans = relationship("Loan", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")
    fines = relationship("Fine", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    category = Column(String, index=True)
    publisher = Column(String)
    year = Column(Integer)
    description = Column(String)
    total_copies = Column(Integer, default=0)
    available_copies = Column(Integer, default=0)
    
    copies = relationship("BookCopy", back_populates="book")
    reservations = relationship("Reservation", back_populates="book")

class BookCopy(Base):
    __tablename__ = "book_copies"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    copy_number = Column(String, unique=True, index=True)
    status = Column(String, default=CopyStatus.AVAILABLE)

    book = relationship("Book", back_populates="copies")
    loans = relationship("Loan", back_populates="copy")

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    copy_id = Column(Integer, ForeignKey("book_copies.id"))
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    return_date = Column(DateTime, nullable=True)
    status = Column(String, default=LoanStatus.ACTIVE)
    renewals = Column(Integer, default=0)

    user = relationship("User", back_populates="loans")
    copy = relationship("BookCopy", back_populates="loans")
    fines = relationship("Fine", back_populates="loan")

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    status = Column(String, default=ReservationStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")

class Fine(Base):
    __tablename__ = "fines"
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    status = Column(String, default=FineStatus.UNPAID)
    created_at = Column(DateTime, default=datetime.utcnow)

    loan = relationship("Loan", back_populates="fines")
    user = relationship("User", back_populates="fines")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String)
    target_type = Column(String)
    target_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
