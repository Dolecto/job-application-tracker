"""
Job Posting Finder
------------------
Given a job title + company, search the web via Tavily, locate the most
likely official job posting, and extract structured fields (link, location,
salary, responsibilities) using an LLM with structured output.

Install:
    pip install -U langchain langchain-tavily langchain-openai pydantic

Env vars required:
    TAVILY_API_KEY
    OPENAI_API_KEY   (or swap in another chat model, see NOTE below)
"""

import os
from typing import Optional, List
from urllib.parse import urlparse

from pydantic import BaseModel, Field
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# ---------------------------------------------------------------------------
# 1. Input template
# ---------------------------------------------------------------------------
class JobQuery(BaseModel):
    job_title: str
    company: str


# ---------------------------------------------------------------------------
# 2. Output schema — this is what gets returned to the caller
# ---------------------------------------------------------------------------
class JobPostingResult(BaseModel):
    company_posting_link: Optional[str] = Field(
        None, description="URL of the job posting, ideally on the company's own careers site."
    )
    location: Optional[str] = Field(None, description="Job location, e.g. 'Remote' or 'Austin, TX'.")
    salary: Optional[str] = Field(
        None, description="Salary or pay range as stated in the posting. Null if not disclosed."
    )
    responsibilities: List[str] = Field(
        default_factory=list, description="Bullet-point list of key responsibilities."
    )
    source_confidence: str = Field(
        description="'high' if this looks like the company's own posting, "
                    "'low' if it's an aggregator (LinkedIn/Indeed/etc.) or uncertain."
    )
    notes: Optional[str] = Field(
        None, description="Any caveats, e.g. 'multiple postings found', 'posting may be expired'."
    )


# ---------------------------------------------------------------------------
# 3. Search step
# ---------------------------------------------------------------------------
def search_job_postings(query: JobQuery, max_results: int = 8):
    """Run a Tavily search and pull back candidate pages with raw content."""
    search_tool = TavilySearch(
        max_results=max_results,
        topic="general",
        include_raw_content="markdown",   # gets us page text to extract from
        include_answer=False,
    )
    search_query = f'"{query.job_title}" "{query.company}" job posting careers'
    results = search_tool.invoke({"query": search_query})
    # TavilySearch returns a dict with a "results" list of {url, title, content, raw_content, score, ...}
    return results.get("results", [])


# ---------------------------------------------------------------------------
# 4. Ranking step — prefer the company's own domain over aggregators
# ---------------------------------------------------------------------------
AGGREGATOR_DOMAINS = {
    "linkedin.com", "indeed.com", "glassdoor.com", "ziprecruiter.com",
    "monster.com", "simplyhired.com", "levels.fyi", "builtin.com",
}

def guess_company_domain(company: str) -> Optional[str]:
    """
    Cheap heuristic: not reliable on its own. In production, resolve this via
    a company-domain lookup (Clearbit, a search of '{company} official site',
    or a maintained internal mapping) rather than guessing.
    """
    normalized = "".join(ch for ch in company.lower() if ch.isalnum())
    return f"{normalized}.com"

def rank_candidates(candidates: list, company: str) -> list:
    likely_domain = guess_company_domain(company)
    def score(c):
        domain = urlparse(c["url"]).netloc.replace("www.", "")
        s = c.get("score", 0)
        if domain in AGGREGATOR_DOMAINS:
            s -= 1.0          # deprioritize aggregators
        if likely_domain and likely_domain in domain:
            s += 1.0          # boost likely company domain
        return s
    return sorted(candidates, key=score, reverse=True)


# ---------------------------------------------------------------------------
# 5. Extraction step — LLM turns raw page content into structured fields
# ---------------------------------------------------------------------------
EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You extract structured job-posting data from raw web page content. "
     "Only use information explicitly present in the text. If a field isn't "
     "stated, return null (or an empty list for responsibilities) — never "
     "guess or infer typical values for the role."),
    ("human",
     "Job title: {job_title}\nCompany: {company}\nSource URL: {url}\n\n"
     "Page content:\n{content}\n\n"
     "Extract the job posting details.")
])

# NOTE: swap ChatOpenAI for ChatAnthropic, ChatGoogleGenerativeAI, etc. as needed.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
extractor = llm.with_structured_output(JobPostingResult)

def extract_from_candidate(query: JobQuery, candidate: dict) -> JobPostingResult:
    content = candidate.get("raw_content") or candidate.get("content") or ""
    content = content[:12000]  # crude token-budget guard; chunk/summarize for long pages
    chain = EXTRACTION_PROMPT | extractor
    result = chain.invoke({
        "job_title": query.job_title,
        "company": query.company,
        "url": candidate["url"],
        "content": content,
    })
    result.company_posting_link = candidate["url"]
    return result


# ---------------------------------------------------------------------------
# 6. Orchestration
# ---------------------------------------------------------------------------
def find_job_posting(job_title: str, company: str) -> JobPostingResult:
    query = JobQuery(job_title=job_title, company=company)
    candidates = search_job_postings(query)

    if not candidates:
        return JobPostingResult(
            source_confidence="low",
            notes="No search results found for this job title/company combination.",
        )

    ranked = rank_candidates(candidates, company)
    top = ranked[0]

    result = extract_from_candidate(query, top)

    domain = urlparse(top["url"]).netloc.replace("www.", "")
    likely_domain = guess_company_domain(company)
    if domain in AGGREGATOR_DOMAINS or (likely_domain and likely_domain not in domain):
        result.source_confidence = "low"
        result.notes = (result.notes or "") + " Best match is not clearly the company's own site."

    return result


if __name__ == "__main__":
    result = find_job_posting("Senior Backend Engineer", "Stripe")
    print(result.model_dump_json(indent=2))