from app.database import Base
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, ForeignKey, Text, DateTime


class SprintUpdate(Base):
    __tablename__ = "sprint_updates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    update_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)