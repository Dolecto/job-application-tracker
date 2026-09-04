from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.db_init import get_db

from models.extracted_job import ExtractedJob
from schemas.extracted_job import ExtractedJobCreate, ExtractedJobResponse
from repositories.extracted_job import ExtractedJobRepository as service


router = APIRouter(prefix = "/extracted_job")


@router.get("", response_model=list[ExtractedJobResponse])
@router.get("/", response_model=list[ExtractedJobResponse])
def get_all(db: Session = Depends(get_db)):
    return service.get_all_jobs(db)


@router.post("", response_model=ExtractedJobResponse)
@router.post("/", response_model=ExtractedJobResponse)
def add_job(job: ExtractedJobCreate, db: Session = Depends(get_db)):
    try:
        return service.insert_job(db, job)
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A job with this posting link already exists."
        )