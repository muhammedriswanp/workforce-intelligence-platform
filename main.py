from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.skills.routes import router as skills_router
from app.employees.routes import router as employees_router
from app.projects.routes import router as projects_router
from app.tasks.routes import router as tasks_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(skills_router)
app.include_router(employees_router)
app.include_router(projects_router)
app.include_router(tasks_router)

@app.get("/")
def root():
    return {"message": "Workforce Intelligence Platform API"}

