"""
Legal Draft Generator Models
----------------------------
Pydantic data models for structured inputs and outputs of the pure-Python
Legal Draft Generator.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PartyInput(BaseModel):
    """Detailed party attributes for pleadings."""
    name: str = Field(..., description="Full legal name of person, firm, or entity")
    relation_type: Optional[str] = Field("S/o", description="Relation type: S/o, D/o, W/o, Through Authorised Representative")
    relation_name: Optional[str] = Field(None, description="Name of father/spouse or representative")
    age: Optional[int] = Field(None, description="Age in years")
    occupation: Optional[str] = Field(None, description="Occupation / Business")
    address: str = Field(..., description="Complete residential or registered office address")
    email: Optional[str] = Field(None, description="Email address for e-service")
    phone: Optional[str] = Field(None, description="Contact phone number")
    is_corporate: bool = Field(False, description="True if bank, company, or statutory corporation")
    cin_or_reg: Optional[str] = Field(None, description="CIN, LLPIN, or Company Registration No.")


class AdvocateInput(BaseModel):
    """Advocate / Legal Counsel details."""
    name: str = Field("D. N. Thakur", description="Advocate name")
    bar_council_number: Optional[str] = Field("D/1234/2010", description="Bar Council Enrollment No.")
    office_address: Optional[str] = Field("Chamber No. 456, Saket District Court Complex, New Delhi - 110017")
    email: Optional[str] = Field("advocate.office@lawfirm.in")
    phone: Optional[str] = Field("+91 98765 43210")


class FactItem(BaseModel):
    """A chronological event or factual statement in the pleading."""
    date: Optional[str] = Field(None, description="Date or time period of the event")
    narrative: str = Field(..., description="Detailed description of the fact")
    annexure_label: Optional[str] = Field(None, description="e.g. ANNEXURE P-1")


class ClaimItem(BaseModel):
    """A monetary or specific performance claim item."""
    description: str = Field(..., description="Description of the claim (Principal, Interest, Damages)")
    amount: float = Field(0.0, description="Amount in INR")
    interest_rate_percent: Optional[float] = Field(None, description="Annual interest rate percentage")
    interest_from_date: Optional[str] = Field(None, description="Start date for interest computation")


class PrayerItem(BaseModel):
    """A specific prayer / relief clause sought from the court."""
    clause_letter: str = Field("a", description="e.g. (a), (b), (c)")
    relief_text: str = Field(..., description="Exact relief requested")


class DraftInput(BaseModel):
    """Complete structured input payload for generating a legal draft."""
    template_id: str = Field(
        "commercial_suit",
        description="Template identifier: 'commercial_suit', 'legal_notice', 'bail_application', 'consumer_complaint', 'general_affidavit'",
    )
    court_name: str = Field(
        "IN THE COURT OF THE DISTRICT JUDGE (COMMERCIAL COURT) AT SAKET, NEW DELHI",
        description="Presiding court title and location",
    )
    jurisdiction_title: Optional[str] = Field(
        "COMMERCIAL CIVIL JURISDICTION",
        description="Court jurisdiction heading",
    )
    case_type_number_year: Optional[str] = Field(
        "COMMERCIAL SUIT NO. 233 OF 2024",
        description="Suit / Case number with year",
    )
    cnr_number: Optional[str] = Field(
        None,
        description="CNR number if instituted or linked to an existing case",
    )

    # Parties
    plaintiffs: List[PartyInput] = Field(default_factory=list)
    defendants: List[PartyInput] = Field(default_factory=list)
    advocate: Optional[AdvocateInput] = None

    # Subject & Valuation
    matter_title: Optional[str] = Field(
        None,
        description="Heading title, e.g., 'SUIT FOR RECOVERY OF MONEY UNDER ORDER VII RULE 1 CPC'",
    )
    total_claim_amount: float = Field(0.0, description="Total monetary valuation in INR")

    # Timeline & Causes
    cause_of_action_date: Optional[str] = Field(None, description="When the cause of action first arose")
    cause_of_action_narrative: Optional[str] = Field(None, description="Summary of jurisdiction and cause of action")
    facts: List[FactItem] = Field(default_factory=list)
    claims: List[ClaimItem] = Field(default_factory=list)
    prayers: List[PrayerItem] = Field(default_factory=list)

    # Statutory Disclosures & Affirmation
    sec_12a_compliance: bool = Field(True, description="Pre-Institution Mediation compliance (Commercial Courts Act)")
    court_fee_paid: Optional[float] = Field(None, description="Court fee deposited in INR")
    place: str = Field("New Delhi", description="Location of signing and verification")
    date: Optional[str] = Field(None, description="Date of drafting / signing")


class DraftOutput(BaseModel):
    """Generated legal draft in multiple formats."""
    template_id: str
    template_name: str
    title: str
    plain_text: str
    markdown: str
    html: str
    structured_sections: Dict[str, Any]
    metadata: Dict[str, Any]
