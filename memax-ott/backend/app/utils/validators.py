"""
Validators
Input validation functions
"""
from typing import Optional
import re
from email_validator import validate_email as email_validate, EmailNotValidError


def validate_email(email: str) -> bool:
    """
    Validate email address
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid
    """
    try:
        email_validate(email)
        return True
    except:
        # Fallback to regex if email_validator not installed
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    
    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate username
    
    Args:
        username: Username to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, None


def validate_rating(rating: float) -> bool:
    """
    Validate rating value
    
    Args:
        rating: Rating value
    
    Returns:
        True if valid (0-10)
    """
    return 0 <= rating <= 10


def validate_year(year: int) -> bool:
    """
    Validate release year
    
    Args:
        year: Year value
    
    Returns:
        True if valid (1900-2030)
    """
    return 1900 <= year <= 2030


def sanitize_input(text: str) -> str:
    """
    Sanitize user input
    
    Args:
        text: Input text
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script tags
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
    
    # Trim whitespace
    text = text.strip()
    
    return text
