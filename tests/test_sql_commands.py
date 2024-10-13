import sqlite3

import pytest
from causaly.src.sql_db_utils import get_most_occurring_keywords_from_sql


def test_get_most_occurring_keywords_from_sql():
    # Given
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE keyword_pair_frequency_table (
            keyword_1 TEXT,
            keyword_2 TEXT,
            frequency INTEGER
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO keyword_pair_frequency_table (keyword_1, keyword_2, frequency)
        VALUES
        ("kw1", "kw2", 1),
        ("kw1", "kw3", 10);
        """
    )
    conn.commit()

    # When
    search_string = "kw1"
    result = get_most_occurring_keywords_from_sql(conn, search_string)

    # Then
    assert result == ["kw3"]

    conn.close()
