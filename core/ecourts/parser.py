"""
eCourts HTML Parser
-------------------
Parses raw HTML responses returned by the eCourts District Court portal:
- cnr_status/searchByCNR/
- home/viewHistory
- casestatus/submitCaseNo

Extracts all tabular and structured information into typed Pydantic models.
Gracefully handles structural quirks, missing elements, non-standard layouts,
and extracts embedded JavaScript calls (like `displayPdf(...)` and `viewHistory(...)`).
"""

import re
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from bs4 import BeautifulSoup

from core.ecourts.models import (
    ComprehensiveCaseData,
    CaseDetails,
    CaseStatus,
    Party,
    ActSection,
    HearingHistoryItem,
    CourtOrder,
    CaseSummary,
)


class ECourtsParser:
    """
    Parser for eCourts District Court portal HTML fragments.
    """

    @staticmethod
    def parse_case_summary_table(html_content: str) -> List[CaseSummary]:
        """
        Parses the search results table from `submitCaseNo` or other search tabs.
        Extracts summary rows containing Sr No, Case Type/No/Year, Parties, and View callback parameters.
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        results: List[CaseSummary] = []

        table = soup.find("table", id="dispTable") or soup.find("table")
        if not table:
            return []

        tbody = table.find("tbody") or table
        rows = tbody.find_all("tr")

        for row in rows:
            # Skip establishment header rows that span columns
            if row.find("th", attrs={"colspan": True}):
                continue

            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            sr_no = cells[0].get_text(strip=True)
            case_type_no_year = cells[1].get_text(strip=True)
            parties = cells[2].get_text(" ", strip=True).replace("\n", " ")

            view_params = {}
            cnr_extracted = None

            # Look for the View link with viewHistory onclick
            view_link = row.find("a", onclick=True)
            if view_link:
                onclick = view_link.get("onclick", "")
                # e.g. viewHistory(207700002332024,'DLST010047302024',1,'','CScaseNumber',26,10,1260011,'CScaseNumber')
                m = re.search(r"viewHistory\(([^)]+)\)", onclick)
                if m:
                    raw_args = [arg.strip().strip("'\"") for arg in m.group(1).split(",")]
                    if len(raw_args) >= 9:
                        view_params = {
                            "case_no": raw_args[0],
                            "cino": raw_args[1],
                            "court_code": raw_args[2],
                            "hideparty": raw_args[3],
                            "caseStatusSearchType": raw_args[4],
                            "state_code": raw_args[5],
                            "dist_code": raw_args[6],
                            "complex_code": raw_args[7],
                            "search_by": raw_args[8],
                        }
                        cnr_extracted = raw_args[1]

            results.append(
                CaseSummary(
                    sr_no=sr_no,
                    case_type_number_year=case_type_no_year,
                    parties_vs=parties,
                    cnr_number=cnr_extracted,
                    view_params=view_params if view_params else None,
                )
            )

        return results

    @classmethod
    def parse_comprehensive_case(cls, html_content: str, default_cnr: str = "") -> ComprehensiveCaseData:
        """
        Parses the full case details page into a ComprehensiveCaseData model.
        Works with both CNR Search result and Case Number drilldown result.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract Court Establishment Header if present
        court_heading = ""
        for h_tag in soup.find_all(["h2", "h3", "h4", "div"], class_=re.compile(r"court|title|heading", re.I)):
            text = h_tag.get_text(strip=True)
            if any(term in text.lower() for term in ["district", "judge", "magistrate", "court", "sessions"]):
                court_heading = text
                break

        # 1. Parse Case Details Table
        case_details_dict = cls._parse_key_value_table(soup, "case_details_table")
        raw_cnr = (
            case_details_dict.get("cnr_number")
            or case_details_dict.get("cnr")
            or cls._extract_cnr_from_text(soup.get_text())
            or default_cnr
        )
        # Clean CNR to strict 16 alphanumeric characters
        m_cnr = re.search(r"([A-Z]{4}\d{12})", raw_cnr)
        cnr_val = m_cnr.group(1) if m_cnr else raw_cnr.strip()

        case_details = CaseDetails(
            case_type=case_details_dict.get("case_type"),
            filing_number=case_details_dict.get("filing_number"),
            filing_date=case_details_dict.get("filing_date"),
            registration_number=case_details_dict.get("registration_number"),
            registration_date=case_details_dict.get("registration_date"),
            cnr_number=cnr_val,
        )

        # 2. Parse Case Status Table
        case_status_dict = cls._parse_key_value_table(soup, "case_status_table")
        case_status = CaseStatus(
            first_hearing_date=case_status_dict.get("first_hearing_date"),
            next_hearing_date=case_status_dict.get("next_hearing_date"),
            decision_date=case_status_dict.get("decision_date"),
            case_stage=case_status_dict.get("case_stage") or case_status_dict.get("case_status"),
            nature_of_disposal=case_status_dict.get("nature_of_disposal"),
            court_number_and_judge=case_status_dict.get("court_number_and_judge") or court_heading,
        )

        # 3. Parse Parties & Advocates
        petitioners, respondents = cls._parse_parties_and_advocates(soup)

        # 4. Parse Acts & Sections
        acts = cls._parse_acts(soup)

        # 5. Parse Hearing History
        hearing_history = cls._parse_hearing_history(soup)

        # 6. Parse Orders and Judgments
        orders = cls._parse_orders(soup)

        return ComprehensiveCaseData(
            cnr_number=cnr_val,
            case_details=case_details,
            case_status=case_status,
            petitioners=petitioners,
            respondents=respondents,
            acts=acts,
            hearing_history=hearing_history,
            orders=orders,
            source="live",
            retrieved_at=datetime.utcnow().isoformat() + "Z",
        )

    @staticmethod
    def _parse_key_value_table(soup: BeautifulSoup, table_class: str) -> Dict[str, str]:
        """
        Parses two-column or four-column key-value tables like case_details_table and case_status_table.
        Normalizes keys into snake_case.
        """
        data: Dict[str, str] = {}
        table = soup.find("table", class_=table_class)
        if not table:
            # Fallback: look for table near a matching heading
            heading = soup.find(lambda tag: tag.name in ["span", "h3", "h4", "b"] and table_class.replace("_", " ") in tag.get_text(strip=True).lower())
            if heading:
                table = heading.find_next("table")

        if not table:
            return data

        for row in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            # Process pairs of (Key, Value)
            for i in range(0, len(cells) - 1, 2):
                raw_key = cells[i]
                raw_val = cells[i + 1]
                # Normalize key
                norm_key = re.sub(r"[^a-zA-Z0-9]+", "_", raw_key.strip()).strip("_").lower()
                norm_key = norm_key.replace("_details", "").replace("_status", "")
                if norm_key and raw_val:
                    data[norm_key] = raw_val

        return data

    @staticmethod
    def _parse_parties_and_advocates(soup: BeautifulSoup) -> Tuple[List[Party], List[Party]]:
        """
        Extracts petitioners, respondents, and their respective advocates.
        eCourts renders these inside `.Petitioner_Advocate_table` and `.Respondent_Advocate_table`
        as `<ul><li>1) Name <br/> Advocate- Name</li></ul>` or in tabular form.
        """
        petitioners: List[Party] = []
        respondents: List[Party] = []

        # 1. Petitioners
        pet_container = soup.find(class_=re.compile(r"petitioner_advocate_table", re.I))
        if pet_container:
            petitioners = ECourtsParser._extract_party_list(pet_container)
        else:
            # Fallback search by text
            pet_hdr = soup.find(lambda t: t.name in ["h3", "h4", "span", "b"] and "petitioner" in t.get_text().lower())
            if pet_hdr:
                nxt = pet_hdr.find_next(["ul", "table"])
                if nxt:
                    petitioners = ECourtsParser._extract_party_list(nxt)

        # 2. Respondents
        resp_container = soup.find(class_=re.compile(r"respondent_advocate_table", re.I))
        if resp_container:
            respondents = ECourtsParser._extract_party_list(resp_container)
        else:
            resp_hdr = soup.find(lambda t: t.name in ["h3", "h4", "span", "b"] and "respondent" in t.get_text().lower())
            if resp_hdr:
                nxt = resp_hdr.find_next(["ul", "table"])
                if nxt:
                    respondents = ECourtsParser._extract_party_list(nxt)

        return petitioners, respondents

    @staticmethod
    def _extract_party_list(container) -> List[Party]:
        parties: List[Party] = []
        items = container.find_all("li")
        if not items:
            # If formatted as table rows
            items = container.find_all("tr")

        for idx, item in enumerate(items, 1):
            text_lines = [line.strip() for line in item.get_text("\n").split("\n") if line.strip()]
            if not text_lines:
                continue

            party_name = text_lines[0]
            # Strip leading sequence numbers like "1) ", "2. "
            party_name = re.sub(r"^\d+[\). -]\s*", "", party_name).strip()

            advocate = None
            address = None

            for line in text_lines[1:]:
                if "advocate" in line.lower():
                    advocate = re.sub(r"(?i)^advocate[:\s\-]*(name)?[:\s\-]*", "", line).strip()
                elif "address" in line.lower():
                    address = re.sub(r"(?i)^address[:\s\-]*", "", line).strip()

            if party_name:
                parties.append(
                    Party(
                        name=party_name,
                        advocate=advocate,
                        address=address,
                        sequence=idx,
                    )
                )
        return parties

    @staticmethod
    def _parse_acts(soup: BeautifulSoup) -> List[ActSection]:
        acts: List[ActSection] = []
        table = soup.find("table", id="act_table") or soup.find("table", class_=re.compile(r"acts_table", re.I))
        if not table:
            return acts

        rows = table.find_all("tr")
        # Row 0 is header: ['Under Act(s)', 'Under Section(s)']
        for row in rows[1:]:
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) >= 1 and cells[0]:
                act_name = cells[0]
                section_val = cells[1] if len(cells) > 1 and cells[1] != "---" else None
                acts.append(ActSection(act=act_name, section=section_val))

        return acts

    @staticmethod
    def _parse_hearing_history(soup: BeautifulSoup) -> List[HearingHistoryItem]:
        history: List[HearingHistoryItem] = []
        table = soup.find("table", class_=re.compile(r"history_table", re.I))
        if not table:
            return history

        rows = table.find_all("tr")
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            # Skip pure headers like ['Cause List Type', 'Hearing Date', ...]
            if any(h in "".join(cells).lower() for h in ["cause list type", "purpose of hearing", "business on date"]):
                continue

            if len(cells) >= 4:
                # Typically: [Judge, Business On Date, Hearing Date, Purpose]
                judge = cells[0]
                business_on_date = cells[1] if len(cells) > 1 else None
                hearing_date = cells[2] if len(cells) > 2 else None
                purpose = cells[3] if len(cells) > 3 else None
                history.append(
                    HearingHistoryItem(
                        judge=judge,
                        business_on_date=business_on_date,
                        hearing_date=hearing_date,
                        purpose=purpose,
                    )
                )

        return history

    @staticmethod
    def _parse_orders(soup: BeautifulSoup) -> List[CourtOrder]:
        orders: List[CourtOrder] = []
        order_tables = soup.find_all("table", class_=re.compile(r"order_table", re.I))

        for ot in order_tables:
            # Check preceding header to distinguish Interim from Final Orders
            prev_header = ot.find_previous(["h2", "h3", "h4", "span", "div", "b"])
            header_text = prev_header.get_text(strip=True).lower() if prev_header else ""
            is_judgment = "judgment" in header_text or "final" in header_text

            rows = ot.find_all("tr")
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if not cells or "order number" in cells[0].lower():
                    continue

                order_no = cells[0] if len(cells) > 0 else None
                order_date = cells[1] if len(cells) > 1 else ""
                order_details = cells[2] if len(cells) > 2 else ""

                # Extract PDF link or displayPdf callback
                pdf_url = None
                link = row.find("a")
                if link:
                    onclick = link.get("onclick", "")
                    m_pdf = re.search(r"displayPdf\(([^)]+)\)", onclick)
                    if m_pdf:
                        # e.g., displayPdf('param1', 'param2', ...)
                        # Build internal API proxy URL for the frontend
                        args = [a.strip().strip("'\"") for a in m_pdf.group(1).split(",")]
                        if len(args) >= 4:
                            pdf_url = f"/api/case/pdf?normal_v={args[0]}&case_val={args[1]}&court_code={args[2]}&filename={args[3]}"
                    elif link.get("href") and not link.get("href").startswith("#"):
                        pdf_url = link.get("href")

                orders.append(
                    CourtOrder(
                        order_number=order_no,
                        order_date=order_date,
                        order_details=order_details,
                        pdf_url=pdf_url,
                        is_judgment=is_judgment,
                    )
                )

        return orders

    @staticmethod
    def _extract_cnr_from_text(text: str) -> Optional[str]:
        m = re.search(r"\b([A-Z]{4}\d{12})\b", text)
        return m.group(1) if m else None
