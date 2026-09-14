from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.skills.routes import router as skills_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(skills_router)
@app.get("/")
def root():
    return {"message": "Workforce Intelligence Platform API"}

