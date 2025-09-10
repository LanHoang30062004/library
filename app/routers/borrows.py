from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..deps import get_current_user, require_roles
from ..database import get_session
from ..models import BorrowRecord, BorrowCreate, Book, User, Role

router = APIRouter(prefix="/borrows", tags=["Borrows"])

@router.post("/", response_model=BorrowRecord)
def borrow_book(
    data: BorrowCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    book = session.get(Book, data.book_id)
    if not book or book.quantity < 1:
        raise HTTPException(status_code=400, detail="Book unavailable")
    book.quantity -= 1
    rec = BorrowRecord(user_id=current_user.id, book_id=book.id, due_date=data.due_date)
    session.add(rec)
    session.add(book)
    session.commit()
    session.refresh(rec)
    return rec

@router.post("/{borrow_id}/return", response_model=BorrowRecord)
def return_book(
    borrow_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin, Role.librarian))
):
    rec = session.get(BorrowRecord, borrow_id)
    if not rec or rec.returned_at is not None:
        raise HTTPException(status_code=400, detail="Invalid borrow record")
    book = session.get(Book, rec.book_id)
    if book:
        book.quantity += 1
        session.add(book)
    rec.returned_at = datetime.utcnow()
    session.add(rec)
    session.commit()
    session.refresh(rec)
    return rec
