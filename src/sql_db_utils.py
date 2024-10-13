import sqlite3


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
