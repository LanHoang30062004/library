from typing import Optional, List
from datetime import datetime, date
import enum
from sqlmodel import SQLModel, Field, Relationship, Column, Integer


class StrEnum(str, enum.Enum):
    def __str__(self) -> str:
        return str(self.value)


class Role(StrEnum):
    admin = "admin"
    librarian = "librarian"
    member = "member"


class UserBase(SQLModel):
    username: str = Field(default=None)
    full_name: Optional[str] = None
    role: Role = Role.member
    is_active: bool = True


class BorrowRecord(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    user_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id")
    borrowed_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: date
    returned_at: Optional[datetime] = None

    user: Optional["User"] = Relationship(back_populates="borrows")
    book: Optional["Book"] = Relationship(back_populates="borrows")


class User(UserBase, table=True):
    id: Optional[int] = Field(
        default=None, sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    hashed_password: str
    borrows: list[BorrowRecord] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    username: str
    password: str
    full_name: Optional[str] = None


class UserRead(SQLModel):
    id: int
    username: str
    full_name: Optional[str]
    role: Role
    is_active: bool


class Author(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    name: str = Field(default=None)
    biography: Optional[str] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    nationality: Optional[str] = None
    books: List["Book"] = Relationship(back_populates="author")


class AuthorRead(SQLModel):
    id: int
    name: str
    biography: Optional[str] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    nationality: Optional[str] = None


class AuthorCreate(SQLModel):
    name: str
    biography: Optional[str] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    nationality: Optional[str] = None


class AuthorUpdate(SQLModel):
    name: Optional[str] = None
    biography: Optional[str] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    nationality: Optional[str] = None


class PaginatedAuthors(SQLModel):
    items: List[AuthorRead]
    total: int
    page: int
    size: int
    total_pages: int


class Category(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    name: str = Field(default=None)
    books: List["Book"] = Relationship(back_populates="category")


class CategoryRead(SQLModel):
    id: int
    name: str


class BookBase(SQLModel):
    title: str = Field(default=None)
    published_year: Optional[int] = None
    quantity: int = 1


class Book(BookBase, table=True):
    id: Optional[int] = Field(
        default=None, sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    author_id: Optional[int] = Field(default=None, foreign_key="author.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    author: Optional[Author] = Relationship(back_populates="books")
    category: Optional[Category] = Relationship(back_populates="books")
    borrows: list[BorrowRecord] = Relationship(back_populates="book")


class BookCreate(BookBase):
    author_id: Optional[int] = None
    category_id: Optional[int] = None


class BookRead(BookBase):
    id: int
    author_id: Optional[int]
    category_id: Optional[int]


class BorrowCreate(SQLModel):
    book_id: int
    user_id: int
    due_date: date


class ReturnBookRequest(SQLModel):
    user_id: int
    book_id: int


class BorrowRecordOut(SQLModel):
    id: int
    user_name: str
    book_title: str
    due_date: datetime
    returned_at: Optional[datetime]


class PaginatedResponse(SQLModel):
    page: int
    size: int
    total: int
    items: list[BorrowRecordOut]
