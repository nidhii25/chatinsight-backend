from fastapi import APIRouter, HTTPException, Response, Depends
from database import db
from utils.auth_utils import get_current_user
from bson import ObjectId
from services.report_gen import generate_pdf, generate_csv
from datetime import datetime
router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/{chat_id}/generate")
async def generate_report(chat_id: str, curr_user: dict = Depends(get_current_user)):
    chat = db.chats.find_one({"_id": ObjectId(chat_id)})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = list(db.messages.find({"chat_id": ObjectId(chat_id)}))
    if not messages:
        raise HTTPException(status_code=404, detail="No messages for this chat")

    # Run analytics pipeline
    from services.analytics import compute_analytics
    analytics_data = compute_analytics(messages)

    # Summarize
    summary_text = f"This chat has {analytics_data['message_count']} messages. " \
                   f"The most active participant is {analytics_data['top_participant']}."

    report_doc = {
        "chat_id": ObjectId(chat_id),
        "summary": summary_text,
        "productivity_score": analytics_data.get("productivity_score", 85),
        "top_keywords": analytics_data.get("top_keywords", []),
        "speaker_stats": analytics_data.get("speaker_stats", {}),
        "created_on": datetime.utcnow()
    }

    result = db.analysis_reports.insert_one(report_doc)

    return {
        "report_id": str(result.inserted_id),
        "message": "Report generated successfully",
        "summary": summary_text
    }


@router.get("/{report_id}")
async def get_report(report_id: str, curr_user: dict = Depends(get_current_user)):
    report_doc = db.analysis_reports.find_one({"_id": ObjectId(report_id)})
    if not report_doc:
        raise HTTPException(status_code=404, detail="Report not found")

    report_doc["_id"] = str(report_doc["_id"])
    if isinstance(report_doc.get("chat_id"), ObjectId):
        report_doc["chat_id"] = str(report_doc["chat_id"])
    return report_doc


@router.get("/{report_id}/download")
async def download_report(report_id: str, format: str = "pdf", curr_user: dict = Depends(get_current_user)):
    from bson.errors import InvalidId

    report_id = report_id.strip('"').strip("'")

    try:
        report_doc = db.analysis_reports.find_one({"_id": ObjectId(report_id)})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid report ID format")

    if not report_doc:
        raise HTTPException(status_code=404, detail="Report not found")

    # Convert ObjectIds to strings
    report_doc["_id"] = str(report_doc["_id"])
    if isinstance(report_doc.get("chat_id"), ObjectId):
        report_doc["chat_id"] = str(report_doc["chat_id"])

    # Generate PDF or CSV
    if format == "pdf":
        pdf_bytes = generate_pdf(report_doc)
        headers = {"Content-Disposition": f"attachment; filename=chat_report_{report_id}.pdf"}
        return Response(content=pdf_bytes.getvalue(), media_type="application/pdf", headers=headers)

    elif format == "csv":
        csv_bytes = generate_csv(report_doc)
        headers = {"Content-Disposition": f"attachment; filename=chat_report_{report_id}.csv"}
        return Response(content=csv_bytes.getvalue(), media_type="text/csv", headers=headers)

    raise HTTPException(status_code=400, detail="Invalid format. Use ?format=pdf or ?format=csv.")
