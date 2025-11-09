"""Lite address standardization utilities."""

import re
from typing import Optional


# USPS state abbreviations mapping (common variants)
STATE_ABBREVIATIONS = {
    "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR",
    "CALIFORNIA": "CA", "COLORADO": "CO", "CONNECTICUT": "CT", "DELAWARE": "DE",
    "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI", "IDAHO": "ID",
    "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS",
    "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME", "MARYLAND": "MD",
    "MASSACHUSETTS": "MA", "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS",
    "MISSOURI": "MO", "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM", "NEW YORK": "NY",
    "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK",
    "OREGON": "OR", "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT",
    "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI", "WYOMING": "WY",
    "DISTRICT OF COLUMBIA": "DC", "PUERTO RICO": "PR", "GUAM": "GU",
    "VIRGIN ISLANDS": "VI", "AMERICAN SAMOA": "AS", "NORTHERN MARIANA ISLANDS": "MP",
}


def clean_text(text: Optional[str]) -> str:
    """
    Clean and normalize text: uppercase, trim, collapse whitespace.
    
    Args:
        text: Input text (can be None or empty)
    
    Returns:
        Cleaned text (empty string if input is None/empty)
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Collapse multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    
    # Uppercase
    text = text.upper()
    
    return text


def standardize_state(state: Optional[str]) -> str:
    """
    Normalize state to 2-letter USPS abbreviation.
    
    Args:
        state: State name or abbreviation
    
    Returns:
        2-letter state code (empty if invalid/unknown)
    """
    if not state or not isinstance(state, str):
        return ""
    
    state_clean = state.strip().upper()
    
    # Already a 2-letter code?
    if len(state_clean) == 2 and state_clean.isalpha():
        return state_clean
    
    # Look up full state name
    return STATE_ABBREVIATIONS.get(state_clean, state_clean[:2] if len(state_clean) >= 2 else "")


def standardize_zip(zip_code: Optional[str]) -> str:
    """
    Normalize ZIP code to 5 digits (US only).
    
    Args:
        zip_code: ZIP code (may include ZIP+4, hyphens, spaces)
    
    Returns:
        5-digit ZIP code (empty if invalid)
    """
    if not zip_code or not isinstance(zip_code, str):
        return ""
    
    # Extract only digits
    digits = re.sub(r'\D', '', zip_code)
    
    # Left-pad to 5 digits with zeros
    if len(digits) > 0:
        return digits[:5].zfill(5)
    
    return ""


def combine_address(address1: Optional[str], address2: Optional[str]) -> str:
    """
    Combine address1 and address2 into a single standardized field.
    
    Args:
        address1: Primary address line
        address2: Secondary address line
    
    Returns:
        Combined address (space-separated if both present)
    """
    addr1 = clean_text(address1)
    addr2 = clean_text(address2)
    
    if addr1 and addr2:
        return f"{addr1} {addr2}"
    elif addr1:
        return addr1
    elif addr2:
        return addr2
    else:
        return ""


def standardize_owner_name(name: Optional[str]) -> str:
    """
    Standardize owner name with basic cleanup.
    
    Args:
        name: Owner name
    
    Returns:
        Cleaned owner name
    """
    cleaned = clean_text(name)
    
    # Remove common prefixes that clutter searches (optional enhancement)
    # For MVP, just return cleaned
    return cleaned

