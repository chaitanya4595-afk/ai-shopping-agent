from ai_shopping_agent.reviews import get_product_rating, get_ratings_for_products


def test_single_product_rating():
    result = get_product_rating(1)
    assert result["product_id"] == 1
    assert result["average_rating"] > 0
    assert result["review_count"] > 0


def test_batch_ratings_preserve_requested_ids():
    results = get_ratings_for_products([1, 3, 5])
    assert [row["product_id"] for row in results] == [1, 3, 5]
    assert all(row["review_count"] > 0 for row in results)
