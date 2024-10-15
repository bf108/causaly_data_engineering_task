import psycopg2
from fastapi import FastAPI

from data_pipeline_app.pipeline_utils.batch_pipeline_utils import (
    get_keyword_pairs_from_meeting_abstract,
)
from data_pipeline_app.pipeline_utils.batch_pipeline_utils import standardize_string
from data_pipeline_app.pipeline_utils.sql_db_utils import (
    get_most_occurring_keywords_from_sql,
)
from data_pipeline_app.pipeline_utils.sql_db_utils import is_meeting_in_table
from data_pipeline_app.pipeline_utils.sql_db_utils import update_data_store
from data_pipeline_app.pipeline_utils.sql_db_utils import update_keyword_pairs_table


app = FastAPI()


@app.post("/get_most_occurring_keywords")
async def get_most_occurring_keywords(keyword: str):
    conn = psycopg2.connect(
        host="postgres-datastore",
        database="datastore",
        user="user",
        password="password",
    )
    keyword_standardized = standardize_string(keyword)
    if not conn:
        return {"message": "Failed to create sqlite3 connection"}
    most_occurring_keywords = get_most_occurring_keywords_from_sql(
        conn, keyword_standardized
    )
    conn.close()
    return {"most_occurring_keywords": most_occurring_keywords}


@app.post("/add_meeting_abstract")
async def add_meeting_abstract(meeting_abstract: str):
    conn = psycopg2.connect(
        host="postgres-datastore",
        database="datastore",
        user="user",
        password="password",
    )
    keyword_pairs = get_keyword_pairs_from_meeting_abstract(meeting_abstract)
    if len(keyword_pairs) == 0:
        return {"message": "No keyword pairs found in meeting abstract"}
    nlm_dcms_id = keyword_pairs[0].nlm_dcms_id
    if is_meeting_in_table(conn, nlm_dcms_id):
        conn.close()
        return {"message": "Meeting abstract already exists in the database"}
    print("Updating keyword_pairs_table")
    update_keyword_pairs_table(conn, keyword_pairs)
    print("Updating keyword_pair_frequency_table")
    update_data_store(conn, keyword_pairs)
    conn.close()
    return {"message": f"Meeting abstract {nlm_dcms_id} added successfully"}
