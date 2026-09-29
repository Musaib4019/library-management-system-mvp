from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from models import Role, CopyStatus, LoanStatus, ReservationStatus, FineStatus

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = Role.MEMBER

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class BookBase(BaseModel):
    isbn: str
    title: str
    author: str
    category: str
    publisher: str
    year: int
    description: str

class BookCreate(BookBase):
    total_copies: int = 1

class BookResponse(BookBase):
    id: int
    total_copies: int
    available_copies: int
    class Config:
        orm_mode = True

class BookCopyBase(BaseModel):
    book_id: int
    copy_number: str
    status: str = CopyStatus.AVAILABLE

class BookCopyResponse(BookCopyBase):
    id: int
    class Config:
        orm_mode = True

class BookCopyWithBook(BookCopyResponse):
    book: BookResponse
    class Config:
        orm_mode = True

class LoanBase(BaseModel):
    user_id: int
    copy_id: int

class LoanCreate(LoanBase):
    pass

class LoanResponse(LoanBase):
    id: int
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str
    renewals: int
    class Config:
        orm_mode = True

class LoanDetails(LoanResponse):
    user: UserResponse
    copy: BookCopyWithBook
    class Config:
        orm_mode = True

class ReservationBase(BaseModel):
    book_id: int

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(ReservationBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    book: Optional[BookResponse] = None
    class Config:
        orm_mode = True

class FineBase(BaseModel):
    loan_id: int
    amount: float
    status: str = FineStatus.UNPAID

class FineResponse(FineBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        orm_mode = True

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: datetime
    class Config:
        orm_mode = True

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    target_type: str
    target_id: Optional[int]
    timestamp: datetime
    class Config:
        orm_mode = True
