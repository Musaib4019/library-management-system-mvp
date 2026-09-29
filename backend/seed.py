from database import SessionLocal, engine, Base
import models, crud, schemas
from datetime import datetime, timedelta

def seed_data():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if we already have data
    if db.query(models.User).count() > 0:
        print("Database already seeded.")
        return

    print("Seeding database...")
    
    # Users
    admin = crud.create_user(db, schemas.UserCreate(name="Admin User", email="admin@library.edu", password="password123", role=models.Role.ADMIN))
    librarian = crud.create_user(db, schemas.UserCreate(name="Librarian User", email="librarian@library.edu", password="password123", role=models.Role.LIBRARIAN))
    
    members = []
    for i in range(1, 6):
        member = crud.create_user(db, schemas.UserCreate(name=f"Member {i}", email=f"member{i}@library.edu", password="password123", role=models.Role.MEMBER))
        members.append(member)
        
    musaib = crud.create_user(db, schemas.UserCreate(name="Musaib Manzoor", email="musaib@library.edu", password="password123", role=models.Role.MEMBER))
    members.append(musaib)
    
    # Books
    books_data = [
        {"title": "Software Engineering", "author": "Ian Sommerville", "category": "Computer Science", "isbn": "9780133943030", "publisher": "Pearson", "year": 2015, "description": "10th Edition", "copies": 3},
        {"title": "Clean Code", "author": "Robert C. Martin", "category": "Programming", "isbn": "9780132350884", "publisher": "Prentice Hall", "year": 2008, "description": "A Handbook of Agile Software Craftsmanship", "copies": 2},
        {"title": "Design Patterns", "author": "Erich Gamma", "category": "Programming", "isbn": "9780201633610", "publisher": "Addison-Wesley", "year": 1994, "description": "Elements of Reusable Object-Oriented Software", "copies": 4},
        {"title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "category": "Computer Science", "isbn": "9780262033848", "publisher": "MIT Press", "year": 2009, "description": "3rd Edition", "copies": 2},
        {"title": "The Pragmatic Programmer", "author": "Andrew Hunt", "category": "Programming", "isbn": "9780201616224", "publisher": "Addison-Wesley", "year": 1999, "description": "From Journeyman to Master", "copies": 3},
        {"title": "The Hobbit", "author": "J.R.R. Tolkien", "category": "Fiction", "isbn": "9780547928227", "publisher": "Houghton Mifflin", "year": 1937, "description": "Fantasy novel", "copies": 2},
    ]
    
    db_books = []
    for b in books_data:
        book = crud.create_book(db, schemas.BookCreate(
            isbn=b["isbn"], title=b["title"], author=b["author"], category=b["category"],
            publisher=b["publisher"], year=b["year"], description=b["description"], total_copies=b["copies"]
        ), current_user_id=admin.id)
        db_books.append(book)
        
    # Loans
    # Issue to Musaib: Software Engineering, Clean Code
    se_book = next(b for b in db_books if b.title == "Software Engineering")
    cc_book = next(b for b in db_books if b.title == "Clean Code")
    
    crud.issue_book(db, user_id=musaib.id, copy_id=se_book.copies[0].id, current_user_id=librarian.id)
    loan_cc, _ = crud.issue_book(db, user_id=musaib.id, copy_id=cc_book.copies[0].id, current_user_id=librarian.id)
    
    # Make Clean Code overdue
    loan_cc.due_date = datetime.utcnow() - timedelta(days=2)
    db.commit()
    
    # Return a book
    loan_returned, _ = crud.issue_book(db, user_id=members[0].id, copy_id=db_books[2].copies[0].id, current_user_id=librarian.id)
    crud.return_book(db, loan_id=loan_returned.id, current_user_id=librarian.id)

    # Reservation
    # Make all copies of The Hobbit issued
    hobbit_book = next(b for b in db_books if b.title == "The Hobbit")
    crud.issue_book(db, user_id=members[1].id, copy_id=hobbit_book.copies[0].id, current_user_id=librarian.id)
    crud.issue_book(db, user_id=members[2].id, copy_id=hobbit_book.copies[1].id, current_user_id=librarian.id)
    
    # Musaib reserves The Hobbit
    crud.reserve_book(db, book_id=hobbit_book.id, user_id=musaib.id)
    
    print("Seed data completed.")
    db.close()

if __name__ == "__main__":
    seed_data()
