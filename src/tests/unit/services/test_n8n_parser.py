from services.n8n_parser import ParserService as service
from repositories.extracted_job import ExtractedJobRepository
from database.db_init import get_db

from sqlalchemy.orm import Session
from fastapi import Depends

db = get_db()

JSON_PATH = "../../fixtures/fixture_n8n_output.json"


things = service.parsing_pipeline(JSON_PATH)

"""

for thing in things:
    ExtractedJobRepository.insert_job(db, thing)
"""

from contextlib import contextmanager
from database.db_init import SessionLocal

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

with get_db_session() as db:
    ExtractedJobRepository.insert_jobs(db, things)

