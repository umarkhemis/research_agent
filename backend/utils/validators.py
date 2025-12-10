
from typing import Any, Dict, List
import re
from utils.error_handler import ValidationError, logger


def validate_query(query: str) -> str:
    """
    Validate and clean search query
    
    Args:
        query: Search query string
        
    Returns:
        Cleaned query string
        
    Raises:
        ValidationError: If query is invalid
    """
    if not query or not isinstance(query, str):
        raise ValidationError("Query must be a non-empty string")
    
    query = query.strip()
    
    if len(query) < 3:
        raise ValidationError("Query must be at least 3 characters long")
    
    if len(query) > 500:
        raise ValidationError("Query must be less than 500 characters")
    
    return query


def validate_limit(limit: int, max_limit: int = 50) -> int:
    """
    Validate paper limit
    
    Args:
        limit: Number of papers requested
        max_limit: Maximum allowed limit
        
    Returns:
        Validated limit
        
    Raises:
        ValidationError: If limit is invalid
    """
    if not isinstance(limit, int):
        raise ValidationError("Limit must be an integer")
    
    if limit < 1:
        raise ValidationError("Limit must be at least 1")
    
    if limit > max_limit:
        logger.warning(f"Limit {limit} exceeds maximum {max_limit}, capping at {max_limit}")
        return max_limit
    
    return limit


def validate_year(year: int) -> int:
    """
    Validate year parameter
    
    Args:
        year: Year value
        
    Returns:
        Validated year
        
    Raises:
        ValidationError: If year is invalid
    """
    if not isinstance(year, int):
        raise ValidationError("Year must be an integer")
    
    if year < 1900 or year > 2030:
        raise ValidationError("Year must be between 1900 and 2030")
    
    return year


def validate_summary_level(level: str) -> str:
    """
    Validate summary detail level
    
    Args:
        level: Summary level string
        
    Returns:
        Validated level
        
    Raises:
        ValidationError: If level is invalid
    """
    valid_levels = ["short", "medium", "long"]
    
    if not isinstance(level, str):
        raise ValidationError("Summary level must be a string")
    
    level = level.lower()
    
    if level not in valid_levels:
        raise ValidationError(f"Summary level must be one of: {', '.join(valid_levels)}")
    
    return level


def validate_paper_data(paper: Dict) -> bool:
    """
    Validate paper data structure
    
    Args:
        paper: Paper dictionary
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If paper data is invalid
    """
    required_fields = ["paper_id", "title", "abstract"]
    
    if not isinstance(paper, dict):
        raise ValidationError("Paper data must be a dictionary")
    
    for field in required_fields:
        if field not in paper:
            raise ValidationError(f"Missing required field: {field}")
        
        if not paper[field]:
            raise ValidationError(f"Field '{field}' cannot be empty")
    
    return True


def validate_email(email: str) -> str:
    """
    Validate email address
    
    Args:
        email: Email address string
        
    Returns:
        Validated email
        
    Raises:
        ValidationError: If email is invalid
    """
    if not isinstance(email, str):
        raise ValidationError("Email must be a string")
    
    email = email.strip().lower()
    
    # Simple email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError("Invalid email address format")
    
    return email


def validate_url(url: str) -> str:
    """
    Validate URL
    
    Args:
        url: URL string
        
    Returns:
        Validated URL
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not isinstance(url, str):
        raise ValidationError("URL must be a string")
    
    url = url.strip()
    
    # Simple URL validation
    if not url.startswith(('http://', 'https://')):
        raise ValidationError("URL must start with http:// or https://")
    
    if len(url) < 10:
        raise ValidationError("URL is too short")
    
    return url


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not isinstance(filename, str):
        return "unnamed_file"
    
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename or "unnamed_file"


def validate_citation_style(style: str) -> str:
    """
    Validate citation style
    
    Args:
        style: Citation style string
        
    Returns:
        Validated style
        
    Raises:
        ValidationError: If style is invalid
    """
    valid_styles = ["APA", "MLA", "IEEE", "Chicago"]
    
    if not isinstance(style, str):
        raise ValidationError("Citation style must be a string")
    
    style = style.upper()
    
    if style not in valid_styles:
        raise ValidationError(f"Citation style must be one of: {', '.join(valid_styles)}")
    
    return style