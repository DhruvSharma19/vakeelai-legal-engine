"""
Legal Demand Notice Template
----------------------------
Statutory legal notice issued by legal counsel on behalf of a claimant
for recovery of dues, breach of commercial contract, or dishonor of payment.
"""

from datetime import datetime
from typing import Dict, Any, List
from core.drafting.models import DraftInput
from core.drafting.num_to_words import format_indian_currency


class LegalNoticeTemplate:
    TEMPLATE_ID = "legal_notice"
    NAME = "Legal Demand Notice (Recovery of Dues / Contractual Breach)"

    @classmethod
    def generate(cls, data: DraftInput) -> Dict[str, Any]:
        cur_date = data.date or datetime.now().strftime("%d-%m-%Y")
        claim_formatted = format_indian_currency(data.total_claim_amount) if data.total_claim_amount > 0 else "Rs. Nil"

        adv = data.advocate
        adv_name = adv.name if adv else "Advocate"
        adv_addr = adv.office_address if adv else "Law Chambers, New Delhi"
        adv_reg = adv.bar_council_number if adv else "D/0000/2020"

        client_name = data.plaintiffs[0].name if data.plaintiffs else "My Client"
        client_addr = data.plaintiffs[0].address if data.plaintiffs else "as stated"

        addressee = data.defendants[0].name if data.defendants else "The Addressee"
        addressee_addr = data.defendants[0].address if data.defendants else "Address not provided"

        facts_bullets = []
        if data.facts:
            for idx, fact in enumerate(data.facts, 1):
                dt_str = f"On {fact.date}, " if fact.date else ""
                facts_bullets.append(f"{idx}. {dt_str}{fact.narrative}")
        else:
            facts_bullets = [
                "1. That my Client and you entered into a binding contractual agreement for goods/services.",
                "2. That despite rendering full and faithful performance, you failed and neglected to remit lawful dues.",
                f"3. That an aggregate outstanding amount of {claim_formatted} remains due, owing and payable by you.",
            ]

        paragraphs = [
            f"UNDER INSTRUCTIONS FROM AND ON BEHALF OF MY CLIENT: {client_name}, having address at {client_addr}, "
            f"I hereby serve upon you the following LEGAL NOTICE:",
            "\n".join(facts_bullets),
            f"That by your persistent default and evasive conduct, my Client has suffered severe financial loss, wrongful injury, "
            f"and hardship, which you are legally bound to make good.",
            f"I, THEREFORE, HEREBY CALL UPON YOU to pay to my Client the said sum of {claim_formatted} along with interest "
            f"@ 18% per annum from the date of default till the date of realization, within a period of 15 (FIFTEEN) DAYS "
            f"from the receipt of this Notice.",
            f"PLEASE TAKE NOTICE that in the event of your failure to comply with the requisitions of this Notice within the "
            f"stipulated period of 15 days, my Client has given me peremptory instructions to initiate appropriate Civil and/or "
            f"Criminal proceedings against you in the competent Court of law, entirely at your risk, cost and consequences.",
        ]

        plain_text = (
            f"LEGAL NOTICE\n"
            f"SPEED POST WITH A/D / REGISTERED EMAIL\n\n"
            f"FROM:\n"
            f"{adv_name}, Advocate\n"
            f"{adv_addr}\n"
            f"Enrollment No: {adv_reg}\n"
            f"Date: {cur_date}\n\n"
            f"TO:\n"
            f"{addressee}\n"
            f"{addressee_addr}\n\n"
            f"SUBJECT: LEGAL DEMAND NOTICE FOR PAYMENT OF {claim_formatted} AND BREACH OF CONTRACT\n\n"
            f"Sir / Madam,\n\n"
            + "\n\n".join(paragraphs)
            + f"\n\nYours faithfully,\n\n"
            f"{adv_name}\n"
            f"Advocate for the Claimant"
        )

        markdown = (
            f"# **LEGAL DEMAND NOTICE**\n"
            f"*Sent via Speed Post A/D & Electronic Mail*\n\n"
            f"**From:**  \n"
            f"**{adv_name}**, Advocate  \n"
            f"{adv_addr}  \n"
            f"Bar Enrollment: `{adv_reg}`  \n"
            f"**Date:** {cur_date}\n\n"
            f"**To:**  \n"
            f"**{addressee}**  \n"
            f"{addressee_addr}\n\n"
            f"---\n\n"
            f"### **SUBJECT: LEGAL DEMAND NOTICE FOR PAYMENT OF {claim_formatted}**\n\n"
            f"Sir / Madam,\n\n"
            + "\n\n".join([f"> {p}" for p in paragraphs])
            + f"\n\n---\n\n"
            f"**Yours faithfully,**  \n\n"
            f"**{adv_name}**  \n"
            f"Counsel for {client_name}"
        )

        return {
            "template_id": cls.TEMPLATE_ID,
            "template_name": cls.NAME,
            "title": f"Legal Demand Notice to {addressee} for {claim_formatted}",
            "plain_text": plain_text,
            "markdown": markdown,
            "structured_sections": {
                "advocate": adv.model_dump() if adv else {},
                "addressee": addressee,
                "client": client_name,
                "claim_amount": claim_formatted,
                "facts": facts_bullets,
                "notice_period": "15 Days",
            },
        }
