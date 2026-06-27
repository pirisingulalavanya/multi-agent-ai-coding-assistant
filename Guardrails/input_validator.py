import re
from loguru import logger

BLOCKED_PATTERNS = [
    r"(rm\s+-rf|del\s+/f|format\s+c:)",
    r"(drop\s+table|delete\s+from|truncate\s+table)",
    r"(hack|exploit|malware|virus|ransomware|phishing)",
    r"(credit.?card|social.?security|bank.?account)",
    r"(password\s*=\s*['\"][^'\"]{4,})",
]

BLOCKED_KEYWORDS = [
    "bomb", "weapon", "illegal", "crack", "piracy"
]

def validate_input(message: str) -> tuple[bool, str]:
    if not message or not message.strip():
        return False, "Empty message not allowed"

    if len(message) > 5000:
        return False, "Message too long. Maximum 5000 characters allowed"

    message_lower = message.lower()
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            logger.warning(f"Blocked pattern detected: {pattern}")
            return False, "Request blocked by safety filter. Please rephrase your request"

    for keyword in BLOCKED_KEYWORDS:
        if keyword in message_lower:
            logger.warning(f"Blocked keyword detected: {keyword}")
            return False, f"Request contains restricted content"

    return True, "OK"

def sanitize_input(message: str) -> str:
    message = message.strip()
    message = re.sub(r'<[^>]+>', '', message)
    message = re.sub(r'\s+', ' ', message)
    return message