from datetime import datetime, date
from typing import Optional


def parse_date_from_string(date_string: str) -> Optional[date]:
    """
    Parse a date string into a date object.
    
    Supports multiple date formats:
    - YYYY-MM-DD
    - MM/DD/YYYY
    - DD/MM/YYYY
    
    Args:
        date_string (str): Date string to parse
        
    Returns:
        Optional[date]: Parsed date or None if parsing fails
    """
    if not date_string:
        return None
    
    # Try different date formats
    date_formats = [
        "%Y-%m-%d",  # YYYY-MM-DD
        "%m/%d/%Y",  # MM/DD/YYYY
        "%d/%m/%Y",  # DD/MM/YYYY
        "%Y-%m-%dT%H:%M:%S",  # ISO datetime
        "%Y-%m-%d %H:%M:%S",   # YYYY-MM-DD HH:MM:SS
    ]
    
    for date_format in date_formats:
        try:
            return datetime.strptime(date_string, date_format).date()
        except ValueError:
            continue
    
    # If all formats fail, return None
    return None
