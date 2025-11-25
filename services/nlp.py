from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
from datetime import datetime
import re
import os
from openai import OpenAI

# -----------------------------
# SAFE IMPORT HANDLING
# -----------------------------
# Heavy transformer models cannot load on Render free tier.
# So we try importing pipeline safely.
try:
    from transformers import pipeline
except ImportError:
    pipeline = None  # prevents crashes on Render

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

analyzer = SentimentIntensityAnalyzer()

# -----------------------------------------
# SAFE EMOTION MODEL LOADING (LOCAL ONLY)
# -----------------------------------------
LOCAL_EMOTION_MODEL = "./emotion-english-distilroberta-base"

emotion_analyzer = None

if pipeline is not None and os.path.exists(LOCAL_EMOTION_MODEL):
    try:
        emotion_analyzer = pipeline(
            "text-classification",
            model=LOCAL_EMOTION_MODEL,
            tokenizer=LOCAL_EMOTION_MODEL
        )
        print("✔ Emotion model loaded locally.")
    except Exception as e:
        print("❌ Failed to load local emotion model:", e)
else:
    print("⚠ Emotion model unavailable or folder missing. Using fallback.")


# -------------------------------------------------------
# EMOTION DETECTION (graceful fallback for Render)
# -------------------------------------------------------
def detect_emotions(messages):
    if not emotion_analyzer:
        # No crash — return empty list if model not available
        return []

    emotions = []
    for msg in messages:
        try:
            text = msg.get("text", "")[:512]
            result = emotion_analyzer(text)[0]
            emotions.append({
                "text": msg["text"],
                "emotion": result["label"],
                "score": result["score"]
            })
        except:
            continue
    return emotions


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
# ADVANCED SUMMARY (OpenAI)
# -------------------------------------------------------
def advanced_summary(texts: list[str]) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # use your preferred model
            messages=[{"role": "user", "content": "Summarize this meeting:\n\n" + ''.join(texts)}],
            temperature=0.3
        )
        content = str(getattr(response.choices[0].message, "content", "")).strip()
        return content or "Summary not generated."
    except Exception as e:
        print(f"⚠️ OpenAI API failed: {e}")
        return "Summary unavailable. Key points:\n" + "\n".join(texts[:5])


# -------------------------------------------------------
# ACTION ITEMS
# -------------------------------------------------------
def extract_action_items(messages):
    pattern = re.compile(
        r"\b(need to|should|let's|will|plan to|decide|assign|do this|send|complete)\b",
        re.IGNORECASE
    )
    action_items = [msg["text"] for msg in messages if pattern.search(msg["text"])]
    return action_items[:10]
