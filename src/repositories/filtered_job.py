from sqlalchemy.orm import Session

from models.extracted_job import ExtractedJob, FilteringStatus
from repositories.extracted_job import ExtractedJobRepository


class FilteredJobRepository(ExtractedJobRepository):
    def get_job_by_id(self, db: Session, id: int) -> ExtractedJob | None:
        return super().get_job_by_id(db, id)