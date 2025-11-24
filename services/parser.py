import re
from datetime import datetime

# Matches lines like: "11/03/25, 09:13 - Nidhi Agrawal: Hi"
WHATSAPP_REGEX = re.compile(
    r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.*)$"
)

def parse_whatsapp_chat(lines):
    messages = []
    current_message = None

    for line in lines:
        line = line.strip()

        # Match a new message
        match = WHATSAPP_REGEX.match(line)
        if match:
            # Save previous message if any
            if current_message:
                messages.append(current_message)

            date_str, time_str, sender, text = match.groups()
            try:
                # Try parsing 2-digit year first, fallback to 4-digit
                try:
                    timestamp = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%y %H:%M")
                except ValueError:
                    timestamp = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            except ValueError:
                timestamp = None

            current_message = {
                "timestamp": timestamp,
                "sender": sender.strip(),
                "text": text.strip()
            }
        elif current_message:
            # Continuation of previous message (multi-line)
            current_message["text"] += " " + line.strip()

    # Append the last message
    if current_message:
        messages.append(current_message)

    return messages
