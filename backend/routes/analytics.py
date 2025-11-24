from services.nlp import analyze_sentiment, keyword_extract, advanced_summary, extract_action_items, detect_emotions
from datetime import datetime
from bson import ObjectId
from utils.auth_utils import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from database import db
from collections import Counter

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/{chat_id}")
async def get_chat_analytics(chat_id: str, curr_user: dict = Depends(get_current_user)):
    chat = db.chats.find_one({"_id": ObjectId(chat_id), "uploaded_by": curr_user["email"]})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found or unauthorized")

    messages = list(db.messages.find({"chat_id": ObjectId(chat_id)}))
    if not messages:
        raise HTTPException(status_code=404, detail="No messages for this chat")

    # Tag sentiments if not done
    for msg in messages:
        if "sentiment" not in msg:
            msg["sentiment"] = analyze_sentiment(msg["text"])
            db.messages.update_one({"_id": msg["_id"]}, {"$set": {"sentiment": msg["sentiment"]}})

    # Aggregations
    participant_stats = list(
        db.messages.aggregate([
            {"$match": {"chat_id": ObjectId(chat_id)}},
            {"$group": {"_id": "$sender", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
    )
    sentiment_stats = list(
        db.messages.aggregate([
            {"$match": {"chat_id": ObjectId(chat_id)}},
            {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
        ])
    )

    sentiment_map = {s["_id"]: s["count"] for s in sentiment_stats}
    total_msgs = sum(sentiment_map.values())
    positive_ratio = sentiment_map.get("positive", 0) / total_msgs if total_msgs else 0
    productivity_score = round(50 + positive_ratio * 50, 2)

    # New NLP Features
    all_texts = [m["text"] for m in messages if m["text"].strip()]
    top_keywords = keyword_extract(all_texts)
    summary = advanced_summary(all_texts)
    action_items = extract_action_items(messages)
    emotions = detect_emotions(messages)
    emotion_counts = {k: v for k, v in Counter([e["emotion"] for e in emotions]).items()}

    # Save Report
    report_doc = {
        "chat_id": ObjectId(chat_id),
        "uploaded_by": curr_user["email"],
        "summary": summary,
        "action_items": action_items,
        "top_keywords": top_keywords,
        "speaker_stats": {p["_id"]: p["count"] for p in participant_stats},
        "sentiment_stats": sentiment_map,
        "emotions": emotion_counts,
        "productivity_score": productivity_score,
        "created_on": datetime.utcnow()
    }

    db.analysis_reports.insert_one(report_doc)

    return {
        "participants": participant_stats,
        "sentiments": sentiment_stats,
        "emotions": emotion_counts,
        "action_items": action_items,
        "keywords": top_keywords,
        "summary": summary,
        "productivity_score": productivity_score
    }
