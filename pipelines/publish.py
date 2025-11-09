"""Publish normalized tables to DuckDB and SQLite FTS."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import duckdb
import pyarrow.parquet as pq
from rich.console import Console

console = Console()


def create_duckdb(publish_dir: Path, duckdb_path: Path) -> None:
    """
    Load Parquet files into DuckDB database.
    
    Args:
        publish_dir: Directory containing Parquet files
        duckdb_path: Path for the DuckDB database file
    """
    console.print(f"[cyan]Creating DuckDB at {duckdb_path}...[/cyan]")
    
    # Remove existing database
    if duckdb_path.exists():
        duckdb_path.unlink()
    
    # Connect to DuckDB
    conn = duckdb.connect(str(duckdb_path))
    
    # Load each Parquet file as a table
    tables = ["aircraft", "registrations", "owners", "aircraft_make_model", "engines"]
    
    for table_name in tables:
        parquet_file = publish_dir / f"{table_name}.parquet"
        if not parquet_file.exists():
            console.print(f"[yellow]Warning: {parquet_file} not found, skipping[/yellow]")
            continue
        
        console.print(f"[cyan]Loading {table_name}...[/cyan]")
        
        # Create table from Parquet
        conn.execute(f"""
            CREATE TABLE {table_name} AS 
            SELECT * FROM read_parquet('{parquet_file}')
        """)
        
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        console.print(f"[green]✓ Loaded {table_name}: {row_count:,} rows[/green]")
    
    # Create owners_summary materialized view
    console.print(f"[cyan]Creating owners_summary view...[/cyan]")
    
    conn.execute("""
        CREATE TABLE owners_summary AS
        SELECT 
            n_number,
            COUNT(*) as owner_count,
            STRING_AGG(owner_name_std, '; ') as owner_names_concat,
            BOOL_OR(owner_type IN ('2', '4', '5')) as any_trust_flag
        FROM owners
        GROUP BY n_number
    """)
    
    summary_count = conn.execute("SELECT COUNT(*) FROM owners_summary").fetchone()[0]
    console.print(f"[green]✓ Created owners_summary: {summary_count:,} rows[/green]")
    
    # Create some useful indexes
    console.print(f"[cyan]Creating indexes...[/cyan]")
    
    # Index on n_number for fast lookups
    conn.execute("CREATE INDEX idx_aircraft_n_number ON aircraft(n_number)")
    conn.execute("CREATE INDEX idx_registrations_n_number ON registrations(n_number)")
    conn.execute("CREATE INDEX idx_owners_n_number ON owners(n_number)")
    conn.execute("CREATE INDEX idx_owners_summary_n_number ON owners_summary(n_number)")
    
    # Index on codes for joins
    conn.execute("CREATE INDEX idx_aircraft_mfr_mdl_code ON aircraft(mfr_mdl_code)")
    conn.execute("CREATE INDEX idx_aircraft_engine_code ON aircraft(engine_code)")
    
    console.print(f"[green]✓ Created indexes[/green]")
    
    # Show some stats
    console.print(f"\n[cyan]Database statistics:[/cyan]")
    stats = conn.execute("""
        SELECT 
            table_name,
            estimated_size as row_count
        FROM duckdb_tables()
        WHERE schema_name = 'main'
        ORDER BY table_name
    """).fetchall()
    
    for table, count in stats:
        console.print(f"  {table}: {count:,} rows")
    
    conn.close()
    console.print(f"[green]✓ DuckDB created: {duckdb_path}[/green]")


def create_sqlite_fts(publish_dir: Path, sqlite_path: Path) -> None:
    """
    Create SQLite database with FTS5 index for owner search.
    
    Args:
        publish_dir: Directory containing Parquet files
        sqlite_path: Path for the SQLite database file
    """
    console.print(f"\n[cyan]Creating SQLite FTS at {sqlite_path}...[/cyan]")
    
    # Remove existing database
    if sqlite_path.exists():
        sqlite_path.unlink()
    
    # Connect to SQLite
    conn = sqlite3.connect(str(sqlite_path))
    cursor = conn.cursor()
    
    # Create owners table
    cursor.execute("""
        CREATE TABLE owners (
            owner_id INTEGER PRIMARY KEY,
            n_number TEXT NOT NULL,
            owner_name_std TEXT,
            address_all_std TEXT,
            city_std TEXT,
            state_std TEXT,
            zip5 TEXT
        )
    """)
    
    # Read owners from Parquet
    console.print("[cyan]Loading owners data...[/cyan]")
    owners_table = pq.read_table(publish_dir / "owners.parquet")
    owners_df = owners_table.to_pandas()
    
    # Insert into SQLite (just the fields we need for search)
    owners_data = owners_df[[
        'owner_id', 'n_number', 'owner_name_std', 'address_all_std',
        'city_std', 'state_std', 'zip5'
    ]].values.tolist()
    
    cursor.executemany("""
        INSERT INTO owners VALUES (?, ?, ?, ?, ?, ?, ?)
    """, owners_data)
    
    console.print(f"[green]✓ Inserted {len(owners_data):,} owner records[/green]")
    
    # Create FTS5 virtual table
    console.print("[cyan]Creating FTS5 index...[/cyan]")
    
    cursor.execute("""
        CREATE VIRTUAL TABLE owners_fts USING fts5(
            owner_name_std,
            address_all_std,
            city_std,
            state_std,
            content=owners,
            content_rowid=owner_id
        )
    """)
    
    # Populate FTS index
    cursor.execute("""
        INSERT INTO owners_fts(owner_name_std, address_all_std, city_std, state_std)
        SELECT owner_name_std, address_all_std, city_std, state_std
        FROM owners
    """)
    
    console.print(f"[green]✓ Created FTS5 index[/green]")
    
    # Create indexes on regular columns for filters
    cursor.execute("CREATE INDEX idx_owners_n_number ON owners(n_number)")
    cursor.execute("CREATE INDEX idx_owners_state ON owners(state_std)")
    
    conn.commit()
    conn.close()
    
    console.print(f"[green]✓ SQLite FTS created: {sqlite_path}[/green]")


def publish(
    data_root: Path = Path("data"),
    snapshot_date: Optional[str] = None,
) -> Path:
    """
    Publish normalized Parquet to DuckDB and SQLite FTS.
    
    Args:
        data_root: Root data directory
        snapshot_date: Snapshot date (for metadata)
    
    Returns:
        Path to publish directory
    """
    publish_dir = data_root / "publish"
    
    if not publish_dir.exists() or not (publish_dir / "aircraft.parquet").exists():
        console.print("[red]No normalized data found. Run 'hangar normalize' first.[/red]")
        raise FileNotFoundError("No Parquet files found in publish directory")
    
    console.print(f"\n[bold cyan]Publishing data from {publish_dir}[/bold cyan]\n")
    
    # Create DuckDB
    duckdb_path = publish_dir / "registry.duckdb"
    create_duckdb(publish_dir, duckdb_path)
    
    # Create SQLite FTS
    sqlite_path = publish_dir / "owners.sqlite"
    create_sqlite_fts(publish_dir, sqlite_path)
    
    # Write metadata
    console.print(f"\n[cyan]Writing publish metadata...[/cyan]")
    
    # Get snapshot date from normalize metadata if available
    if snapshot_date is None:
        normalize_meta = publish_dir / "_meta" / "normalize.json"
        if normalize_meta.exists():
            with open(normalize_meta) as f:
                meta = json.load(f)
                snapshot_date = meta.get("snapshot_date", "unknown")
    
    metadata = {
        "snapshot_date": snapshot_date,
        "published_at": datetime.utcnow().isoformat() + "Z",
        "duckdb_path": str(duckdb_path.name),
        "sqlite_path": str(sqlite_path.name),
        "duckdb_size_mb": round(duckdb_path.stat().st_size / 1024 / 1024, 2),
        "sqlite_size_mb": round(sqlite_path.stat().st_size / 1024 / 1024, 2),
    }
    
    meta_dir = publish_dir / "_meta"
    meta_dir.mkdir(exist_ok=True)
    
    with open(meta_dir / "publish.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    console.print(f"[green]✓ Wrote metadata to {meta_dir / 'publish.json'}[/green]")
    
    console.print(f"\n[bold green]✓ Publish complete![/bold green]")
    console.print(f"[dim]DuckDB: {duckdb_path}[/dim]")
    console.print(f"[dim]SQLite: {sqlite_path}[/dim]\n")
    
    # Show example queries
    console.print("[cyan]Try these queries:[/cyan]")
    console.print("  hangar sql \"SELECT COUNT(*) FROM aircraft\"")
    console.print("  hangar sql \"SELECT maker, COUNT(*) FROM aircraft JOIN aircraft_make_model USING(mfr_mdl_code) GROUP BY 1 ORDER BY 2 DESC LIMIT 10\"")
    
    return publish_dir


if __name__ == "__main__":
    publish()
