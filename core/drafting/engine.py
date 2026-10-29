"""
Pure-Python Legal Drafting Engine
---------------------------------
Strict constraints satisfied:
- PURE PYTHON ONLY.
- NO LLMs, NO external APIs.
- Takes structured inputs (parties, court, facts, claims, prayers) and produces structured legal drafts.
- Supports rich exports: Plain Text, Markdown, Printable Legal HTML, and Microsoft Word (.docx).
- Includes cross-task bridge to auto-populate drafts directly from scraped eCourts cases!
"""

import io
from datetime import datetime
from typing import Dict, Any, List, Optional

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.drafting.models import (
    DraftInput,
    DraftOutput,
    PartyInput,
    AdvocateInput,
    FactItem,
    ClaimItem,
    PrayerItem,
)
from core.drafting.templates import TEMPLATES_REGISTRY
from core.ecourts.models import ComprehensiveCaseData


class LegalDraftingEngine:
    """
    Pure-Python rule-based template generation engine.
    """

    @classmethod
    def list_templates(cls) -> List[Dict[str, str]]:
        """Returns catalog of registered legal document templates."""
        return [
            {
                "id": tid,
                "name": tcls.NAME,
                "description": tcls.__doc__.strip().split("\n")[0] if tcls.__doc__ else "",
            }
            for tid, tcls in TEMPLATES_REGISTRY.items()
        ]

    @classmethod
    def generate_draft(cls, draft_input: DraftInput) -> DraftOutput:
        """
        Executes pure-Python template generation without external APIs or LLMs.
        """
        template_cls = TEMPLATES_REGISTRY.get(draft_input.template_id)
        if not template_cls:
            template_cls = TEMPLATES_REGISTRY["commercial_suit"]

        result = template_cls.generate(draft_input)

        # Generate styled printable HTML
        html_content = cls._render_printable_html(result["title"], result["plain_text"], draft_input)

        return DraftOutput(
            template_id=result["template_id"],
            template_name=result["template_name"],
            title=result["title"],
            plain_text=result["plain_text"],
            markdown=result["markdown"],
            html=html_content,
            structured_sections=result["structured_sections"],
            metadata={
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "engine": "Pure-Python Rule-Based Legal Assembler (No LLMs)",
                "template_id": result["template_id"],
            },
        )

    @classmethod
    def populate_from_case(cls, case: ComprehensiveCaseData, template_id: str = "commercial_suit") -> DraftInput:
        """
        Cross-Task Synergy Bridge:
        Takes a scraped eCourts case and transforms its parsed fields
        into pre-populated DraftInput parameters for the legal drafting engine.
        """
        # 1. Map Court Details
        court_name = case.case_status.court_number_and_judge or "IN THE DISTRICT COURT"
        if "saket" in court_name.lower():
            court_title = "IN THE COURT OF DISTRICT JUDGE (COMMERCIAL COURT) AT SAKET, NEW DELHI"
        else:
            court_title = f"IN THE COURT OF {court_name.upper()}"

        suit_no = f"{case.case_details.case_type or 'SUIT'}/{case.case_details.registration_number or '2024'}"

        # 2. Map Plaintiffs / Petitioners
        plaintiffs: List[PartyInput] = []
        for p in case.petitioners:
            plaintiffs.append(
                PartyInput(
                    name=p.name,
                    relation_type="Through Authorised Representative" if "bank" in p.name.lower() or "ltd" in p.name.lower() else "S/o",
                    relation_name="Branch Manager" if "bank" in p.name.lower() else "",
                    address=p.address or "Branch Office at District Jurisdiction",
                    is_corporate=bool("bank" in p.name.lower() or "ltd" in p.name.lower()),
                )
            )
        if not plaintiffs:
            plaintiffs.append(PartyInput(name="Petitioner / Plaintiff", address="Address not specified"))

        # 3. Map Defendants / Respondents
        defendants: List[PartyInput] = []
        for r in case.respondents:
            defendants.append(
                PartyInput(
                    name=r.name,
                    relation_type="S/o",
                    address=r.address or "Address within Court Jurisdiction",
                )
            )
        if not defendants:
            defendants.append(PartyInput(name="Respondent / Defendant", address="Address not specified"))

        # 4. Map Advocate
        adv_name = "Advocate"
        for p in case.petitioners:
            if p.advocate:
                adv_name = p.advocate
                break

        advocate = AdvocateInput(
            name=adv_name,
            bar_council_number="D/1234/2012",
            office_address="Chamber No. 512, Lawyers Chambers Block, Saket Courts Complex, New Delhi",
        )

        # 5. Map Facts from Hearing History & Acts
        facts: List[FactItem] = []
        if case.case_details.filing_date:
            facts.append(
                FactItem(
                    date=case.case_details.filing_date,
                    narrative=f"That the present proceedings were instituted under filing number {case.case_details.filing_number or 'N/A'}.",
                )
            )

        if case.acts:
            acts_str = ", ".join([f"{a.act} (Section {a.section or 'General'})" for a in case.acts])
            facts.append(
                FactItem(
                    date=case.case_details.registration_date,
                    narrative=f"That the suit is instituted under the statutory provisions of {acts_str}.",
                )
            )

        # Hearing timeline summary
        for h in case.hearing_history[:4]:
            if h.hearing_date and h.purpose:
                facts.append(
                    FactItem(
                        date=h.hearing_date,
                        narrative=f"The matter was taken up before {h.judge or 'the Hon’ble Court'} for the purpose of '{h.purpose}'.",
                    )
                )

        if not facts:
            facts.append(
                FactItem(
                    date="2024",
                    narrative="Commercial credit facility was granted to the Defendant which remains unpaid despite maturity.",
                )
            )

        # Default Claim Amount for commercial recovery
        claim_amt = 1500000.0  # 15 Lakhs default for demo

        return DraftInput(
            template_id=template_id,
            court_name=court_title,
            jurisdiction_title="COMMERCIAL CIVIL JURISDICTION",
            case_type_number_year=suit_no,
            cnr_number=case.cnr_number,
            plaintiffs=plaintiffs,
            defendants=defendants,
            advocate=advocate,
            matter_title=f"SUIT FOR RECOVERY OF MONEY UNDER ORDER VII RULE 1 CPC READ WITH COMMERCIAL COURTS ACT, 2015",
            total_claim_amount=claim_amt,
            cause_of_action_date=case.case_details.filing_date or "10-05-2024",
            cause_of_action_narrative="arose when the default occurred and continues till full recovery.",
            facts=facts,
            place="New Delhi",
            date=datetime.now().strftime("%d-%m-%Y"),
        )

    @classmethod
    def export_to_docx(cls, draft: DraftOutput) -> bytes:
        """
        Exports the generated draft into a clean, formatted Microsoft Word (.docx) document
        using standard legal margins (1.5 inch left margin for court binding).
        """
        doc = Document()

        # Set standard legal margins: Left 1.5 in (for binding), Right 1 in, Top/Bottom 1.25 in
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1.25)
            section.bottom_margin = Inches(1.25)
            section.left_margin = Inches(1.5)
            section.right_margin = Inches(1.0)

        # Document Header
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title_p.add_run(draft.title.upper())
        run.bold = True
        run.font.size = Pt(13)
        run.font.name = "Times New Roman"

        doc.add_paragraph()  # spacer

        # Split text into paragraphs
        lines = draft.plain_text.split("\n\n")
        for para_text in lines:
            clean_text = para_text.strip()
            if not clean_text:
                continue

            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.5  # Standard 1.5 line spacing for court pleadings
            p.paragraph_format.space_after = Pt(6)

            # Center headers
            if any(h in clean_text for h in ["IN THE COURT OF", "VERSUS", "MOST RESPECTFULLY SHOWETH:", "PRAYER", "VERIFICATION", "STATEMENT OF TRUTH"]):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(clean_text)
                r.bold = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                r = p.add_run(clean_text)
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)

        out_stream = io.BytesIO()
        doc.save(out_stream)
        return out_stream.getvalue()

    @staticmethod
    def _render_printable_html(title: str, plain_text: str, data: DraftInput) -> str:
        """
        Renders clean, printable HTML document styled according to Indian legal drafting standards
        (Times New Roman, 1.5 line height, justification, proper signature lines).
        """
        paragraphs_html = ""
        for block in plain_text.split("\n\n"):
            clean = block.strip()
            if not clean:
                continue
            if any(h in clean for h in ["IN THE COURT OF", "VERSUS", "MOST RESPECTFULLY SHOWETH:", "PRAYER", "VERIFICATION:", "STATEMENT OF TRUTH"]):
                paragraphs_html += f"<div class='court-heading' style='text-align:center; font-weight:bold; margin: 16px 0;'>{clean.replace(chr(10), '<br/>')}</div>"
            else:
                paragraphs_html += f"<p style='text-align:justify; text-indent:30px; margin-bottom:12px;'>{clean.replace(chr(10), '<br/>')}</p>"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{
    font-family: 'Times New Roman', Times, serif;
    font-size: 14pt;
    line-height: 1.6;
    color: #111;
    margin: 40px auto;
    max-width: 800px;
    padding: 20px 40px;
    background: #fff;
  }}
  @media print {{
    body {{
      margin: 0;
      padding: 0;
    }}
  }}
  h1, h2, h3, h4 {{
    text-align: center;
    font-weight: bold;
    margin-top: 10px;
    margin-bottom: 10px;
  }}
  p {{
    text-align: justify;
    margin-bottom: 14px;
  }}
  .signature-box {{
    margin-top: 40px;
    display: flex;
    justify-content: space-between;
  }}
  .divider {{
    border-top: 1px solid #999;
    margin: 30px 0;
  }}
</style>
</head>
<body>
  {paragraphs_html}
</body>
</html>"""

