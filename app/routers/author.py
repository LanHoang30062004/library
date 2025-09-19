from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func
from typing import Optional, List
from ..models import Author, User, Role, AuthorRead , PaginatedAuthors , AuthorCreate , AuthorUpdate
from ..deps import get_current_user, require_roles
from ..database import get_session


router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=PaginatedAuthors)
def list_authors(
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin, Role.librarian)),  # chỉ admin và librarian
):
    stmt = select(Author)
    if q:
        stmt = stmt.where(Author.name.ilike(f"%{q}%"))

    count_stmt = select(func.count()).select_from(Author)
    if q:
        count_stmt = count_stmt.where(Author.name.ilike(f"%{q}%"))
    total = session.exec(count_stmt).one()

    stmt = stmt.order_by(Author.id)
    items = session.exec(stmt.offset((page - 1) * size).limit(size)).all()

    total_pages = (total + size - 1) // size

    return PaginatedAuthors(
        items=[AuthorRead.model_validate(a) for a in items],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
    )
@router.post("/", response_model=AuthorRead)
def create_author(
    data: AuthorCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin, Role.librarian))
):
    author = Author(**data.dict())
    session.add(author)
    session.commit()
    session.refresh(author)
    return AuthorRead.model_validate(author)


@router.put("/{author_id}", response_model=AuthorRead)
def update_author(
    author_id: int,
    data: AuthorUpdate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin, Role.librarian))
):
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(author, key, value)

    session.add(author)
    session.commit()
    session.refresh(author)
    return AuthorRead.model_validate(author)


@router.delete("/{author_id}")
def delete_author(
    author_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin, Role.librarian))
):
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    session.delete(author)
    session.commit()
    return {"detail": "Author deleted successfully"}

