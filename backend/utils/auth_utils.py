import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from database import users_collection
from dotenv import load_dotenv
from utils.mongo import fix_mongo
# OAuth2 scheme (used to extract token from Authorization header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
load_dotenv()
# Environment variables (store these in .env)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "chatinsight_secret")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "chatinsight_refresh_secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


# -------------------- JWT CREATION --------------------
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# -------------------- VERIFY CURRENT USER --------------------
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub", "")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user = fix_mongo(user)
        user.pop("hashed_password", None)
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or invalid")