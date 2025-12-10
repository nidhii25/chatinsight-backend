from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
from datetime import datetime
import re
import os

# -------------------------------------------------------
# SENTIMENT ANALYZER
# -------------------------------------------------------
analyzer = SentimentIntensityAnalyzer()


# -------------------------------------------------------
# BASIC SENTIMENT
# -------------------------------------------------------
def analyze_sentiment(text: str) -> str:
    score = analyzer.polarity_scores(text)["compound"]
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    return "neutral"


# -------------------------------------------------------
# KEYWORD EXTRACTION
# -------------------------------------------------------
def keyword_extract(texts):
    words = re.findall(r"\b[a-zA-Z]{4,}\b", " ".join(texts).lower())
    stopwords = {"this", "that", "with", "from", "have", "your", "there", "they", "will", "about"}
    words = [w for w in words if w not in stopwords]
    common = Counter(words).most_common(10)
    return [{"keyword": k, "count": v} for k, v in common]


# -------------------------------------------------------
# ACTION ITEMS
# -------------------------------------------------------
def extract_action_items(messages):
    pattern = re.compile(
        r"\b(need to|should|let's|will|plan to|decide|assign|do this|send|complete)\b",
        re.IGNORECASE
    )
    return [msg["text"] for msg in messages if pattern.search(msg["text"])]


# -------------------------------------------------------
# MANUAL SUMMARY (NO API)
# -------------------------------------------------------
def advanced_summary(texts: list[str]) -> str:
    """
    Creates a structured summary WITHOUT using AI.
    Uses simple heuristics:
    - Most common topics (keywords)
    - Most positive/negative messages
    - Conversation tone
    - Start/end highlights
    """

    if not texts:
        return "No content to summarize."

    # 1) Get key topics
    keywords = keyword_extract(texts)
    top_topics = [k['keyword'] for k in keywords[:5]]

    # 2) Find emotional extremes
    positive_msgs = []
    negative_msgs = []

    for t in texts:
        score = analyzer.polarity_scores(t)["compound"]
        if score >= 0.4:
            positive_msgs.append(t)
        elif score <= -0.4:
            negative_msgs.append(t)

    # 3) Conversation tone
    avg_sent = sum(analyzer.polarity_scores(t)["compound"] for t in texts) / len(texts)
    if avg_sent > 0.2:
        tone = "Mostly positive and supportive."
    elif avg_sent < -0.2:
        tone = "Mostly negative, tense, or emotional."
    else:
        tone = "Neutral or mixed tone."

    # 4) Start + End highlight
    start = texts[0][:120] + "..." if len(texts[0]) > 120 else texts[0]
    end = texts[-1][:120] + "..." if len(texts[-1]) > 120 else texts[-1]

    # 5) Build summary
    summary = [
        "📌 Conversation Summary (Local Analysis)",
        "",
        f"Overall Tone: {tone}",
        "",
        "🔍 Main Topics Discussed:",
        ", ".join(top_topics) if top_topics else "Not enough data",
        "",
        "😊 Positive Moments:",
    ]

    if positive_msgs:
        summary.append(f"- Example: {positive_msgs[0][:120]}...")
    else:
        summary.append("- No strong positive messages detected.")

    summary.append("")
    summary.append("😞 Negative / Emotional Moments:")

    if negative_msgs:
        summary.append(f"- Example: {negative_msgs[0][:120]}...")
    else:
        summary.append("- No strong negative messages detected.")

    summary.append("")
    summary.append("🕒 Conversation Start:")
    summary.append(f"- {start}")

    summary.append("")
    summary.append("🕛 Conversation End:")
    summary.append(f"- {end}")

    return "\n".join(summary)
