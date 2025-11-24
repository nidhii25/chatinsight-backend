from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from utils.auth_utils import get_current_user
from services.parser import parse_whatsapp_chat
from database import db
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/chats", tags=["Chats"])

@router.post("/upload")
async def upload_chat(file: UploadFile = File(...), curr_user: dict = Depends(get_current_user)):
    # Read file once
    raw_bytes = await file.read()

    # Decode safely
    content_text = raw_bytes.decode("utf-8", errors="ignore").replace("\r", "")
    lines = content_text.split("\n")

    # 🔍 Debug print first 10 lines
    print("\n📄--- File Preview ---")
    for line in lines[:10]:
        print(line)
    print("📄--- End Preview ---\n")

    # Normalize en-dash and em-dash to hyphen for regex
    lines = [line.replace("–", "-").replace("—", "-") for line in lines]

    messages = parse_whatsapp_chat(lines)

    if not messages:
        raise HTTPException(status_code=400, detail="No valid messages found in file")

    chat_doc = {
        "title": file.filename,
        "source": "whatsapp",
        "uploaded_by": curr_user["email"],
        "participants": list(set([m["sender"] for m in messages])),
        "start_time": messages[0]["timestamp"],
        "end_time": messages[-1]["timestamp"],
        "created_at": datetime.utcnow(),
    }
    chat_id = db.chats.insert_one(chat_doc).inserted_id

    for msg in messages:
        msg["chat_id"] = chat_id
    db.messages.insert_many(messages)

    return {
        "chat_id": str(chat_id),
        "participants": chat_doc["participants"],
        "message_count": len(messages),
        "message": "Chat uploaded and parsed successfully",
    }

@router.delete("/{chat_id}")
async def delete_chat(chat_id: str, curr_user: dict = Depends(get_current_user)):
    chat = db.chats.find_one({"_id": ObjectId(chat_id), "uploaded_by": curr_user["email"]})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found or unauthorized")

    db.messages.delete_many({"chat_id": ObjectId(chat_id)})
    db.chats.delete_one({"_id": ObjectId(chat_id)})
    return {"message": f"Chat {chat_id} deleted successfully"}
