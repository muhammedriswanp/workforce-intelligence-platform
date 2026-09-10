from app.database import Base
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    experience: Mapped[int] = mapped_column(Integer, nullable=False)
    