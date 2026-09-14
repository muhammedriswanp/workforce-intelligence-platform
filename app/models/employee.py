from app.database import Base
from sqlalchemy import String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.skill import Skill
    from app.models.user import User


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency_level: Mapped[str] = mapped_column(String(50), nullable=False)  # Beginner, Intermediate, Advanced

    employee: Mapped["Employee"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(back_populates="employees")

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    designation: Mapped[str] = mapped_column(String(100), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weekly_capacity: Mapped[float] = mapped_column(Float, default=40.0, nullable=False)
    current_workload: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    skills: Mapped[list["EmployeeSkill"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    