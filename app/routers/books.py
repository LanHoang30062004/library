from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from ..deps import get_current_user, require_roles
from ..database import get_session
from ..models import Book, BookCreate, BookRead, Role, User
from sqlalchemy import func

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[BookRead])
def list_books(
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    stmt = select(Book)
    if q:
        stmt = stmt.where(Book.title.ilike(f"%{q}%"))
    if category_id:
        stmt = stmt.where(Book.category_id == category_id)
    if author_id:
        stmt = stmt.where(Book.author_id == author_id)

    count_stmt = select(func.count()).select_from(Book)
    if q:
        count_stmt = count_stmt.where(Book.title.ilike(f"%{q}%"))
    if category_id:
        count_stmt = count_stmt.where(Book.category_id == category_id)
    if author_id:
        count_stmt = count_stmt.where(Book.author_id == author_id)
    total = session.exec(count_stmt).one()

    stmt = stmt.order_by(Book.id)

    items = session.exec(stmt.offset((page - 1) * size).limit(size)).all()

    return [BookRead.model_validate(b) for b in items]


@router.post("/", response_model=BookRead)
def create_book(
    data: BookCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin, Role.librarian)),
):
    book = Book(**data.model_dump())
    session.add(book)
    session.commit()
    session.refresh(book)
    return BookRead.model_validate(book)


@router.get("/{book_id}", response_model=BookRead)
def get_book(
    book_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookRead.model_validate(book)


@router.put("/{book_id}", response_model=BookRead)
def update_book(
    book_id: int,
    data: BookCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin, Role.librarian)),
):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for k, v in data.model_dump().items():
        setattr(book, k, v)
    session.add(book)
    session.commit()
    session.refresh(book)
    return BookRead.model_validate(book)


@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin, Role.librarian)),
):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
