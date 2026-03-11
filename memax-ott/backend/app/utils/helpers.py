"""
Utility Helper Functions
Common utility functions used across the application
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import hashlib
import random
import string


def generate_random_string(length: int = 32) -> str:
    """Generate random string"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_hash(text: str) -> str:
    """Generate SHA256 hash"""
    return hashlib.sha256(text.encode()).hexdigest()


def format_duration(minutes: int) -> str:
    """
    Format duration in minutes to human-readable string
    
    Args:
        minutes: Duration in minutes
    
    Returns:
        Formatted string (e.g., "2h 30m")
    """
    if minutes < 60:
        return f"{minutes}m"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours}h"
    
    return f"{hours}h {mins}m"


def parse_duration(duration_str: str) -> int:
    """
    Parse duration string to minutes
    
    Args:
        duration_str: Duration string (e.g., "2h 30m", "150 min")
    
    Returns:
        Duration in minutes
    """
    if not duration_str:
        return 0
    
    duration_str = duration_str.lower().strip()
    total_minutes = 0
    
    # Handle "150 min" format
    if 'min' in duration_str and 'h' not in duration_str:
        try:
            return int(duration_str.split()[0])
        except:
            return 0
    
    # Handle "2h 30m" format
    if 'h' in duration_str:
        parts = duration_str.split('h')
        try:
            total_minutes += int(parts[0].strip()) * 60
        except:
            pass
        
        if len(parts) > 1 and 'm' in parts[1]:
            try:
                total_minutes += int(parts[1].replace('m', '').strip())
            except:
                pass
    
    return total_minutes


def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date"""
    today = datetime.utcnow()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def paginate(items: List[Any], page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Paginate a list of items
    
    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        page_size: Items per page
    
    Returns:
        Dict with paginated items and metadata
    """
    total = len(items)
    total_pages = (total + page_size - 1) // page_size
    
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        'items': items[start:end],
        'page': page,
        'page_size': page_size,
        'total': total,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters
    text = text.strip()
    
    return text


def get_time_ago(dt: datetime) -> str:
    """
    Get human-readable time ago string
    
    Args:
        dt: Datetime to compare
    
    Returns:
        String like "2 hours ago", "3 days ago"
    """
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"
