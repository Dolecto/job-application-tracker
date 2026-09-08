"""Model for jobs extracted from emails."""

from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import validates, Mapped, mapped_column
from sqlalchemy.sql import func

import hashlib
import enum

from database.db_init import Base


class FilteringStatus(enum.Enum):
    pending = "pending"
    processed = "processed"
    passed = "passed"
    rejected = "rejected"
    failed = "failed"


class ExtractedJob(Base):
    __tablename__ = "extracted_jobs"

    id = Column(Integer, primary_key=True)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    emailed_posting_link = Column(String(1024), nullable=False)
    emailed_posting_link_hash: Mapped[str] = mapped_column(String(64))
    filtering_status = Column(Enum(FilteringStatus), nullable=False, default=FilteringStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @validates("emailed_posting_link")
    def _set_link_hash(self, key, value):
        self.emailed_posting_link_hash = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return value