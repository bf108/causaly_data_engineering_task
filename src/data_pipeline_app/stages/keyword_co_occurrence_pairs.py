import sqlite3

from data_pipeline_app.pipeline_utils.batch_pipeline_utils import (
    parse_all_meeting_abstracts,
)


# Stage 1-3: Parse XML file, extract keyword pairs, preprocess keywords
if __name__ == "__main__":
    conn = sqlite3.connect("/opt/data/meeting_abstracts_airflow.db")
    assert isinstance(conn, sqlite3.Connection), "Failed to create sqlite3 connection"
    meetings_data = str("/opt/data/SpaceLifeSciences.xml")
    df = parse_all_meeting_abstracts(meetings_data)
    print(f"Shape of raw_extracts_table: {df.shape}")
    df.to_sql("raw_extracts_table", conn, if_exists="replace", index=False)
    print("Successfully populated `raw_extracts_table` in meeting_abstracts_airflow.db")
    conn.close()
