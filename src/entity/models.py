from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    number: Mapped[str] = mapped_column(String(20))
    birthday: Mapped[str] = mapped_column(Date())
    description: Mapped[str] = mapped_column(Text(250))
