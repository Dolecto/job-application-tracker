from sqlalchemy import select
from sqlalchemy.orm import Session
from models.extracted_job import ExtractedJob, FilteringStatus

from typing import List

class ExtractedJobRepository:
    @staticmethod
    def get_job_by_id(db: Session, id: int) -> ExtractedJob | None:
        return db.get(ExtractedJob, id)


    # SELECT statements
    # NOTE: check if this is correct or if this can be more efficient
    @staticmethod
    def get_job_by_title(db: Session, job_title: str) -> List[dict] | None:
        stmt = select(ExtractedJob).filter_by(job_title=job_title)
        rows = list(db.execute(stmt))   # row objects
        return [row._asdict() for row in rows]  

    @staticmethod
    def get_job_by_company_name(db: Session, company_name: str) -> List[dict] | None:
        stmt = select(ExtractedJob).filter_by(company_name=company_name)
        rows = list(db.execute(stmt)) 
        return [row._asdict() for row in rows]  

    @staticmethod
    def get_job_by_filtering_status(db: Session, filtering_status: FilteringStatus) -> List[dict] | None:
        stmt = select(ExtractedJob).filter_by(filtering_status=filtering_status)
        rows = list(db.execute(stmt)) 
        return [row._asdict() for row in rows]  