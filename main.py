from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.skills.routes import router as skills_router
from app.employees.routes import router as employees_router
from app.projects.routes import router as projects_router
from app.tasks.routes import router as tasks_router
from app.assignments.routes import router as assignments_router
from app.ai.routes import router as ai_router
from app.agent.routes import router as agent_router


app = FastAPI(title="Workforce Intelligence Platform")

app.include_router(auth_router)
app.include_router(skills_router)
app.include_router(employees_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(assignments_router)
app.include_router(ai_router)
app.include_router(agent_router)

@app.get("/")
def root():
    return {"message": "Workforce Intelligence Platform API"}

