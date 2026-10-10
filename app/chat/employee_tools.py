from langchain_core.tools import tool
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Assignment, Task, Project
from app.rag.retriever import retrieve_relevant_policies


def build_employee_tools(employee_id: int):
    """Build the tools for ONE employee.
    employee_id comes from the login (set by the backend), never from the AI."""

    @tool
    def get_my_tasks() -> str:
        """List my own active tasks with their project, status and allocated hours."""
        with SessionLocal() as db:
            rows = db.execute(
                select(Assignment, Task, Project)
                .join(Task, Assignment.task_id == Task.id)
                .join(Project, Task.project_id == Project.id)
                .where(
                    Assignment.employee_id == employee_id,
                    Assignment.status == "active",
                )
            ).all()

        if not rows:
            return "You have no active tasks."

        return "\n".join(
            f"- Task #{t.id} '{t.title}' | project #{p.id} '{p.title}' | "
            f"task status: {t.status} | allocated: {a.allocated_hours}h"
            for a, t, p in rows
        )

    @tool
    def search_policies(query: str) -> str:
        """Search company policies, role guidelines and project standards."""
        results = retrieve_relevant_policies(query, k=3)
        if not results:
            return "No matching policy found."
        return "\n".join(f"- {text.lstrip('- ').strip()}" for text in results)

    @tool
    def get_project_details(project_id: int) -> str:
        """Read-only details of a project and its tasks."""
        with SessionLocal() as db:
            project = db.get(Project, project_id)
            if not project:
                return "Project not found."
            tasks = db.execute(
                select(Task).where(Task.project_id == project_id)
            ).scalars().all()

        lines = [
            f"Project #{project.id} '{project.title}' (status: {project.status})",
            f"Description: {project.description or '-'}",
            "Tasks:",
        ]
        lines += [
            f"- #{t.id} '{t.title}' | {t.estimated_hours}h | {t.status}"
            for t in tasks
        ] or ["- (no tasks yet)"]
        return "\n".join(lines)

    return [get_my_tasks, search_policies, get_project_details]