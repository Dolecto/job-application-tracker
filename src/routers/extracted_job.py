from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.db_init import get_db

from models.extracted_job import ExtractedJob, FilteringStatus
from schemas.extracted_job import ExtractedJobCreate, ExtractedJobResponse
from repositories.extracted_job import ExtractedJobRepository as repo


router = APIRouter(prefix = "/extracted_job")


# GET operations
@router.get("", response_model=list[ExtractedJobResponse])
@router.get("/", response_model=list[ExtractedJobResponse])
def get_all(db: Session = Depends(get_db)):
    return repo.get_all_jobs(db)

@router.get("/id/{id}", response_model=ExtractedJobResponse)
def get_job_by_id(id: int, db: Session = Depends(get_db)):
    job = repo.get_job_by_id(db, id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/title/{title}", response_model=list[ExtractedJobResponse])
def get_jobs_by_title(title: str, db: Session = Depends(get_db)):
    return repo.get_jobs_by_title(db, title)

@router.get("/company/{company_name}", response_model=list[ExtractedJobResponse])
def get_jobs_by_company_name(company_name: str, db: Session = Depends(get_db)):
    return repo.get_jobs_by_company_name(db, company_name)

@router.get("/status/{filtering_status}", response_model=list[ExtractedJobResponse])
def get_jobs_by_filtering_status(filtering_status: FilteringStatus, db: Session = Depends(get_db)):
    return repo.get_jobs_by_filtering_status(db, filtering_status)


# POST operations
@router.post("", response_model=ExtractedJobResponse)
@router.post("/", response_model=ExtractedJobResponse)
def add_job(job: ExtractedJobCreate, db: Session = Depends(get_db)):
    try:
        return repo.insert_job(db, job)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A job with this posting link already exists."
        )