from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select
from ..deps import get_current_user, require_roles
from ..database import get_session
from ..models import (
    BorrowRecord,
    BorrowCreate,
    Book,
    User,
    Role,
    ReturnBookRequest,
    PaginatedResponse,
)

router = APIRouter(prefix="/borrows", tags=["Borrows"])


@router.post("/", response_model=BorrowRecord)
def borrow_book(
    data: BorrowCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["admin", "librarian"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    book = session.get(Book, data.book_id)
    if not book or book.quantity < 1:
        raise HTTPException(status_code=400, detail="Book unavailable")

    book.quantity -= 1

    rec = BorrowRecord(user_id=data.user_id, book_id=book.id, due_date=data.due_date)

    session.add(rec)
    session.add(book)
    session.commit()
    session.refresh(rec)
    return rec


@router.post("/return", response_model=BorrowRecord)
def return_book(
    data: ReturnBookRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin, Role.librarian)),
):
    rec = session.exec(
        select(BorrowRecord)
        .where(BorrowRecord.user_id == data.user_id)
        .where(BorrowRecord.book_id == data.book_id)
        .where(BorrowRecord.returned_at.is_(None))
    ).first()

    if not rec:
        raise HTTPException(
            status_code=400, detail="Borrow record not found or already returned"
        )

    now = datetime.utcnow()
    if now > rec.due_date:
        raise HTTPException(status_code=400, detail="Book return is overdue!")

    book = session.get(Book, rec.book_id)
    if book:
        book.quantity += 1
        session.add(book)

    rec.returned_at = now
    session.add(rec)
    session.commit()
    session.refresh(rec)
    return rec


@router.get("/", response_model=PaginatedResponse)
def list_borrow_records(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin, Role.librarian)),
):
    total = session.exec(select(func.count()).select_from(BorrowRecord)).one()

    offset = (page - 1) * size

    items = session.exec(
        select(BorrowRecord).order_by(BorrowRecord.id).offset(offset).limit(size)
    ).all()

    return PaginatedResponse(
        page=page,
        size=size,
        total=total,
        items=items,
    )
