"""
Unit Tests: Legal Draft Generator
---------------------------------
Tests the currency/words engine, template assembler, exports, and case bridge.
"""

import pytest
from core.drafting.num_to_words import number_to_indian_words, format_indian_currency
from core.drafting.models import DraftInput, PartyInput, FactItem
from core.drafting.engine import LegalDraftingEngine
from core.ecourts.sample_data import get_fallback_case_by_cnr


def test_indian_numbers_to_words():
    """Verify Indian numbering conversions."""
    assert number_to_indian_words(0) == "Zero"
    assert number_to_indian_words(100) == "One Hundred"
    assert number_to_indian_words(1500) == "One Thousand Five Hundred"
    assert number_to_indian_words(100000) == "One Lakh"
    assert number_to_indian_words(2500000) == "Twenty Five Lakh"
    assert number_to_indian_words(10000000) == "One Crore"


def test_indian_currency_formatter():
    """Verify formatting of monetary amounts."""
    res = format_indian_currency(2450000)
    assert "Rs. 24,50,000/-" in res
    assert "Twenty Four Lakh Fifty Thousand" in res


def test_list_templates():
    """Verify registered templates are listed."""
    templates = LegalDraftingEngine.list_templates()
    assert len(templates) >= 5
    ids = [t["id"] for t in templates]
    assert "commercial_suit" in ids
    assert "legal_notice" in ids
    assert "bail_application" in ids
    assert "consumer_complaint" in ids
    assert "general_affidavit" in ids


def test_commercial_suit_generation():
    """Verify Commercial Suit plaint generation and statutory clauses."""
    d_input = DraftInput(
        template_id="commercial_suit",
        court_name="IN THE COURT OF DISTRICT JUDGE, SAKET",
        plaintiffs=[PartyInput(name="Punjab National Bank", address="Saket, New Delhi", is_corporate=True)],
        defendants=[PartyInput(name="Sunil Kumar", address="Saket, New Delhi")],
        total_claim_amount=2450000.0,
        facts=[FactItem(date="10-05-2024", narrative="Credit defaulted by Defendant.")],
    )
    draft = LegalDraftingEngine.generate_draft(d_input)

    assert draft.template_id == "commercial_suit"
    assert "PUNJAB NATIONAL BANK" in draft.plain_text
    assert "SUNIL KUMAR" in draft.plain_text
    assert "SECTION 12A" in draft.plain_text.upper()  # Commercial Courts Act mediation
    assert "STATEMENT OF TRUTH" in draft.plain_text.upper()  # Order VI Rule 15A CPC
    assert "Rs. 24,50,000/-" in draft.plain_text


def test_docx_export():
    """Verify generation of valid .docx file bytes."""
    d_input = DraftInput(
        template_id="commercial_suit",
        plaintiffs=[PartyInput(name="Bank Ltd", address="Delhi")],
        defendants=[PartyInput(name="Borrower", address="Delhi")],
        total_claim_amount=500000.0,
    )
    draft = LegalDraftingEngine.generate_draft(d_input)
    docx_bytes = LegalDraftingEngine.export_to_docx(draft)

    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 10000  # Non-empty docx binary


def test_case_to_draft_prefill_bridge():
    """Verify that a scraped case can be seamlessly bridged into a legal draft."""
    case = get_fallback_case_by_cnr("DLST010047302024")
    prefilled_input = LegalDraftingEngine.populate_from_case(case)

    assert prefilled_input.plaintiffs[0].name == "Punjab National Bank"
    assert prefilled_input.defendants[0].name == "Sunil Kumar"
    assert prefilled_input.cnr_number == "DLST010047302024"

    draft = LegalDraftingEngine.generate_draft(prefilled_input)
    assert "PUNJAB NATIONAL BANK" in draft.plain_text
    assert "SUNIL KUMAR" in draft.plain_text

