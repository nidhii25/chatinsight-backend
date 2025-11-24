from fpdf import FPDF
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from collections import Counter


# ----------------------------------------------------------------------
# 🎨 Helper chart functions
# ----------------------------------------------------------------------

def plot_sentiment_pie(sentiments: dict):
    """Generate pie chart for sentiment distribution."""
    labels = list(sentiments.keys())
    values = list(sentiments.values())

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title("Sentiment Distribution", fontsize=10)
    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format="png")
    plt.close(fig)
    img.seek(0)
    return img


def plot_participant_bar(participants: dict):
    """Generate bar chart for participant message counts."""
    labels = list(participants.keys())
    values = list(participants.values())

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.barh(labels, values)
    ax.set_title("Messages per Participant", fontsize=10)
    ax.set_xlabel("Message Count")
    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format="png")
    plt.close(fig)
    img.seek(0)
    return img


def plot_emotion_bar(emotions: dict):
    """Generate bar chart for detected emotions (if available)."""
    if not emotions:
        return None

    labels = list(emotions.keys())
    values = list(emotions.values())

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(labels, values, color='skyblue')
    ax.set_title("Emotion Distribution", fontsize=10)
    ax.set_ylabel("Count")
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format="png")
    plt.close(fig)
    img.seek(0)
    return img


# ----------------------------------------------------------------------
# 🧾 PDF Generator
# ----------------------------------------------------------------------

def generate_pdf(report_doc: dict) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title Section
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, "ChatInsight Analysis Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", ln=True)
    pdf.cell(0, 10, f"Chat ID: {report_doc.get('chat_id', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Uploaded by: {report_doc.get('uploaded_by', 'N/A')}", ln=True)
    pdf.ln(10)

    # Summary Section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Meeting Summary:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, report_doc.get("summary", "No summary available."))
    pdf.ln(8)

    # Action Items Section
    action_items = report_doc.get("action_items", [])
    if action_items:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Action Items:", ln=True)
        pdf.set_font("Arial", "", 12)
        for i, item in enumerate(action_items, 1):
            pdf.multi_cell(0, 8, f"{i}. {item}")
        pdf.ln(8)

    # Analytics Overview Title
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Analytics Overview:", ln=True)
    pdf.ln(4)

    # Convert stats properly
    raw_sentiments = report_doc.get("sentiment_stats", [])
    sentiments = {s["_id"]: s["count"] for s in raw_sentiments} if isinstance(raw_sentiments, list) else raw_sentiments

    raw_participants = report_doc.get("speaker_stats", {})
    participants = {k: int(v) for k, v in raw_participants.items()}

    emotions = report_doc.get("emotions", {})

    # Sentiment Pie Chart
    if sentiments:
        img = plot_sentiment_pie(sentiments)
        pdf.image(img, x=20, w=160)
        pdf.ln(10)

    # Participant Activity Chart
    if participants:
        img = plot_participant_bar(participants)
        pdf.image(img, x=20, w=160)
        pdf.ln(10)

    # Emotion Chart
    if emotions:
        img = plot_emotion_bar(emotions)
        if img:
            pdf.image(img, x=20, w=160)
            pdf.ln(10)

    # Statistical Insights
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Statistical Insights:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Overall Productivity Score: {report_doc.get('productivity_score', 'N/A')}", ln=True)

    # Keywords
    top_keywords = report_doc.get("top_keywords", [])
    if top_keywords:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Top Keywords:", ln=True)
        pdf.set_font("Arial", "", 12)
        keywords_str = ", ".join([kw["keyword"] for kw in top_keywords if "keyword" in kw])
        pdf.multi_cell(0, 8, keywords_str)
        pdf.ln(8)

    # AI Insights
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "AI Insights:", ln=True)
    pdf.set_font("Arial", "", 12)

    top_speaker = (
    max(participants.items(), key=lambda x: x[1])[0]
    if participants else "N/A"
)

    dominant_sentiment = (
        max(sentiments.items(), key=lambda x: x[1])[0]
        if sentiments else "neutral"
    )


    insight_text = (
        f"The overall tone of this conversation was {dominant_sentiment}.\n"
        f"The most active participant was {top_speaker}.\n"
        f"The positivity score indicates a productivity level of {report_doc.get('productivity_score', 0)}%.\n"
    )

    pdf.multi_cell(0, 8, insight_text)

    # Return PDF bytes correctly
    pdf_bytes = pdf.output(dest="S")
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    return buffer



# ----------------------------------------------------------------------
# 📊 CSV Generator
# ----------------------------------------------------------------------

def generate_csv(report_doc: dict) -> BytesIO:
    """Export summary and stats as CSV."""
    output = BytesIO()

    # Flatten data for CSV export
    summary_data = {
        "chat_id": report_doc.get("chat_id"),
        "uploaded_by": report_doc.get("uploaded_by"),
        "productivity_score": report_doc.get("productivity_score"),
        "summary": report_doc.get("summary")
    }

    df_summary = pd.DataFrame([summary_data])

    # Create multiple sheets-like CSV (append sections)
    df_summary.to_csv(output, index=False)
    output.write(b"\n\nSpeaker Stats\n")
    pd.DataFrame.from_dict(report_doc.get("speaker_stats", {}), orient="index", columns=["message_count"]).to_csv(output)
    output.write(b"\n\nSentiment Stats\n")
    pd.DataFrame.from_dict(report_doc.get("sentiment_stats", {}), orient="index", columns=["count"]).to_csv(output)
    output.write(b"\n\nTop Keywords\n")
    pd.DataFrame(report_doc.get("top_keywords", []), columns=["keyword"]).to_csv(output, index=False)

    output.seek(0)
    return output
