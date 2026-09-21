import os 
import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def create_access_token(user_id: int, role: str, name: str = "", email: str = "") -> str:
    #payload is the information we want to put inside the JWT
    payload = {
        "user_id": user_id,
        "role": role,
        "name": name,
        "email": email,
    }
    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm="HS256"
    )

    return token