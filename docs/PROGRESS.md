# Development Progress

This document tracks the implementation journey for hangarbay.

## Session 1: Foundation (2025-11-08)

### Goals
Bootstrap the project from the planning document and get to a working data fetch.

### What We Built

**1. Project Structure**
- Modern Python packaging with `pyproject.toml`
- Clean directory layout matching the plan
- MIT license
- Proper .gitignore

**2. Schema Definitions** (`hangarbay/schemas.py`)
- Defined Arrow schemas for all 7 tables
- Implemented deterministic schema hashing with blake2
- Created schema registry for manifest generation
- Wrote tests to validate schema properties

**3. Fetch Pipeline** (`pipelines/fetch.py`)
- Downloads FAA ReleasableAircraft.zip (single ZIP file, not individual TXT files)
- Extracts MASTER.txt, ACFTREF.txt, ENGINE.txt
- Creates manifest.json with:
  - Snapshot date and timestamp
  - Source URLs and file sizes
  - SHA256 hashes for each file
  - Schema hashes for all tables
  - Reference to previous snapshot (for future diffs)
- Retry logic with exponential backoff
- **Key fix**: Added browser-like headers to avoid FAA server blocking automated requests

**4. CLI** (`hangarbay/cli.py`)
- Typer-based CLI with Rich output
- `hangar fetch` - working
- `hangar version` - working
- Stubs for search, fleet, owners, sql commands

**5. Testing**
- pytest setup
- 5 schema validation tests (all passing)
- Tests for deterministic hashing, field presence, type checking

**6. Documentation**
- README with quick start
- Updated planning doc with implementation status
- CHANGELOG tracking progress
- This PROGRESS.md file

### Challenges Solved

**FAA Server Blocking**
- Initial attempts timed out after 5+ minutes
- FAA server was rejecting automated requests
- Solution: Added browser-like User-Agent and headers to requests
- Now downloads successfully (~72 MB in reasonable time)

### Data Snapshot (2025-11-08)

Successfully fetched:
```
MASTER.txt:   180 MB,  307,794 rows
ACFTREF.txt:   14 MB,  make/model reference
ENGINE.txt:   227 KB,  engine specifications
```

Sample fields from MASTER.txt:
- N-NUMBER, SERIAL NUMBER, MFR MDL CODE, ENG MFR MDL
- YEAR MFR, TYPE REGISTRANT, NAME, STREET, CITY, STATE, ZIP
- LAST ACTION DATE, CERT ISSUE DATE, EXPIRATION DATE
- STATUS CODE, MODE S CODE, etc.

### Next Session Goals

**Normalize Pipeline**
1. Parse MASTER.txt with PyArrow CSV reader
2. Split into 3 tables:
   - `aircraft` - airframe facts with denormalized registration fields
   - `registrations` - canonical registration state
   - `owners` - one row per owner-party with raw + standardized fields
3. Generate deterministic `owner_id` using xxhash64
4. Apply lite address standardization:
   - Uppercase, trim, collapse whitespace
   - Combine address1 + address2
   - Normalize state to 2-letter codes
   - Zero-pad ZIP to 5 digits
5. Parse ACFTREF.txt → `aircraft_make_model` table
6. Parse ENGINE.txt → `engines` table
7. Cast all tables to declared Arrow schemas
8. Write Parquet files to `data/interim/`
9. Update manifest with row counts and write to `data/publish/`

**Estimated Complexity**: Medium
- PyArrow CSV parsing is straightforward
- Address standardization is deterministic string ops
- Main complexity is splitting MASTER into 3 tables correctly
- Need to handle encoding issues (Windows-1252 vs UTF-8?)

### Commands Reference

```bash
# Fetch data
hangar fetch

# Run tests
pytest tests/ -v

# What's in the snapshot
ls -lh data/raw/2025-11-08/
cat data/raw/2025-11-08/manifest.json | jq

# Peek at raw data
head -20 data/raw/2025-11-08/MASTER.txt
wc -l data/raw/2025-11-08/*.txt
```

### Technical Decisions

1. **Package name**: `hangarbay` with CLI command `hangar`
2. **Fetch strategy**: Single ZIP download + extract (not individual files)
3. **Schema management**: Versioned in code, hashed in manifest
4. **Provenance**: SHA256 + timestamps + schema versions in manifest.json
5. **Error handling**: Retry with backoff, preserve previous snapshot on failure

---

## Future Sessions

### Session 2: Normalize Pipeline (Next)
Goal: Raw TXT → Typed Parquet tables

### Session 3: Publish Pipeline
Goal: Parquet → DuckDB + SQLite FTS

### Session 4: Query Interface
Goal: Working CLI commands for search and analysis

### Session 5: Quality & Polish
Goal: Verify checks, anomaly scans, documentation

