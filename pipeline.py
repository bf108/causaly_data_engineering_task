import sqlite3
from pathlib import Path

from causaly.src.batch_pipeline_utils import create_connection
from causaly.src.batch_pipeline_utils import groupby_keyword_count_unique_ids
from causaly.src.batch_pipeline_utils import parse_all_meeting_abstracts


if __name__ == "__main__":
    parent_dir = Path(__file__).parent
    conn = create_connection("data/meeting_abstracts.db")
    assert isinstance(conn, sqlite3.Connection), "Failed to create sqlite3 connection"
    meetings_data = str(parent_dir / "data/SpaceLifeSciences.xml")
    df = parse_all_meeting_abstracts(meetings_data)
    df.to_sql("raw_extracts_table", conn, if_exists="replace", index=False)
    df_gb = groupby_keyword_count_unique_ids(df)
    # Write grouped table to sqlite3 database
    df_gb.to_sql("keyword_pair_frequency_table", conn, if_exists="replace", index=False)
    conn.close()
    print("Pipeline completed successfully")
