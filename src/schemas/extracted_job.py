"""Pydantic response schemas for ExtractedJob API."""

from pydantic import BaseModel
from models.extracted_job import FilteringStatus 


class ExtractedJobCreate(BaseModel):
    job_title: str
    company_name: str
    emailed_posting_link: str


class ExtractedJobResponse(BaseModel):
    id: int
    job_title: str
    company_name: str
    emailed_posting_link: str
    emailed_posting_link_hash: str
    filtering_status: FilteringStatus 
    created_at: str | None = None

    class Config:
        from_attributes = True