"""Arrow schemas for type safety and consistency across the pipeline."""

import hashlib
import pyarrow as pa


def schema_hash(schema: pa.Schema) -> str:
    """Compute a stable hash of a schema for provenance tracking."""
    schema_str = str(schema)
    return hashlib.blake2b(schema_str.encode(), digest_size=16).hexdigest()


# Core tables
aircraft_schema = pa.schema([
    ("n_number", pa.string()),
    ("serial_no", pa.string()),
    ("mfr_mdl_code", pa.string()),
    ("engine_code", pa.string()),
    ("year_mfr", pa.int32()),
    ("airworthiness_class", pa.string()),
    ("seats", pa.int32()),
    ("engines", pa.int32()),
    ("reg_status", pa.string()),
    ("status_date", pa.date32()),
    ("reg_expiration", pa.date32()),
    ("mode_s_code", pa.string()),
    ("mode_s_code_hex", pa.string()),
    ("is_deregistered", pa.bool_()),
])

registrations_schema = pa.schema([
    ("n_number", pa.string()),
    ("reg_type", pa.string()),
    ("reg_status", pa.string()),
    ("status_date", pa.date32()),
    ("reg_expiration", pa.date32()),
    ("cert_issue_date", pa.date32()),
])

owners_schema = pa.schema([
    ("owner_id", pa.int64()),
    ("n_number", pa.string()),
    ("owner_type", pa.string()),
    # Raw fields
    ("owner_name_raw", pa.string()),
    ("address1_raw", pa.string()),
    ("address2_raw", pa.string()),
    ("city_raw", pa.string()),
    ("state_raw", pa.string()),
    ("zip_raw", pa.string()),
    # Standardized fields
    ("owner_name_std", pa.string()),
    ("address_all_std", pa.string()),
    ("city_std", pa.string()),
    ("state_std", pa.string()),
    ("zip5", pa.string()),
])

# Reference tables
aircraft_make_model_schema = pa.schema([
    ("mfr_mdl_code", pa.string()),
    ("maker", pa.string()),
    ("model", pa.string()),
    ("category", pa.string()),
    ("type", pa.string()),
    ("engine_type", pa.string()),
    ("seats_default", pa.int32()),
])

engines_schema = pa.schema([
    ("engine_code", pa.string()),
    ("manufacturer", pa.string()),
    ("model", pa.string()),
    ("type", pa.string()),
    ("horsepower", pa.int32()),
    ("cylinders", pa.int32()),
])

# Optional: deregistrations
deregistrations_schema = pa.schema([
    ("n_number", pa.string()),
    ("dereg_date", pa.date32()),
    ("reason_code", pa.string()),
    ("new_mark", pa.string()),
    ("notes_raw", pa.string()),
])

# Summary views
owners_summary_schema = pa.schema([
    ("n_number", pa.string()),
    ("owner_count", pa.int32()),
    ("owner_names_concat", pa.string()),
    ("any_trust_flag", pa.bool_()),
])


# Schema registry for manifest generation
SCHEMAS = {
    "aircraft": aircraft_schema,
    "registrations": registrations_schema,
    "owners": owners_schema,
    "aircraft_make_model": aircraft_make_model_schema,
    "engines": engines_schema,
    "deregistrations": deregistrations_schema,
    "owners_summary": owners_summary_schema,
}


def get_all_schema_hashes() -> dict[str, str]:
    """Generate schema hashes for all tables."""
    return {name: schema_hash(schema) for name, schema in SCHEMAS.items()}

