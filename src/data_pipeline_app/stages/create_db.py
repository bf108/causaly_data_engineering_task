import sqlite3

from data_pipeline_app.pipeline_utils.sql_db_utils import create_connection

# Stage 0: Create SQLite3 database
if __name__ == "__main__":
    conn = create_connection("/opt/data/meeting_abstracts_airflow.db")
    assert isinstance(conn, sqlite3.Connection), "Failed to create sqlite3 connection"
    print("SQLite DB created successfully")
    conn.close()
