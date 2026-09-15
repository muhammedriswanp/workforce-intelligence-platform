from app.database import Base
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, ForeignKey, String, Float, Text, DateTime

if TYPE_CHECKING:
    from app.models.project  import Project

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    estimated_hours: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="todo", nullable=False)  # todo, in_progress, completed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="tasks")
