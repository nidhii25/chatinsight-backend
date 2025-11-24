from collections import Counter
from textblob import TextBlob
from typing import List, Dict
from datetime import datetime

# Import advanced NLP functions
from services.nlp import (
    detect_emotions,
    extract_action_items,
    advanced_summary,
    keyword_extract
)

def compute_analytics(messages: List[Dict]) -> Dict:
    """
    Performs advanced analytics on a list of chat/meeting messages.
    Each message is a dict with keys: sender, text, timestamp.
    """

    # --- 1️⃣ Basic counts ---
    message_count = len(messages)
    participants = [m.get("sender", "Unknown") for m in messages]
    speaker_stats: Dict[str, int] = dict(Counter(participants))
    top_participant = (max(speaker_stats, key=speaker_stats.get) if speaker_stats else "Unknown") #type: ignore[arg-type]

    # --- 2️⃣ Sentiment Analysis ---
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    sentiment_labels = []  # for later correlation
    for m in messages:
        text = m.get("text", "")
        if not text or not text.strip():
            sentiment_labels.append("neutral")
            continue
        polarity = TextBlob(text).sentiment.polarity  # type: ignore[attr-defined]
        if polarity > 0.2:
            sentiments["positive"] += 1
            sentiment_labels.append("positive")
        elif polarity < -0.2:
            sentiments["negative"] += 1
            sentiment_labels.append("negative")
        else:
            sentiments["neutral"] += 1
            sentiment_labels.append("neutral")

    # --- 3️⃣ Emotion Detection (AI-powered) ---
    emotion_results = detect_emotions(messages)
    emotion_stats = dict(Counter([e["emotion"] for e in emotion_results]))

    # --- 4️⃣ Keyword Extraction (smart version) ---
    all_texts = [m.get("text", "") for m in messages if m.get("text", "").strip()]
    top_keywords = keyword_extract(all_texts)

    # --- 5️⃣ Action Item Extraction ---
    action_items = extract_action_items(messages)

    # --- 6️⃣ AI Summary (Optional, GPT-assisted) ---
    summary = advanced_summary(all_texts)

    # --- 7️⃣ Productivity Score ---
    # Heuristic: balanced participation + positive tone + fewer negatives
    total_msgs = sum(sentiments.values())
    pos_ratio = sentiments["positive"] / total_msgs if total_msgs else 0
    neg_ratio = sentiments["negative"] / total_msgs if total_msgs else 0
    balance = 1 - abs(max(speaker_stats.values(), default=1) - min(speaker_stats.values(), default=1)) / max(speaker_stats.values(), default=1)
    productivity_score = round((pos_ratio * 50 + balance * 30 + (1 - neg_ratio) * 20), 2)

    # --- 8️⃣ Return Complete Analytics Report ---
    return {
        "message_count": message_count,
        "speaker_stats": speaker_stats,
        "top_participant": top_participant,
        "sentiment_stats": sentiments,
        "emotion_stats": emotion_stats,
        "top_keywords": top_keywords,
        "action_items": action_items,
        "summary": summary,
        "productivity_score": productivity_score,
        "generated_on": datetime.utcnow().isoformat()
    }
