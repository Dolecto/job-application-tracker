"""Model for jobs after enrichment and filtering."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from database.db_init import Base


class FilteredJob(Base):
    __tablename__ = "filtered_jobs"

    id = Column(Integer, primary_key=True)
    extracted_job_id = Column(Integer, ForeignKey("extracted_jobs.id", ondelete="CASCADE"), nullable=False, unique=True)
    company_posting_link = Column(String(1024), nullable=True)
    location = Column(String(255), nullable=True)
    listed_salary = Column(String(255), nullable=True)
    tech_stack = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())