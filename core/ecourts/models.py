"""
eCourts Data Models
-------------------
Defines Pydantic models for structured representation of district court case data.
Covers all facets displayed on the eCourts District Court portal:
- Case Details (Type, Filing/Registration numbers, Dates, CNR)
- Case Status (First/Next hearing, Stage, Court Number & Judge)
- Parties & Advocates (Petitioners, Respondents)
- Acts & Sections
- Hearing History (Chronological timeline of hearings)
- Orders & Judgments (Interim and final orders with PDF links)
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CaseDetails(BaseModel):
    """Core identification and filing details of the case."""
    case_type: Optional[str] = Field(None, description="Type of case, e.g., CS (COMM)")
    filing_number: Optional[str] = Field(None, description="Case filing number with year")
    filing_date: Optional[str] = Field(None, description="Date when case was filed")
    registration_number: Optional[str] = Field(None, description="Official registration number with year")
    registration_date: Optional[str] = Field(None, description="Date of registration")
    cnr_number: str = Field(..., description="16-character unique CNR number")


class CaseStatus(BaseModel):
    """Current procedural status and stage of the case."""
    first_hearing_date: Optional[str] = Field(None, description="Date of first hearing")
    next_hearing_date: Optional[str] = Field(None, description="Scheduled next hearing date, if pending")
    decision_date: Optional[str] = Field(None, description="Date of disposal/judgment if disposed")
    case_stage: Optional[str] = Field(None, description="Current procedural stage")
    nature_of_disposal: Optional[str] = Field(None, description="Disposal reason if closed")
    court_number_and_judge: Optional[str] = Field(None, description="Presiding judge designation and courtroom")
    state: Optional[str] = Field(None, description="State of the court")
    district: Optional[str] = Field(None, description="District of the court")
    court_complex: Optional[str] = Field(None, description="Court Complex name")
    court_establishment: Optional[str] = Field(None, description="Establishment name")


class Party(BaseModel):
    """Details of a petitioner or respondent, including their legal counsel."""
    name: str = Field(..., description="Name of the party (individual, bank, or company)")
    advocate: Optional[str] = Field(None, description="Name of representing advocate")
    address: Optional[str] = Field(None, description="Address if available in public records")
    sequence: int = Field(1, description="Order index of the party")


class ActSection(BaseModel):
    """Legal act and section under which the case is instituted."""
    act: str = Field(..., description="Name of the act (e.g., Commercial Courts Act, 2015)")
    section: Optional[str] = Field(None, description="Applicable sections")


class HearingHistoryItem(BaseModel):
    """A single record from the chronological history of case hearings."""
    judge: Optional[str] = Field(None, description="Judge presiding over this hearing")
    business_on_date: Optional[str] = Field(None, description="Date when business took place")
    hearing_date: Optional[str] = Field(None, description="Date of the hearing")
    purpose: Optional[str] = Field(None, description="Procedural purpose (e.g., Arguments, Order, Disposed)")


class CourtOrder(BaseModel):
    """An interim or final order/judgment issued by the court."""
    order_number: Optional[str] = Field(None, description="Sequential order number")
    order_date: str = Field(..., description="Date of the order")
    order_details: str = Field(..., description="Description (e.g., COPY OF ORDER, COPY OF JUDGMENT)")
    pdf_url: Optional[str] = Field(None, description="Direct or relative URL to the order PDF")
    is_judgment: bool = Field(False, description="True if marked as final judgment")


class CaseSummary(BaseModel):
    """Brief summary record returned in case list search before drilling down."""
    sr_no: Optional[str] = None
    case_type_number_year: str
    parties_vs: str
    cnr_number: Optional[str] = None
    view_params: Optional[Dict[str, Any]] = None


class ComprehensiveCaseData(BaseModel):
    """
    Complete structured representation of a court case returned by the scraper.
    """
    cnr_number: str
    case_details: CaseDetails
    case_status: CaseStatus
    petitioners: List[Party] = Field(default_factory=list)
    respondents: List[Party] = Field(default_factory=list)
    acts: List[ActSection] = Field(default_factory=list)
    hearing_history: List[HearingHistoryItem] = Field(default_factory=list)
    orders: List[CourtOrder] = Field(default_factory=list)
    source: str = Field("live", description="'live' if fetched from eCourts, 'mock' if resilience fallback")
    retrieved_at: str = Field(..., description="ISO 8601 timestamp of data extraction")
