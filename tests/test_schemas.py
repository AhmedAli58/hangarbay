"""Test schema definitions and hash generation."""

import pyarrow as pa
from hangarbay.schemas import (
    aircraft_schema,
    registrations_schema,
    owners_schema,
    schema_hash,
    get_all_schema_hashes,
)


def test_aircraft_schema_has_required_fields():
    """Verify aircraft schema has all required fields."""
    field_names = [field.name for field in aircraft_schema]
    required = ["n_number", "serial_no", "mfr_mdl_code", "reg_status"]
    for field in required:
        assert field in field_names


def test_n_number_is_string():
    """N-numbers must be stored as strings to preserve leading zeros."""
    field = aircraft_schema.field("n_number")
    assert field.type == pa.string()


def test_schema_hash_is_deterministic():
    """Schema hash should be stable across runs."""
    hash1 = schema_hash(aircraft_schema)
    hash2 = schema_hash(aircraft_schema)
    assert hash1 == hash2
    assert len(hash1) == 32  # blake2b with digest_size=16 -> 32 hex chars


def test_get_all_schema_hashes():
    """Verify we can generate hashes for all schemas."""
    hashes = get_all_schema_hashes()
    assert "aircraft" in hashes
    assert "registrations" in hashes
    assert "owners" in hashes
    assert all(len(h) == 32 for h in hashes.values())


def test_owners_has_raw_and_std_fields():
    """Owners schema should have both raw and standardized fields."""
    field_names = [field.name for field in owners_schema]
    assert "owner_name_raw" in field_names
    assert "owner_name_std" in field_names
    assert "zip_raw" in field_names
    assert "zip5" in field_names

