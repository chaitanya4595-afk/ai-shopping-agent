import sqlite3
from pathlib import Path


DB = Path(__file__).resolve().parents[1] / "data" / "store.db"


def test_catalog_contains_demo_products():
    with sqlite3.connect(DB) as conn:
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    assert count == 32


def test_honey_catalog_is_available():
    with sqlite3.connect(DB) as conn:
        names = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM products WHERE category = 'honey' ORDER BY id"
            )
        ]
    assert "Organic Raw Honey" in names
