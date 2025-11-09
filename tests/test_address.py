"""Test address standardization utilities."""

from hangarbay.address import (
    clean_text,
    standardize_state,
    standardize_zip,
    combine_address,
    standardize_owner_name,
)


def test_clean_text():
    """Test basic text cleaning."""
    assert clean_text("  hello  world  ") == "HELLO WORLD"
    assert clean_text("lowercase") == "LOWERCASE"
    assert clean_text("") == ""
    assert clean_text(None) == ""
    assert clean_text("  multiple   spaces  ") == "MULTIPLE SPACES"


def test_standardize_state():
    """Test state normalization."""
    # Already abbreviated
    assert standardize_state("CA") == "CA"
    assert standardize_state("ca") == "CA"
    
    # Full state names
    assert standardize_state("California") == "CA"
    assert standardize_state("CALIFORNIA") == "CA"
    assert standardize_state("New York") == "NY"
    assert standardize_state("TEXAS") == "TX"
    
    # Edge cases
    assert standardize_state("") == ""
    assert standardize_state(None) == ""
    
    # Territories
    assert standardize_state("Puerto Rico") == "PR"
    assert standardize_state("GUAM") == "GU"


def test_standardize_zip():
    """Test ZIP code normalization."""
    # 5-digit ZIP
    assert standardize_zip("12345") == "12345"
    
    # ZIP+4
    assert standardize_zip("12345-6789") == "12345"
    assert standardize_zip("123456789") == "12345"
    
    # Leading zeros (should be preserved)
    assert standardize_zip("01234") == "01234"
    assert standardize_zip("123") == "00123"
    
    # With spaces and punctuation
    assert standardize_zip(" 12345 ") == "12345"
    assert standardize_zip("12345.") == "12345"
    
    # Edge cases
    assert standardize_zip("") == ""
    assert standardize_zip(None) == ""
    assert standardize_zip("ABCDE") == ""


def test_combine_address():
    """Test address combination."""
    assert combine_address("123 Main St", "Apt 4") == "123 MAIN ST APT 4"
    assert combine_address("123 Main St", "") == "123 MAIN ST"
    assert combine_address("", "Apt 4") == "APT 4"
    assert combine_address("", "") == ""
    assert combine_address(None, None) == ""
    assert combine_address("  spaces  ", "  more  ") == "SPACES MORE"


def test_standardize_owner_name():
    """Test owner name standardization."""
    assert standardize_owner_name("John Doe") == "JOHN DOE"
    assert standardize_owner_name("  extra  spaces  ") == "EXTRA SPACES"
    assert standardize_owner_name("") == ""
    assert standardize_owner_name(None) == ""

