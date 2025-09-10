from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..deps import require_roles
from ..models import User, UserRead, Role
from ..database import get_session

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin))
):
    return [UserRead.model_validate(u) for u in session.exec(select(User)).all()]

@router.patch("/{user_id}/role", response_model=UserRead)
def update_role(
    user_id: int,
    role: Role,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(Role.admin))
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserRead.model_validate(user)
