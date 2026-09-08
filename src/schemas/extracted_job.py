"""Pydantic response schemas for ExtractedJob API."""

from pydantic import BaseModel
from models.extracted_job import FilteringStatus 
from datetime import datetime


class ExtractedJobCreate(BaseModel):
    job_title: str
    company_name: str
    emailed_posting_link: str

    def __hash__(self):
        return hash(self.emailed_posting_link)


class ExtractedJobResponse(BaseModel):
    id: int
    job_title: str
    company_name: str
    emailed_posting_link: str
    emailed_posting_link_hash: str
    filtering_status: FilteringStatus 
    created_at: datetime | None = None

    class Config:
        from_attributes = True