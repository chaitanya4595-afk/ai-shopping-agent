from pathlib import Path
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "store.db"


def get_product_rating(product_id: int, db_path: Path = DB_PATH) -> dict:
    """Return average rating and review count for one product."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT AVG(rating), COUNT(*) FROM reviews WHERE product_id = ?",
        (product_id,),
    )
    row = cursor.fetchone()
    conn.close()

    avg = round(row[0], 2) if row and row[0] is not None else 0.0
    count = row[1] if row else 0
    return {
        "product_id": product_id,
        "average_rating": avg,
        "review_count": count,
    }


def get_ratings_for_products(product_ids: list[int], db_path: Path = DB_PATH) -> list[dict]:
    """Return ratings for a list of product IDs."""
    if not product_ids:
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    placeholders = ",".join("?" * len(product_ids))
    cursor.execute(
        f"""
        SELECT product_id, AVG(rating), COUNT(*)
        FROM reviews
        WHERE product_id IN ({placeholders})
        GROUP BY product_id
        """,
        product_ids,
    )
    rows = cursor.fetchall()
    conn.close()

    ratings = {
        row[0]: {
            "average_rating": round(row[1], 2),
            "review_count": row[2],
        }
        for row in rows
    }

    return [
        {
            "product_id": product_id,
            "average_rating": ratings.get(product_id, {}).get("average_rating", 0.0),
            "review_count": ratings.get(product_id, {}).get("review_count", 0),
        }
        for product_id in product_ids
    ]
