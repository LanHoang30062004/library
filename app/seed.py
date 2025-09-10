from sqlmodel import Session, select
from .database import engine
from .models import User, Role
from .security import hash_password

def seed_admin():
    with Session(engine) as s:
        existed = s.exec(select(User).where(User.username == "admin")).first()
        if not existed:
            admin = User(username="admin", full_name="Administrator", role=Role.admin, hashed_password=hash_password("admin123"))
            s.add(admin)
            s.commit()
            
if __name__ == "__main__":
    seed_admin()
