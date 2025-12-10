import re
from datetime import datetime

WHATSAPP_REGEX = re.compile(
    r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?:\s?[APMapm]{2})?)\s*-\s*(.*)$"
)

def parse_whatsapp_chat(lines):
    messages = []
    current_message = None

    for line in lines:
        line = line.strip()

        match = WHATSAPP_REGEX.match(line)
        if match:
            date_str, time_str, rest = match.groups()

            # System messages (no sender)
            if ":" in rest:
                sender, text = rest.split(":", 1)
                sender = sender.strip()
                text = text.strip()
            else:
                sender = "System"
                text = rest.strip()

            # Convert timestamp safely
            timestamp = None
            for fmt in ["%d/%m/%y %I:%M %p", "%d/%m/%Y %I:%M %p", "%d/%m/%y %H:%M", "%d/%m/%Y %H:%M"]:
                try:
                    timestamp = datetime.strptime(f"{date_str} {time_str}", fmt)
                    break
                except:
                    pass

            # Save previous multi-line message
            if current_message:
                messages.append(current_message)

            current_message = {
                "timestamp": timestamp,
                "sender": sender,
                "text": text
            }

        else:
            # Line doesn’t start with date → continuation of previous message
            if current_message:
                current_message["text"] += " " + line

    # last message
    if current_message:
        messages.append(current_message)

    return messages
