from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from utils.auth_utils import get_current_user
from database import db
from datetime import datetime, timedelta
from services.meeting_analyzer import analyze_meeting
from services.report_gen import generate_pdf, generate_csv

router = APIRouter(prefix="/api/meetings", tags=["Live Meetings"])


def maybe_trigger_analysis(meeting_id: str):
    """Runs analysis only if last run >30 seconds ago."""
    record = db.meeting_analytics.find_one({"meeting_id": meeting_id})
    now = datetime.utcnow()

    if not record or (now - record["last_analyzed_at"]) > timedelta(seconds=30):
        messages = list(db.messages.find({"meeting_id": meeting_id}, {"_id": 0}))
        results = analyze_meeting(messages)

        db.meeting_analytics.update_one(
            {"meeting_id": meeting_id},
            {
                "$set": {
                    "analytics": results,
                    "last_analyzed_at": now
                }
            },
            upsert=True
        )



@router.post("/live")
async def live_meeting_capture(payload: dict, background: BackgroundTasks, curr_user: dict = Depends(get_current_user)):
    if not payload.get("meeting_id") or not payload.get("text"):
        raise HTTPException(status_code=400, detail="Missing meeting_id or text")

    doc = {
        "meeting_id": payload["meeting_id"],
        "sender": payload.get("sender", "Unknown"),
        "text": payload["text"],
        "timestamp": payload.get("timestamp", datetime.utcnow()),
        "uploaded_by": curr_user["email"],
        "created_at": datetime.utcnow()
    }

    db.messages.insert_one(doc)

    # Background analysis
    background.add_task(maybe_trigger_analysis, payload["meeting_id"])

    return {"status": "captured", "analysis": "queued"}



@router.get("/list")
async def list_meetings(curr_user: dict = Depends(get_current_user)):
    meetings = db.messages.aggregate([
        {"$group": {"_id": "$meeting_id", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ])
    return [{"meeting_id": m["_id"], "messages": m["count"]} for m in meetings]



@router.get("/{meeting_id}")
async def get_meeting_messages(meeting_id: str, curr_user: dict = Depends(get_current_user)):
    msgs = list(db.messages.find({"meeting_id": meeting_id}, {"_id": 0}))
    return {"meeting_id": meeting_id, "messages": msgs}



@router.post("/{meeting_id}/analyze")
async def run_analysis(meeting_id: str, curr_user: dict = Depends(get_current_user)):
    messages = list(db.messages.find({"meeting_id": meeting_id}, {"_id": 0}))
    if not messages:
        raise HTTPException(status_code=404, detail="No messages for this meeting")

    results = analyze_meeting(messages)

    db.meeting_analytics.update_one(
        {"meeting_id": meeting_id},
        {"$set": {"analytics": results, "last_analyzed_at": datetime.utcnow()}},
        upsert=True
    )

    return {"meeting_id": meeting_id, "analytics": results, "forced": True}



@router.get("/{meeting_id}/analytics")
async def fetch_analytics(meeting_id: str, background: BackgroundTasks, curr_user: dict = Depends(get_current_user)):
    record = db.meeting_analytics.find_one({"meeting_id": meeting_id}, {"_id": 0})

    if not record:
        background.add_task(maybe_trigger_analysis, meeting_id)
        return {"status": "processing", "message": "Analytics being generated..."}

    return record["analytics"]



@router.get("/{meeting_id}/report/download")
async def download_meeting_report(meeting_id: str, format: str = "pdf", curr_user: dict = Depends(get_current_user)):
    analytics = db.meeting_analytics.find_one({"meeting_id": meeting_id}, {"_id": 0})

    if not analytics:
        raise HTTPException(status_code=404, detail="No analytics found. Run /analyze first.")

    report_data = {
        "title": f"Meeting Report: {meeting_id}",
        "summary": analytics.get("summary", ""),
        "keywords": analytics.get("keywords", []),
        "emotion_distribution": analytics.get("emotion_distribution", {}),
        "action_items": analytics.get("action_items", []),
        "overall_sentiment": analytics.get("overall_sentiment", ""),
        "message_count": analytics.get("message_count", 0)
    }

    if format == "pdf":
        pdf_bytes = generate_pdf(report_data)
        return Response(
            content=pdf_bytes.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=meeting_{meeting_id}.pdf"}
        )
    
    elif format == "csv":
        csv_bytes = generate_csv(report_data)
        return Response(
            content=csv_bytes.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=meeting_{meeting_id}.csv"}
        )

    raise HTTPException(status_code=400, detail="Invalid format")
