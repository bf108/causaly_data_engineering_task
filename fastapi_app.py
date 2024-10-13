import sqlite3
from pathlib import Path

from fastapi import FastAPI
from src.batch_pipeline_utils import standardize_string


app = FastAPI()


def get_most_occurring_keywords_from_sql(search_string: str) -> list[str]:
    parent_dir = Path(__file__).parent
    conn = sqlite3.connect(parent_dir / "data/meeting_abstracts.db")
    cursor = conn.cursor()
    top_keyword_pairs = cursor.execute(
        f"SELECT keyword_2 FROM keyword_pair_frequency_table WHERE keyword_1 = '{search_string}'"
        f"AND frequency = (SELECT MAX(frequency) FROM keyword_pair_frequency_table WHERE keyword_1 = '{search_string}')"
        f"ORDER BY keyword_2 ASC"
    )
    top_matches = [kw[0] for kw in top_keyword_pairs]
    return top_matches


@app.post("/get_most_occurring_keywords")
async def get_most_occurring_keywords(keyword: str):
    keyword_standardized = standardize_string(keyword)
    most_occurring_keywords = get_most_occurring_keywords_from_sql(keyword_standardized)
    return {"most_occurring_keywords": most_occurring_keywords}


@app.post("/add_meeting_abstract")
async def add_meeting_abstract(meeting_abstract):
    return {"message": "Meeting abstract added successfully"}
