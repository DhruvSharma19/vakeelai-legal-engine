"""
Consumer Complaint Template
---------------------------
Complaint under Section 35 of the Consumer Protection Act, 2019
before the District Consumer Disputes Redressal Commission.
"""

from datetime import datetime
from typing import Dict, Any, List
from core.drafting.models import DraftInput
from core.drafting.num_to_words import format_indian_currency


class ConsumerComplaintTemplate:
    TEMPLATE_ID = "consumer_complaint"
    NAME = "Consumer Protection Complaint (Section 35 Consumer Protection Act, 2019)"

    @classmethod
    def generate(cls, data: DraftInput) -> Dict[str, Any]:
        cur_date = data.date or datetime.now().strftime("%d-%m-%Y")
        claim_formatted = format_indian_currency(data.total_claim_amount) if data.total_claim_amount > 0 else "Rs. Nil"

        court_header = (data.court_name or "BEFORE THE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION, NEW DELHI").upper()
        case_no = data.case_type_number_year or "CONSUMER COMPLAINT NO. _____ OF 2024"

        complainant = data.plaintiffs[0].name if data.plaintiffs else "The Complainant"
        complainant_addr = data.plaintiffs[0].address if data.plaintiffs else "Address not provided"

        op = data.defendants[0].name if data.defendants else "The Opposite Party"
        op_addr = data.defendants[0].address if data.defendants else "Address not provided"

        facts = []
        if data.facts:
            for idx, f in enumerate(data.facts, 1):
                facts.append(f"{idx}. {f.narrative}")
        else:
            facts = [
                "1. That the Complainant is a consumer within the definition of Section 2(7) of the Consumer Protection Act, 2019.",
                f"2. That the Opposite Party is a service provider/seller who was engaged by the Complainant against valuable consideration.",
                "3. That the Opposite Party committed severe deficiency in service, negligence, and unfair trade practices causing financial injury and mental agony to the Complainant.",
            ]

        plain_text = (
            f"{court_header}\n"
            f"{case_no}\n\n"
            f"IN THE MATTER OF:\n"
            f"{complainant.upper()}\n"
            f"R/o: {complainant_addr}\n"
            f"...COMPLAINANT\n\n"
            f"VERSUS\n\n"
            f"{op.upper()}\n"
            f"Address: {op_addr}\n"
            f"...OPPOSITE PARTY\n\n"
            f"COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019 FOR DEFICIENCY IN SERVICE "
            f"AND UNFAIR TRADE PRACTICE\n\n"
            f"RESPECTFULLY SHOWETH:\n\n"
            + "\n\n".join(facts)
            + f"\n\nPRAYER:\n"
            f"It is therefore most respectfully prayed that this Hon'ble Commission may graciously be pleased to:\n"
            f"(a) Direct the Opposite Party to refund the sum of {claim_formatted} along with interest @ 18% p.a.;\n"
            f"(b) Direct the Opposite Party to pay Rs. 1,00,000/- as compensation for mental harassment and agony;\n"
            f"(c) Direct the Opposite Party to pay Rs. 25,000/- towards litigation expenses;\n"
            f"(d) Pass any other relief deemed appropriate.\n\n"
            f"Place: {data.place}\n"
            f"Date: {cur_date}\n\n"
            f"COMPLAINANT"
        )

        markdown = (
            f"### {court_header}\n"
            f"**{case_no}**\n\n"
            f"#### IN THE MATTER OF:\n"
            f"**{complainant.upper()}** (Complainant)  \n"
            f"**VERSUS**  \n"
            f"**{op.upper()}** (Opposite Party)  \n\n"
            f"---\n\n"
            f"### **COMPLAINT UNDER SECTION 35 CONSUMER PROTECTION ACT, 2019**\n\n"
            + "\n\n".join([f"> {f}" for f in facts])
            + f"\n\n### **PRAYER:**\n\n"
            f"* **(a)** Direct refund of **{claim_formatted}** with 18% interest;\n"
            f"* **(b)** Direct compensation of Rs. 1,00,000/- for harassment;\n"
            f"* **(c)** Award litigation costs of Rs. 25,000/-.\n\n"
            f"---\n**COMPLAINANT**"
        )

        return {
            "template_id": cls.TEMPLATE_ID,
            "template_name": cls.NAME,
            "title": f"Consumer Complaint against {op}",
            "plain_text": plain_text,
            "markdown": markdown,
            "structured_sections": {
                "court": court_header,
                "complainant": complainant,
                "opposite_party": op,
                "facts": facts,
            },
        }

