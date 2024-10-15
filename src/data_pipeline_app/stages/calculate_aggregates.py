import psycopg2

# Stage 4-5: Aggregate keyword pairs and write to db
if __name__ == "__main__":
    conn = psycopg2.connect(
        host="postgres-datastore",
        database="datastore",
        user="user",
        password="password",
    )
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
    cur.execute(
        "SELECT * FROM keyword_pair_frequency_table ORDER BY frequency DESC LIMIT 10;"
    )
    resp = cur.fetchall()
    print(resp)
    conn.close()
