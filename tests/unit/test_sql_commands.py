import os
import sqlite3
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
data_pipeline_app_dir = root_dir / "src"
sys.path.insert(0, str(data_pipeline_app_dir))

from data_pipeline_app.pipeline_utils.keyword_pair_dataclass import KeywordPair
from data_pipeline_app.pipeline_utils.sql_db_utils import create_connection
from data_pipeline_app.pipeline_utils.sql_db_utils import get_keyword_pair_freq_count
from data_pipeline_app.pipeline_utils.sql_db_utils import (
    get_most_occurring_keywords_from_sql,
)
from data_pipeline_app.pipeline_utils.sql_db_utils import is_meeting_in_table
from data_pipeline_app.pipeline_utils.sql_db_utils import update_data_store
from data_pipeline_app.pipeline_utils.sql_db_utils import update_raw_extracts_table


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


def test_get_keyword_pair_freq_count():
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
        ("kw2", "kw1", 1);
        """
    )
    conn.commit()

    # When

    keyword_pair = KeywordPair(nlm_dcms_id="id1", keyword_1="kw1", keyword_2="kw2")
    result = get_keyword_pair_freq_count(conn, keyword_pair)

    # Then
    assert result == 1

    # When
    keyword_pair = KeywordPair(nlm_dcms_id="id1", keyword_1="kw1", keyword_2="kw3")
    result = get_keyword_pair_freq_count(conn, keyword_pair)

    # Then
    assert result == 0

    conn.close()


def test_update_data_store():
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
        ("kw2", "kw1", 1);
        """
    )
    conn.commit()
    keyword_pairs = [
        KeywordPair(nlm_dcms_id="id1", keyword_1="kw1", keyword_2="kw2"),
        KeywordPair(nlm_dcms_id="id3", keyword_1="kw2", keyword_2="kw1"),
        KeywordPair(nlm_dcms_id="id2", keyword_1="kw2", keyword_2="kw3"),
    ]

    # When
    update_data_store(conn, keyword_pairs)

    # Then
    cursor.execute("SELECT * FROM keyword_pair_frequency_table")
    result = cursor.fetchall()
    expected_result = [("kw1", "kw2", 2), ("kw2", "kw1", 2), ("kw2", "kw3", 1)]
    assert result == expected_result
    conn.close()


def test_create_connection_with_valid_db_file():
    conn = create_connection("test.db")
    assert isinstance(conn, sqlite3.Connection)
    if os.path.exists("test.db"):
        os.remove("test.db")
    else:
        raise FileNotFoundError("test.db file not found")


def test_create_connection_with_invalid_db_file():
    conn = create_connection("/invalid/path/to/db_file.db")
    assert conn is None


def test_is_meeting_in_table():
    # Given
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE raw_extracts_table (
            nlm_dcms_id TEXT,
            keyword_1 TEXT,
            keyword_2 TEXT
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO raw_extracts_table (nlm_dcms_id, keyword_1, keyword_2)
        VALUES
        ("id1", "kw1", "kw2"),
        ("id2","kw1", "kw3");
        """
    )
    conn.commit()

    # When
    search_uid = "id1"
    result = is_meeting_in_table(conn, search_uid)

    # Then
    assert result == True

    # When
    search_uid = "id3"

    # Then
    result = is_meeting_in_table(conn, search_uid)
    assert result == False

    conn.close()


def test_update_raw_extracts_table():
    # Given
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE raw_extracts_table (
            nlm_dcms_id TEXT,
            keyword_1 TEXT,
            keyword_2 TEXT
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO raw_extracts_table (nlm_dcms_id, keyword_1, keyword_2)
        VALUES
        ("id1", "kw1", "kw2"),
        ("id2","kw2", "kw3");
        """
    )

    conn.commit()

    keyword_pairs = [
        KeywordPair(nlm_dcms_id="id3", keyword_1="kw1", keyword_2="kw2"),
        KeywordPair(nlm_dcms_id="id4", keyword_1="kw2", keyword_2="kw3"),
    ]

    # When
    update_raw_extracts_table(conn, keyword_pairs)

    # Then
    cursor.execute("SELECT * FROM raw_extracts_table")
    result = cursor.fetchall()
    expected_result = [
        ("id1", "kw1", "kw2"),
        ("id2", "kw2", "kw3"),
        ("id3", "kw1", "kw2"),
        ("id4", "kw2", "kw3"),
    ]
    assert result == expected_result

    conn.close()
