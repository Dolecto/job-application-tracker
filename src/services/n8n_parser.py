"""
Parser that takes raw n8n JSON outputs from the "Read Email" workflow and
extracts the data required for the extracted_job table.

NOTE: this is meant for LinkedIn.
"""

from schemas.extracted_job import ExtractedJobCreate

import re
import json
from html import unescape
from urllib.parse import urlparse


# Regex for raw HTML
# TODO: generalize, or create platform-specific regex
_BLOCK_SPLIT_RE = re.compile(r"-{5,}")
_VIEW_JOB_RE = re.compile(r"View job:\s*(\S+)")


class ParserService:
    @staticmethod
    def parsing_pipeline(json_path: str) -> list[ExtractedJobCreate]:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        all_jobs = []

        for email in data:
            jobs = ParserService.parse_json(email.get("text", ""))
            all_jobs = all_jobs + jobs

        all_jobs = list(set(all_jobs))  # TODO: maybe there's a better way

        return all_jobs


    @classmethod
    def parse_json(cls, text: str) -> list[ExtractedJobCreate]:
        """Extract job listings from the 'text' field of one email."""
        if not text:
            return []

        jobs = []

        for block in _BLOCK_SPLIT_RE.split(text):
            link_match = _VIEW_JOB_RE.search(block)
            if not link_match:
                continue  # not a job block

            link = link_match.group(1)
            pre_link_text = block[: link_match.start()]
            lines = [ln.strip() for ln in pre_link_text.splitlines() if ln.strip()]
            lines = [ln for ln in lines if not ln.lower().startswith("your job alert for")]
            if len(lines) < 3:
                continue

            # TODO: pass location to filtered_jobs OR extract during enrichment
            title, company, location = lines[0], lines[1], lines[2]  

            # Extract link without query parameters
            try:
                url = unescape(link)
                parsed = urlparse(url)
                cleaned_link = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            except Exception:
                cleaned_link = link

            job = ExtractedJobCreate(
                job_title=unescape(title),
                company_name=unescape(company),
                emailed_posting_link=cleaned_link
            )

            jobs.append(job)

        return jobs
        



