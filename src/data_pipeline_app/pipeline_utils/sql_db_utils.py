import sqlite3

from psycopg2.extensions import connection

from data_pipeline_app.pipeline_utils.keyword_pair_dataclass import KeywordPair


def get_most_occurring_keywords_from_sql(
    conn: connection, search_string: str
) -> list[str]:
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT keyword_2 FROM keyword_pair_frequency_table WHERE keyword_1 = '{search_string}' "
        f"AND frequency = (SELECT MAX(frequency) FROM keyword_pair_frequency_table WHERE keyword_1 = '{search_string}') "
        f"ORDER BY keyword_2 ASC"
    )
    top_keyword_pairs = cursor.fetchall()
    print(top_keyword_pairs)
    top_matches = [kw[0] for kw in top_keyword_pairs]
    return top_matches


def get_keyword_pair_freq_count(conn: connection, keyword_pair: KeywordPair) -> int:
    cursor = conn.cursor()
    kw1 = keyword_pair.keyword_1
    kw2 = keyword_pair.keyword_2
    cursor.execute(
        f"""
        SELECT frequency
        FROM keyword_pair_frequency_table
        WHERE keyword_1 = '{kw1}' AND keyword_2 = '{kw2}'
        """
    )
    freq_val = cursor.fetchone()
    if freq_val:
        return freq_val[0]
    return 0


def update_keyword_pair_frequency_table(
    conn: connection, keyword_pair: KeywordPair
) -> None:
    cursor = conn.cursor()
    kw1 = keyword_pair.keyword_1
    kw2 = keyword_pair.keyword_2
    cursor.execute(
        f"""
        UPDATE keyword_pair_frequency_table
        SET frequency = frequency + 1
        WHERE keyword_1 = '{kw1}' AND keyword_2 = '{kw2}'
        """
    )
    conn.commit()


def insert_keyword_pair_frequency_table(
    conn: connection, keyword_pair: KeywordPair
) -> None:
    cursor = conn.cursor()
    kw1 = keyword_pair.keyword_1
    kw2 = keyword_pair.keyword_2
    cursor.execute(
        f"""
        INSERT INTO keyword_pair_frequency_table (keyword_1, keyword_2, frequency)
        VALUES ('{kw1}', '{kw2}', 1)
        """
    )
    conn.commit()


def update_data_store(conn: connection, keyword_pairs: list[KeywordPair]) -> None:
    for keyword_pair in keyword_pairs:
        freq = get_keyword_pair_freq_count(conn, keyword_pair)
        if freq == 0:
            insert_keyword_pair_frequency_table(conn, keyword_pair)
        else:
            update_keyword_pair_frequency_table(conn, keyword_pair)


def is_meeting_in_table(conn: connection, nlm_dcms_id: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM keyword_pairs_table
        WHERE nlm_dcms_id = '{nlm_dcms_id}'
        """
    )
    count = cursor.fetchone()
    return count[0] > 0


def update_keyword_pairs_table(
    conn: connection, keyword_pairs: list[KeywordPair]
) -> None:
    keyword_pairs_tuples = [
        (kw.nlm_dcms_id, kw.keyword_1, kw.keyword_2) for kw in keyword_pairs
    ]
    if isinstance(conn, connection):
        query = """INSERT INTO keyword_pairs_table (nlm_dcms_id, keyword_1, keyword_2) VALUES (%s, %s, %s)"""
    elif isinstance(conn, sqlite3.Connection):
        query = """INSERT INTO keyword_pairs_table (nlm_dcms_id, keyword_1, keyword_2) VALUES (?, ?, ?)"""
    else:
        raise ValueError("Connection object not recognized")

    cursor = conn.cursor()
    cursor.executemany(query, keyword_pairs_tuples)
    conn.commit()
