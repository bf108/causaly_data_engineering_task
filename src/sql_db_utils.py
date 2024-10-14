import sqlite3

from keyword_pair_dataclass import KeywordPair


def create_connection(db_file: str) -> sqlite3.Connection | None:
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn


def get_most_occurring_keywords_from_sql(
    conn: sqlite3.Connection, search_string: str
) -> list[str]:
    cursor = conn.cursor()
    top_keyword_pairs = cursor.execute(
        f"SELECT keyword_2 FROM keyword_pair_frequency_table WHERE keyword_1 = '{search_string}'"
        f"AND frequency = (SELECT MAX(frequency) FROM keyword_pair_frequency_table WHERE keyword_1 = '{search_string}')"
        f"ORDER BY keyword_2 ASC"
    )
    top_matches = [kw[0] for kw in top_keyword_pairs]
    return top_matches


def get_keyword_pair_freq_count(
    conn: sqlite3.Connection, keyword_pair: KeywordPair
) -> int:
    cursor = conn.cursor()
    freq = cursor.execute(
        """
        SELECT frequency
        FROM keyword_pair_frequency_table
        WHERE keyword_1 = ? AND keyword_2 = ?
        """,
        (keyword_pair.keyword_1, keyword_pair.keyword_2),
    )
    freq_val = freq.fetchone()
    if freq_val:
        return freq_val[0]
    return 0


def update_keyword_pair_frequency_table(
    conn: sqlite3.Connection, keyword_pair: KeywordPair
) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE keyword_pair_frequency_table
        SET frequency = frequency + 1
        WHERE keyword_1 = ? AND keyword_2 = ?
        """,
        (keyword_pair.keyword_1, keyword_pair.keyword_2),
    )
    conn.commit()


def insert_keyword_pair_frequency_table(
    conn: sqlite3.Connection, keyword_pair: KeywordPair
) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO keyword_pair_frequency_table (keyword_1, keyword_2, frequency)
        VALUES (?, ?, 1)
        """,
        (keyword_pair.keyword_1, keyword_pair.keyword_2),
    )
    conn.commit()


def update_data_store(
    conn: sqlite3.Connection, keyword_pairs: list[KeywordPair]
) -> None:
    for keyword_pair in keyword_pairs:
        freq = get_keyword_pair_freq_count(conn, keyword_pair)
        if freq == 0:
            insert_keyword_pair_frequency_table(conn, keyword_pair)
        else:
            update_keyword_pair_frequency_table(conn, keyword_pair)
