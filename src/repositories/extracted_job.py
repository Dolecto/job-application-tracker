from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.extracted_job import ExtractedJob, FilteringStatus
from schemas.extracted_job import ExtractedJobCreate

from typing import List
import hashlib

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
    def get_jobs_by_title(db: Session, job_title: str) -> List[dict] | None:
        stmt = select(ExtractedJob).filter_by(job_title=job_title)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_jobs_by_company_name(db: Session, company_name: str) -> List[dict] | None:
        stmt = select(ExtractedJob).filter_by(company_name=company_name)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_jobs_by_filtering_status(db: Session, filtering_status: FilteringStatus) -> List[dict] | None:
        stmt = select(ExtractedJob).filter_by(filtering_status=filtering_status)
        return list(db.execute(stmt).scalars().all())


    # INSERT statements
    @staticmethod
    def insert_job(db: Session, extracted_job: ExtractedJobCreate):
        # We're checking the hash before insert, otherwise we'll have to loop 
        # through inserts instead of using add_all()
        link_hash = hashlib.sha256(extracted_job.emailed_posting_link.encode("utf-8")).hexdigest()
        exists = db.execute(select(ExtractedJob.id).filter_by(emailed_posting_link_hash=link_hash))
        if exists is not None:
            return None

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
            return None
        db.refresh(job)
        return job

    @staticmethod
    def insert_jobs(db: Session, extracted_jobs: List[ExtractedJobCreate]):
        seen_hashes = set()
        candidates = []

        # Batch deduplication
        for extracted_job in extracted_jobs:
            link_hash = hashlib.sha256(extracted_job.emailed_posting_link.encode("utf-8")).hexdigest()
            if link_hash in seen_hashes:
                continue
            seen_hashes.add(link_hash)
            candidates.append((extracted_job, link_hash))

        # DB deduplication
        existing_hashes = set(
            db.scalars(
                select(ExtractedJob.emailed_posting_link_hash).where(
                    ExtractedJob.emailed_posting_link_hash.in_(seen_hashes)
                )
            ).all()
        )
        jobs = [row[0] for row in candidates if row[1] not in existing_hashes]
        if not jobs:
            return []

        try:
            inserted = db.scalars(insert(ExtractedJob).returning(ExtractedJob), jobs,).all()
            db.commit()
            return list(inserted)
        except IntegrityError:
            # Race condition fallback: retry one at a time
            db.rollback()
            inserted = []
            for job in jobs:
                try:
                    obj = db.scalars(insert(ExtractedJob).returning(ExtractedJob), [job]).one()
                    db.commit()
                    inserted.append(obj)
                except IntegrityError:
                    db.rollback()
            return inserted


    # DELETE statements
    # NOTE: we're not implementing delete_all_jobs() for now...
    @staticmethod
    def delete_all_jobs(db: Session):
        return "TODO"

    @staticmethod
    def delete_job_by_id(db: Session, id: int) -> bool | None:
        job = db.get(ExtractedJob, id)
        if job is None:
            return None
        try:
            db.delete(job)
        except:
            db.rollback()
            return False
        db.commit()
        return True