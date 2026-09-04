from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.extracted_job import ExtractedJob, FilteringStatus
from schemas.extracted_job import ExtractedJobCreate

from typing import List

class ExtractedJobRepository:
    # General GET statements
    @staticmethod
    def get_job_by_id(db: Session, id: int) -> ExtractedJob | None:
        return db.get(ExtractedJob, id)

    @staticmethod
    def get_all_jobs(db: Session) -> List[ExtractedJob] | None:
        stmt = select(ExtractedJob)
        return list(db.execute(stmt).scalars().all())

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


    # INSERT statement
    @staticmethod
    def insert_job(db: Session, extracted_job: ExtractedJobCreate):
        job = ExtractedJob(
            job_title=extracted_job.job_title,
            company_name=extracted_job.company_name,
            emailed_posting_link=extracted_job.emailed_posting_link
        )
        db.add(job)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise
        db.refresh(job)
        return job