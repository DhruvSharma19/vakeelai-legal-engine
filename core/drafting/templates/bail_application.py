"""
Bail Application Template
-------------------------
Filed under Section 439 of the Code of Criminal Procedure, 1973 (CrPC)
/ Section 483 of the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS).
"""

from datetime import datetime
from typing import Dict, Any, List
from core.drafting.models import DraftInput


class BailApplicationTemplate:
    TEMPLATE_ID = "bail_application"
    NAME = "Regular Bail Application (Section 439 CrPC / Section 483 BNSS)"

    @classmethod
    def generate(cls, data: DraftInput) -> Dict[str, Any]:
        cur_date = data.date or datetime.now().strftime("%d-%m-%Y")
        court_header = (data.court_name or "IN THE COURT OF SESSIONS JUDGE, NEW DELHI").upper()
        case_no = data.case_type_number_year or "BAIL APPLICATION NO. _____ OF 2024"

        accused = data.plaintiffs[0].name if data.plaintiffs else "The Accused / Applicant"
        accused_addr = data.plaintiffs[0].address if data.plaintiffs else "New Delhi"
        adv_name = data.advocate.name if data.advocate else "Advocate"
        adv_office = data.advocate.office_address if data.advocate else "Chamber No. 12, Court Complex"
        adv_reg = data.advocate.bar_council_number if data.advocate else "D/0000/2020"

        facts_list = []
        if data.facts:
            for idx, f in enumerate(data.facts, 1):
                dt_str = f"On {f.date}: " if f.date else ""
                facts_list.append(f"{idx}. {dt_str}{f.narrative}")
        else:
            facts_list = [
                "1. That the Applicant is a law-abiding citizen with clean antecedents and deep roots in society.",
                "2. That the Applicant has been falsely implicated in the present case due to enmity and ulterior motives.",
                "3. That the investigation is substantially complete, no custodial interrogation is required, and nothing remains to be recovered from the Applicant.",
            ]

        grounds = [
            "(i) That the Applicant is innocent and has committed no offence whatsoever.",
            "(ii) That the Applicant has deep roots in society, is the sole breadwinner of his family, and has no criminal antecedents.",
            "(iii) That there is no reasonable apprehension of the Applicant absconding, fleeing justice, or tampering with evidence.",
            "(iv) That the Applicant undertakes to abide by any terms and conditions imposed by this Hon'ble Court and will make himself available for investigation as and when required.",
            "(v) That the Applicant is ready and willing to furnish solvent surety to the entire satisfaction of this Hon'ble Court.",
        ]

        plain_text = (
            f"{court_header}\n"
            f"{case_no}\n\n"
            f"IN THE MATTER OF:\n"
            f"{accused.upper()}\n"
            f"R/o: {accused_addr}\n"
            f"...APPLICANT / ACCUSED\n\n"
            f"VERSUS\n\n"
            f"STATE (NCT OF DELHI)\n"
            f"...RESPONDENT\n\n"
            f"APPLICATION UNDER SECTION 439 OF THE CODE OF CRIMINAL PROCEDURE, 1973 "
            f"(READ WITH SECTION 483 BNSS, 2023) FOR GRANT OF REGULAR BAIL ON BEHALF OF THE APPLICANT\n\n"
            f"MOST RESPECTFULLY SHOWETH:\n\n"
            + "\n\n".join(facts_list)
            + f"\n\nGROUNDS FOR BAIL:\n\n"
            + "\n".join(grounds)
            + f"\n\nPRAYER:\n"
            f"Wherefore, in the interest of justice, it is most respectfully prayed that this Hon'ble Court may be pleased to:\n"
            f"(a) Release the Applicant / Accused on regular bail in the aforementioned case, on such terms and conditions as deemed fit;\n"
            f"(b) Pass any other or further order(s) as this Hon'ble Court may deem fit and proper.\n\n"
            f"Place: {data.place}\n"
            f"Date: {cur_date}\n\n"
            f"APPLICANT\n\n"
            f"THROUGH COUNSEL\n"
            f"{adv_name}, Advocate\n"
            f"{adv_office}\n"
            f"Enrolment No: {adv_reg}\n\n"
            f"VERIFICATION:\n"
            f"Verified at {data.place} on this {cur_date} that the contents of the above application are true and correct.\n\n"
            f"DEPONENT"
        )

        markdown = (
            f"### {court_header}\n"
            f"**{case_no}**\n\n"
            f"#### IN THE MATTER OF:\n"
            f"**{accused.upper()}**  \n"
            f"*{accused_addr}*  \n"
            f"**...APPLICANT / ACCUSED**\n\n"
            f"**VERSUS**\n\n"
            f"**STATE (NCT OF DELHI)**  \n"
            f"**...RESPONDENT**\n\n"
            f"---\n\n"
            f"### **APPLICATION FOR GRANT OF REGULAR BAIL UNDER SECTION 439 CrPC / 483 BNSS**\n\n"
            f"**MOST RESPECTFULLY SHOWETH:**\n\n"
            + "\n\n".join([f"> {f}" for f in facts_list])
            + f"\n\n#### **GROUNDS FOR BAIL:**\n\n"
            + "\n".join([f"* **{g}**" for g in grounds])
            + f"\n\n### **PRAYER:**\n\n"
            f"* **(a)** Release the Applicant on regular bail on reasonable terms and conditions;\n"
            f"* **(b)** Pass any other order deemed fit and proper in the interest of justice.\n\n"
            f"---\n\n"
            f"**APPLICANT**  \n"
            f"*Through Counsel:* **{adv_name}**, Advocate (`{adv_reg}`)"
        )

        return {
            "template_id": cls.TEMPLATE_ID,
            "template_name": cls.NAME,
            "title": f"Regular Bail Application on behalf of {accused}",
            "plain_text": plain_text,
            "markdown": markdown,
            "structured_sections": {
                "court": court_header,
                "case_no": case_no,
                "accused": accused,
                "facts": facts_list,
                "grounds": grounds,
            },
        }

