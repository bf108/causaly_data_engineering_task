import psycopg2
from sqlalchemy import create_engine

from data_pipeline_app.pipeline_utils.batch_pipeline_utils import (
    parse_all_meeting_abstracts,
)


# Stage 1-3: Parse XML file, extract keyword pairs, preprocess keywords
if __name__ == "__main__":
    engine = create_engine(
        "postgresql+psycopg2://user:password@postgres-datastore/datastore"
    )
    conn = psycopg2.connect(
        host="postgres-datastore",
        database="datastore",
        user="user",
        password="password",
    )
    cursor = conn.cursor()
    # Print PostgreSQL details
    print("PostgreSQL server information")
    print(conn.get_dsn_parameters(), "\n")
    meetings_data = str("/opt/data/SpaceLifeSciences.xml")
    df = parse_all_meeting_abstracts(meetings_data)
    print(f"Shape of raw_extracts_table: {df.shape}")
    df.to_sql("raw_extracts_table", engine, if_exists="replace", index=False)
    print("Successfully populated `raw_extracts_table` in postgreSQL datastore")
    conn.close()
