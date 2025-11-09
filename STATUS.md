# Current Status

**Last Updated**: 2025-11-08  
**Version**: 0.3.0  
**Phase**: 🎉 **MVP COMPLETE!** All Core Features Working! 🎉

## ✅ What Works Right Now

**Full pipeline from raw data to SQL queries:**

```bash
# Install
pip install -e ".[dev]"

# Run the complete pipeline
hangar fetch      # ✅ Download 72 MB FAA data
hangar normalize  # ✅ Parse to 36 MB Parquet 
hangar publish    # ✅ Build 161 MB DuckDB + SQLite FTS

# Or just: make all

# Query the data!
hangar search N100
hangar sql "SELECT COUNT(*) FROM aircraft"
hangar sql "SELECT maker, COUNT(*) as count 
  FROM aircraft JOIN aircraft_make_model USING(mfr_mdl_code) 
  WHERE maker != '' GROUP BY 1 ORDER BY 2 DESC LIMIT 10"

# Tests
pytest tests/ -v  # ✅ 10/10 passing
```

## 📊 Current Data

**Raw files:**
```
data/raw/2025-11-08/
├── MASTER.txt          180 MB   307,794 aircraft registrations
├── ACFTREF.txt          14 MB   make/model reference data  
├── ENGINE.txt          227 KB   engine specifications
├── manifest.json        1.2 KB  provenance + SHA256 hashes
└── ReleasableAircraft.zip  69 MB   original download
```

**Normalized Parquet tables:**
```
data/publish/
├── aircraft.parquet              5.9 MB   307,793 rows
├── registrations.parquet         2.6 MB   307,793 rows
├── owners.parquet               25.0 MB   307,793 rows (with address std!)
├── aircraft_make_model.parquet   2.2 MB    93,342 rows
├── engines.parquet                71 KB     4,736 rows
└── _meta/normalize.json          metadata + row counts
```

**Queryable databases:**
```
data/publish/
├── registry.duckdb              106 MB    6 tables + indexes
├── owners.sqlite                 55 MB    FTS5 full-text search
└── _meta/publish.json            metadata
```

**Query Performance:** Sub-second on 300K+ rows!

## 🎯 Optional Enhancements

The core pipeline is **complete and working**! Future additions:

1. **Python API** - Programmatic access for notebooks/scripts
2. **`hangar fleet` command** - Search by owner name
3. **Verify checks** - Data quality validation
4. **Historical diffs** - Track changes across snapshots  
5. **FastAPI service** - HTTP API for web apps
6. **Geocoding** - Owner city coordinates for maps

**But you can use it productively RIGHT NOW!** 🚀

## 📝 Key Decisions Made

1. Project name: `hangarbay` (package) / `hangar` (CLI)
2. FAA data comes as single ZIP, not individual files
3. Browser headers required to avoid server blocking
4. Schemas versioned in code, hashed in manifest
5. Keep both raw and standardized address fields

## 🔗 Useful Links

- FAA Registry: https://registry.faa.gov/database/ReleasableAircraft.zip
- Planning Doc: `FAA_registry_plan.md`
- Progress Log: `docs/PROGRESS.md`
- Changelog: `CHANGELOG.md`

