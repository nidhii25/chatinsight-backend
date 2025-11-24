from fastapi import APIRouter, HTTPException, Depends, Body, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from bson import ObjectId
import bcrypt
from utils.mongo import fix_mongo
from models.user import UserCreate, UserLogin
from database import users_collection
from utils.auth_utils import create_access_token, create_refresh_token, get_current_user
from database import db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# -------------------- Password Utilities --------------------
async def password_strength(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    return True


async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


# -------------------- Register --------------------
@router.post("/register")
async def register(user: UserCreate):
    """Register new user with hashed password."""
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    if not await password_strength(user.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters and include upper, lower, and digit",
        )

    hashed_password = await hash_password(user.password)
    user_dict = {
        "_id": ObjectId(),
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    users_collection.insert_one(user_dict)
    return {"message": "User registered successfully"}


# -------------------- Login (OAuth2 Form) --------------------
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user using OAuth2PasswordRequestForm (username=email)."""
    user_dict = users_collection.find_one({"email": form_data.username})
    if not user_dict:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not bcrypt.checkpw(
        form_data.password.encode("utf-8"), user_dict["hashed_password"].encode("utf-8")
    ):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user_dict["email"]}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_refresh_token(
        data={"sub": user_dict["email"]}, expires_delta=refresh_token_expires
    )

    users_collection.update_one(
        {"email": user_dict["email"]}, {"$set": {"refresh_token": refresh_token}}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# -------------------- Current User --------------------
@router.get("/me")
async def get_me(curr_user: dict = Depends(get_current_user)):
    return {"user": curr_user}



# -------------------- Refresh Token --------------------
@router.post("/refresh_token")
async def refresh_token(refresh_token: str = Body(...)):
    from jose import JWTError, jwt
    from utils.auth_utils import SECRET_KEY, REFRESH_SECRET_KEY, ALGORITHM

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = users_collection.find_one({"email": email, "refresh_token": refresh_token})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token_expires = timedelta(minutes=30)
    new_access_token = create_access_token(data={"sub": email}, expires_delta=access_token_expires)
    refresh_token_expires = timedelta(days=7)
    new_refresh_token = create_refresh_token(data={"sub": email}, expires_delta=refresh_token_expires)

    users_collection.update_one(
        {"email": email}, {"$set": {"refresh_token": new_refresh_token}}
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


# -------------------- Logout --------------------
@router.post("/logout")
async def logout(curr_user: dict = Depends(get_current_user)):

    email = curr_user["email"]

    # 1️⃣ Remove refresh token (your original behavior)
    users_collection.update_one(
        {"email": email},
        {"$unset": {"refresh_token": ""}}
    )

    # 2️⃣ Find all chats uploaded by the user
    chats = list(db.chats.find({"uploaded_by": email}, {"_id": 1}))
    chat_ids = [c["_id"] for c in chats]

    # 3️⃣ Delete messages belonging to these chats
    if chat_ids:
        db.messages.delete_many({"chat_id": {"$in": chat_ids}})

    # 4️⃣ Delete the chats themselves
        db.chats.delete_many({"_id": {"$in": chat_ids}})

    return {
        "message": "Logged out successfully. All chats and messages were deleted."
    }

