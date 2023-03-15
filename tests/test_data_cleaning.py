import pytest

from data_cleaning import clean_column_name


@pytest.mark.parametrize("column_name, expected_result", [
    ("oRdeRs", "orders"),
    ("customer-birthday", 'customer_birthday'),
    ("order__type", 'order_type'),
    ("column-name@1", "column_name_1"),
    ("  column  ", "column"),
    ("COLUMN", "column"),
])
def test_sanitize_column_name(column_name: str, expected_result: str) -> None:
    assert clean_column_name(column_name) == expected_result
