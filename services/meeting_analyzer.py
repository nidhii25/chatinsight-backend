from services.nlp import analyze_sentiment, detect_emotions, keyword_extract, advanced_summary, extract_action_items

def analyze_meeting(messages):
    """Runs full analytics pipeline on meeting messages"""

    all_texts = [m["text"] for m in messages]

    # Sentiment (overall)
    combined_text = " ".join(all_texts)
    sentiment = analyze_sentiment(combined_text)

    # Emotions (per message)
    emotions_raw = detect_emotions(messages)
    emotion_count = {}

    for e in emotions_raw:
        lbl = e["emotion"]
        emotion_count[lbl] = emotion_count.get(lbl, 0) + 1

    # Keywords
    keywords = keyword_extract(all_texts)

    # Summary
    summary = advanced_summary(all_texts)

    # Action items
    actions = extract_action_items(messages)

    return {
        "overall_sentiment": sentiment,
        "emotion_distribution": emotion_count,
        "keywords": keywords,
        "summary": summary,
        "action_items": actions,
        "message_count": len(messages)
    }
