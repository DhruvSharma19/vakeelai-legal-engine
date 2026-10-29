"""
Commercial Civil Suit Plaint Template
-------------------------------------
Instituted under Order VII Rule 1 of the Code of Civil Procedure, 1908
read with Section 6 of the Commercial Courts Act, 2015.

Directly pairs with eCourts commercial suit filings (e.g. Saket Court Commercial Suits).
Includes:
- Court Header & Memo of Parties
- Comprehensive numbered factual averments
- Section 12A Pre-Institution Mediation averment
- Limitation & Jurisdiction clauses
- Valuation & Court Fee statement
- Itemized Prayer clause
- Verification clause
- Statement of Truth under Order VI Rule 15A CPC (Commercial Courts Act)
"""

from datetime import datetime
from typing import Dict, Any, List
from core.drafting.models import DraftInput
from core.drafting.num_to_words import format_indian_currency


class CommercialSuitTemplate:
    """
    Generates a high-court/district-court grade Commercial Suit Plaint.
    """

    TEMPLATE_ID = "commercial_suit"
    NAME = "Commercial Civil Suit Plaint (Order VII CPC & Commercial Courts Act, 2015)"

    @classmethod
    def generate(cls, data: DraftInput) -> Dict[str, Any]:
        cur_date = data.date or datetime.now().strftime("%d-%m-%Y")
        claim_formatted = format_indian_currency(data.total_claim_amount) if data.total_claim_amount > 0 else "Rs. Nil"

        # 1. Header & Title
        court_header = data.court_name.upper()
        jurisdiction = (data.jurisdiction_title or "COMMERCIAL CIVIL JURISDICTION").upper()
        suit_no = (data.case_type_number_year or "COMMERCIAL SUIT NO. _____ OF 2024").upper()
        cnr_line = f"CNR NO. {data.cnr_number}\n" if data.cnr_number else ""

        # 2. Parties Memo
        plaintiffs_text = cls._format_parties_memo(data.plaintiffs, "PLAINTIFF")
        defendants_text = cls._format_parties_memo(data.defendants, "DEFENDANT")

        # 3. Subject Matter Title
        matter_title = data.matter_title or (
            f"SUIT FOR RECOVERY OF {claim_formatted} ALONG WITH PENDENTE LITE AND FUTURE INTEREST "
            f"UNDER ORDER VII RULE 1 OF THE CODE OF CIVIL PROCEDURE, 1908 READ WITH THE COMMERCIAL COURTS ACT, 2015"
        )

        # 4. Numbered Paragraphs (Averments)
        paragraphs: List[str] = []

        # Intro paras
        p1 = data.plaintiffs[0].name if data.plaintiffs else "The Plaintiff"
        d1 = data.defendants[0].name if data.defendants else "The Defendant"

        paragraphs.append(
            f"1. That the Plaintiff, {p1}, is a body corporate / entity carrying on lawful commercial business "
            f"having its registered/branch office at {data.plaintiffs[0].address if data.plaintiffs else 'as stated in the memo of parties'}. "
            f"The present suit is instituted through its duly authorized representative who is conversant with the facts of the case."
        )

        paragraphs.append(
            f"2. That the Defendant, {d1}, is an individual/business carrying on trade/residing at "
            f"{data.defendants[0].address if data.defendants else 'as stated in the memo of parties'}."
        )

        # Facts timeline
        para_idx = 3
        if data.facts:
            for fact in data.facts:
                date_prefix = f"On or about {fact.date}, " if fact.date else ""
                annexure_suffix = f" (marked and annexed herewith as {fact.annexure_label})" if fact.annexure_label else ""
                paragraphs.append(f"{para_idx}. {date_prefix}{fact.narrative}{annexure_suffix}.")
                para_idx += 1
        else:
            paragraphs.append(
                f"{para_idx}. That the Plaintiff and Defendant entered into commercial transactions whereby goods/credit facilities "
                f"were extended to the Defendant upon the terms and covenants agreed between the parties."
            )
            para_idx += 1
            paragraphs.append(
                f"{para_idx}. That the Defendant failed to discharge their outstanding contractual liabilities, despite repeated requests, "
                f"demands, and legal notices issued on behalf of the Plaintiff."
            )
            para_idx += 1

        # Claim Breakdown
        if data.claims:
            claim_desc = "; ".join([f"{c.description}: {format_indian_currency(c.amount)}" for c in data.claims])
            paragraphs.append(
                f"{para_idx}. That as on the date of filing of the present suit, an aggregate sum of {claim_formatted} "
                f"is lawfully due and recoverable from the Defendant, broken down as follows: {claim_desc}."
            )
            para_idx += 1

        # Pre-institution Mediation (Sec 12A Commercial Courts Act)
        if data.sec_12a_compliance:
            paragraphs.append(
                f"{para_idx}. That the Plaintiff complied with the mandatory requirements of Section 12A of the Commercial Courts Act, 2015 "
                f"by participating in pre-institution mediation before the concerned District Legal Services Authority (DLSA). "
                f"A Non-Starter Report has been duly issued by the DLSA and is annexed herewith."
            )
            para_idx += 1

        # Cause of Action
        coa_date = data.cause_of_action_date or "upon default of payment"
        coa_narrative = data.cause_of_action_narrative or (
            f"arose when credit was extended, and subsequently on {coa_date} when the Defendant failed to pay, "
            f"and continues to subsist de die in diem until full realization."
        )
        paragraphs.append(f"{para_idx}. That the cause of action for the present suit {coa_narrative}")
        para_idx += 1

        # Jurisdiction & Limitation
        paragraphs.append(
            f"{para_idx}. That the cause of action arose within the territorial jurisdiction of this Hon'ble Court as the transactions "
            f"were negotiated, executed, and payable within its jurisdiction. Furthermore, the suit is well within the period of "
            f"limitation prescribed under the Limitation Act, 1963."
        )
        para_idx += 1

        # Valuation & Court Fee
        fee_amount = data.court_fee_paid or (data.total_claim_amount * 0.02)
        paragraphs.append(
            f"{para_idx}. That the value of the suit for the purposes of court fee and jurisdiction is fixed at {claim_formatted}, "
            f"on which requisite ad valorem court fee of {format_indian_currency(fee_amount)} has been deposited."
        )
        para_idx += 1

        # 5. Prayer Clause
        prayer_clauses: List[str] = []
        if data.prayers:
            for p in data.prayers:
                prayer_clauses.append(f"({p.clause_letter}) {p.relief_text}")
        else:
            prayer_clauses = [
                f"(a) Pass a decree for a sum of {claim_formatted} in favour of the Plaintiff and against the Defendant;",
                f"(b) Award pendente lite and future interest at the rate of 18% per annum from the date of filing till realization;",
                f"(c) Award costs of the suit in favour of the Plaintiff;",
                f"(d) Pass such other and further order(s) as this Hon'ble Court may deem fit and proper in the interest of justice.",
            ]

        # 6. Verification
        verification_text = (
            f"I, the Authorized Representative of the Plaintiff, do hereby solemnly verify at {data.place} on this "
            f"{cur_date} that the contents of paragraphs 1 to {para_idx - 1} are true and correct to my knowledge and "
            f"derived from the official records maintained by the Plaintiff in the ordinary course of business, "
            f"legal advice received and believed to be true. No part of it is false and nothing material has been concealed therefrom."
        )

        # 7. Statement of Truth (Commercial Courts Act)
        statement_of_truth = (
            f"STATEMENT OF TRUTH UNDER ORDER VI RULE 15A CPC\n"
            f"--------------------------------------------------\n"
            f"1. I am the authorized representative of the Plaintiff and am competent to swear this affidavit.\n"
            f"2. I say that the statements made in the plaint are based on facts and documents within my knowledge.\n"
            f"3. I say that all documents in the power, possession, control or custody of the Plaintiff relating to "
            f"the commercial dispute have been disclosed and listed in the plaint.\n"
            f"4. I verify that the contents of this statement of truth are true and correct.\n\n"
            f"Verified at {data.place} on {cur_date}.\n\n"
            f"DEPONENT"
        )

        # Assemble plain text & markdown
        body_text = "\n\n".join(paragraphs)
        prayers_text = "\n".join(prayer_clauses)

        plain_text = (
            f"{court_header}\n"
            f"{jurisdiction}\n"
            f"{suit_no}\n"
            f"{cnr_line}\n"
            f"IN THE MATTER OF:\n\n"
            f"{plaintiffs_text}\n"
            f"...PLAINTIFF(S)\n\n"
            f"VERSUS\n\n"
            f"{defendants_text}\n"
            f"...DEFENDANT(S)\n\n"
            f"{matter_title}\n\n"
            f"MOST RESPECTFULLY SHOWETH:\n\n"
            f"{body_text}\n\n"
            f"PRAYER\n"
            f"Wherefore, it is most respectfully prayed that this Hon'ble Court may graciously be pleased to:\n\n"
            f"{prayers_text}\n\n"
            f"PLAINTIFF\n\n"
            f"THROUGH COUNSEL\n"
            f"{data.advocate.name if data.advocate else 'ADVOCATE'}\n"
            f"{data.advocate.office_address if data.advocate else ''}\n"
            f"Enrollment No: {data.advocate.bar_council_number if data.advocate else ''}\n\n"
            f"VERIFICATION:\n"
            f"{verification_text}\n\n"
            f"DEPONENT\n\n"
            f"{statement_of_truth}"
        )

        markdown = (
            f"### {court_header}\n"
            f"**{jurisdiction}**  \n"
            f"**{suit_no}**  \n"
            f"{f'**CNR:** `{data.cnr_number}`  ' if data.cnr_number else ''}\n\n"
            f"#### IN THE MATTER OF:\n\n"
            f"{plaintiffs_text}  \n"
            f"**...PLAINTIFF(S)**\n\n"
            f"**VERSUS**\n\n"
            f"{defendants_text}  \n"
            f"**...DEFENDANT(S)**\n\n"
            f"---\n\n"
            f"#### **{matter_title}**\n\n"
            f"**MOST RESPECTFULLY SHOWETH:**\n\n"
            + "\n\n".join([f"> {p}" for p in paragraphs])
            + f"\n\n### **PRAYER**\n\n"
            f"Wherefore, it is most respectfully prayed that this Hon'ble Court may graciously be pleased to:\n\n"
            + "\n".join([f"* **{p}**" for p in prayer_clauses])
            + f"\n\n---\n\n"
            f"**PLAINTIFF**  \n"
            f"*Through Counsel:*  \n"
            f"**{data.advocate.name if data.advocate else 'Advocate'}**  \n"
            f"*{data.advocate.office_address if data.advocate else ''}*  \n"
            f"Bar Reg: `{data.advocate.bar_council_number if data.advocate else ''}`\n\n"
            f"### **VERIFICATION**\n\n"
            f"{verification_text}\n\n"
            f"**DEPONENT**\n\n"
            f"---\n\n"
            f"### **STATEMENT OF TRUTH**\n*(Under Order VI Rule 15A of CPC)*\n\n"
            f"```text\n{statement_of_truth}\n```"
        )

        return {
            "template_id": cls.TEMPLATE_ID,
            "template_name": cls.NAME,
            "title": matter_title,
            "plain_text": plain_text,
            "markdown": markdown,
            "structured_sections": {
                "court_header": court_header,
                "jurisdiction": jurisdiction,
                "suit_no": suit_no,
                "plaintiffs": [p.model_dump() for p in data.plaintiffs],
                "defendants": [d.model_dump() for d in data.defendants],
                "matter_title": matter_title,
                "paragraphs": paragraphs,
                "prayers": prayer_clauses,
                "verification": verification_text,
                "statement_of_truth": statement_of_truth,
            },
        }

    @staticmethod
    def _format_parties_memo(parties: List[Any], party_role: str) -> str:
        if not parties:
            return f"1. [Name of {party_role}]"
        lines = []
        for idx, p in enumerate(parties, 1):
            rel = f", {p.relation_type} {p.relation_name}" if p.relation_name else ""
            age = f", Aged about {p.age} years" if p.age else ""
            lines.append(f"{idx}. {p.name.upper()}{rel}{age}\n   R/o: {p.address}")
        return "\n".join(lines)
