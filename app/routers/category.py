from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from ..deps import get_current_user, require_roles
from ..database import get_session
from ..models import User, Role, CategoryRead, Category
from sqlalchemy import func
from typing import List, Optional

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryRead])
def list_categories(
    q: Optional[str] = None,
    session: Session = Depends(get_session),
    _: User = Depends(
        require_roles(Role.admin, Role.librarian)
    ),  # chỉ admin & librarian
):
    stmt = select(Category)
    if q:
        stmt = stmt.where(Category.name.ilike(f"%{q}%"))
    items = session.exec(stmt).all()
    return [CategoryRead.model_validate(c) for c in items]
