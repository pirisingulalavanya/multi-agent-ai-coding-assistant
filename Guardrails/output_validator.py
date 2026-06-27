import re
from loguru import logger

SECRET_PATTERNS = [
    r"(sk-[a-zA-Z0-9]{20,})",
    r"(gsk_[a-zA-Z0-9]{40,})",
    r"(ghp_[a-zA-Z0-9]{36})",
    r"(AKIA[0-9A-Z]{16})",
    r"(password\s*=\s*['\"][^'\"]{4,}['\"])",
]

def validate_output(content: str) -> str:
    for pattern in SECRET_PATTERNS:
        content = re.sub(pattern, "[REDACTED]", content)
    return content

def is_safe_output(content: str) -> bool:
    dangerous = ["rm -rf", "format c:", "DROP TABLE", "DELETE FROM"]
    for d in dangerous:
        if d.lower() in content.lower():
            logger.warning(f"Dangerous content in output: {d}")
            return False
    return True