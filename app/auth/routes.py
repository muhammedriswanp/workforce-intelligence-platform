from fastapi import APIRouter
from app.schemas import UserCreate, UserLogin
from app.password_utils import hash_password, verify_password
from app.models.user import User
from app.database import SessionLocal
from sqlalchemy import select
from app.jwt_utils import create_access_token
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.dependencies import get_current_user, get_current_manager
from fastapi import HTTPException, status

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
def register(user: UserCreate):

    db = SessionLocal()

    hashed_password = hash_password(user.password)
    new_user = User(
        name = user.name,
        email = user.email,
        password_hash = hashed_password,
        role = user.role,
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    return {
    "message": "User registered successfully",
    "user_id": new_user.id,
    "name": new_user.name,
    "email": new_user.email,
    "role": new_user.role,
}

@router.post("/login")
def login(user: OAuth2PasswordRequestForm = Depends()):

    db = SessionLocal()

    statement = select(User).where(User.email == user.username)

    result = db.execute(statement)

    db_user = result.scalar_one_or_none()

    # If user doesn't exist OR password doesn't match, reject with 401
    if db_user is None or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        user_id=db_user.id,
        role=db_user.role,
    )

    return {
    "message": "Login successful",
    "access_token": access_token,
}

@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": current_user,
    }

@router.get("/manager-only")
def manager_dashboard(current_user=Depends(get_current_manager)):
    return {
        "message": "Welcome to the manager dashboard",
        "user": current_user,
    }