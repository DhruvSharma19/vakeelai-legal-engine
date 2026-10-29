"""
General Affidavit & Verification Template
-----------------------------------------
Standard Evidentiary Affidavit under Order XIX of the Code of Civil Procedure, 1908
and Notaries Act, 1952.
"""

from datetime import datetime
from typing import Dict, Any
from core.drafting.models import DraftInput


class GeneralAffidavitTemplate:
    TEMPLATE_ID = "general_affidavit"
    NAME = "General Affidavit & Verification (Order XIX CPC / Notaries Act)"

    @classmethod
    def generate(cls, data: DraftInput) -> Dict[str, Any]:
        cur_date = data.date or datetime.now().strftime("%d-%m-%Y")
        deponent = data.plaintiffs[0].name if data.plaintiffs else "The Deponent"
        rel_type = data.plaintiffs[0].relation_type if data.plaintiffs and data.plaintiffs[0].relation_type else "S/o"
        rel_name = data.plaintiffs[0].relation_name if data.plaintiffs and data.plaintiffs[0].relation_name else "Father's Name"
        age = data.plaintiffs[0].age if data.plaintiffs and data.plaintiffs[0].age else 35
        addr = data.plaintiffs[0].address if data.plaintiffs else "New Delhi"

        facts_list = []
        if data.facts:
            for idx, f in enumerate(data.facts, 1):
                facts_list.append(f"{idx}. That {f.narrative}")
        else:
            facts_list = [
                "1. That I am the deponent herein and conversant with the facts and circumstances of the case.",
                "2. That the statements made in the accompanying application/petition are true to the best of my personal knowledge and belief.",
                "3. That no material information has been concealed or misrepresented.",
            ]

        plain_text = (
            f"AFFIDAVIT\n\n"
            f"I, {deponent}, {rel_type} {rel_name}, aged about {age} years, resident of {addr}, "
            f"do hereby solemnly affirm and declare on oath as under:\n\n"
            + "\n\n".join(facts_list)
            + f"\n\nDEPONENT\n\n"
            f"VERIFICATION:\n"
            f"Verified at {data.place} on this {cur_date} that the contents of the above affidavit are true and "
            f"correct to the best of my knowledge and belief. No part of it is false and nothing material has been concealed.\n\n"
            f"DEPONENT"
        )

        markdown = (
            f"# **AFFIDAVIT**\n\n"
            f"I, **{deponent}**, {rel_type} *{rel_name}*, aged about {age} years, resident of *{addr}*, "
            f"do hereby solemnly affirm and declare on oath as under:\n\n"
            + "\n\n".join([f"> {f}" for f in facts_list])
            + f"\n\n**DEPONENT**\n\n"
            f"---\n\n"
            f"### **VERIFICATION**\n\n"
            f"Verified at **{data.place}** on this **{cur_date}** that the contents of the above affidavit are true and "
            f"correct to the best of my knowledge. Nothing material has been concealed.\n\n"
            f"**DEPONENT**"
        )

        return {
            "template_id": cls.TEMPLATE_ID,
            "template_name": cls.NAME,
            "title": f"Affidavit of {deponent}",
            "plain_text": plain_text,
            "markdown": markdown,
            "structured_sections": {
                "deponent": deponent,
                "facts": facts_list,
                "place": data.place,
                "date": cur_date,
            },
        }

