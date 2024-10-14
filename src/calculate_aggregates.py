import sqlite3

# Stage 4-5: Aggregate keyword pairs and write to db
if __name__ == "__main__":
    conn = sqlite3.connect("/opt/data/meeting_abstracts_airflow.db")
    assert isinstance(conn, sqlite3.Connection), "Failed to create sqlite3 connection"
    sql_statement = """
        CREATE TABLE keyword_pair_frequency_table AS
        SELECT keyword_1, keyword_2, COUNT(DISTINCT( nlm_dcms_id)) AS frequency
        FROM raw_extracts_table
        GROUP BY keyword_1, keyword_2;
    """
    print(sql_statement)
    cur = conn.cursor()
    cur.execute(sql_statement)
    print(
        "Successfully added keyword_pair_frequency_table table to meeting_abstracts_airflow.db"
    )
    conn.close()
