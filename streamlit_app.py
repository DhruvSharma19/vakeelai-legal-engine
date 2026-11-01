"""
VakeelAI LegalTech Platform
===========================
Streamlit Cloud / Live Deployment Entrypoint
--------------------------------------------
Provides a complete, interactive, mobile-responsive UI for:
1. District Court Case Scraper (eCourts portal reverse engineered)
2. Pure-Python Legal Draft Generator (Deterministic Rule-Based Engine)
3. One-Click Synergy Bridge & Multi-Format Exports (Word .docx, Markdown, JSON, HTML)
"""

import json
from datetime import datetime
import streamlit as st

from core.ecourts.scraper import DistrictCourtScraper
from core.ecourts.sample_data import (
    get_fallback_case_by_cnr,
    SAMPLE_STATES,
    SAMPLE_DELHI_DISTRICTS,
    SAMPLE_SOUTH_COMPLEXES,
    SAMPLE_SAKET_ESTABLISHMENTS,
    SAMPLE_COMMERCIAL_CASE_TYPES,
)
from core.drafting.engine import LegalDraftingEngine
from core.drafting.models import DraftInput, PartyInput, AdvocateInput, FactItem

st.set_page_config(
    page_title="VakeelAI - eCourts Scraper & Legal Draft Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .badge-pill {
        background-color: #f1f5f9;
        color: #0f172a;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
        border: 1px solid #e2e8f0;
    }
    .legal-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        font-family: 'Times New Roman', serif;
        font-size: 15px;
        line-height: 1.8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "scraped_case" not in st.session_state:
    st.session_state.scraped_case = None
if "draft_input_prefilled" not in st.session_state:
    st.session_state.draft_input_prefilled = None

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/fluency/96/courthouse.png", width=64)
st.sidebar.title("VakeelAI LegalTech")
st.sidebar.markdown("**Legal Engineering Platform**")
st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    "Navigate to:",
    ["⚖️ eCourts Case Scraper", "📝 Legal Draft Studio", "🏛️ System Architecture & Docs"],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Resilience Built-in:** Includes live eCourts request flow reproduction with dynamic "
    "token/header parsing and an offline verified fallback dataset for cloud hosting reliability."
)

scraper = DistrictCourtScraper(timeout=12)

# ==========================================
# 1. eCourts Case Scraper
# ==========================================
if app_mode == "⚖️ eCourts Case Scraper":
    st.markdown('<div class="main-header">District Court Case Scraper</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header"><span class="badge-pill">eCourts Engine</span> '
        'Programmatic network flow reproduction against <code>services.ecourts.gov.in</code> with dynamic rotating header decryption.</div>',
        unsafe_allow_html=True,
    )

    search_tab1, search_tab2 = st.tabs(["🔍 Search by CNR Number", "🏛️ Search by Case Number"])

    # Search by CNR
    with search_tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            cnr_input = st.text_input(
                "Enter 16-Character CNR Number",
                value="DLST010047302024",
                help="Example: DLST010047302024 (Saket Court Commercial Suit) or DLND020000602007 (PHC Criminal Case)",
            )
            st.caption("Try examples: `DLST010047302024` (Saket PNB vs Sunil Kumar) | `DLND020000602007` (Patiala House)")

        with col2:
            auto_solve = st.checkbox("Auto-solve Captcha via offline OCR", value=True)
            manual_captcha = st.text_input("Manual Captcha (if auto-solve unchecked)", value="")

        if st.button("Fetch Case Details by CNR", type="primary"):
            with st.spinner("Executing network flow against eCourts portal..."):
                try:
                    case = scraper.scrape_by_cnr(
                        cnr_number=cnr_input,
                        user_captcha=manual_captcha if not auto_solve else None,
                        allow_fallback=True,
                    )
                    st.session_state.scraped_case = case
                    st.success(f"Successfully scraped case: {case.cnr_number} (Source: {case.source})")
                except Exception as e:
                    st.error(f"Search failed: {e}")

    # Search by Case Number
    with search_tab2:
        st.markdown("##### Court Hierarchy & Case Identification")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            state = st.selectbox("State", ["Delhi (26)", "Maharashtra (1)"])
        with c2:
            district = st.selectbox("District", ["South (10)", "Central (8)", "New Delhi (7)"])
        with c3:
            complex_val = st.selectbox("Court Complex", ["Saket Court Complex (1260011)"])
        with c4:
            establishment = st.selectbox("Establishment", ["District and Sessions Judge, South, Saket (1)"])

        c5, c6, c7 = st.columns([2, 1, 1])
        with c5:
            case_type = st.selectbox(
                "Case Type",
                ["CS (COMM) - CIVIL SUIT (COMMERCIAL) (77^1)", "ARB. A.(COMM.) (76^1)", "Bail Matters (69^1)"],
            )
        with c6:
            case_no = st.text_input("Case Number", value="233")
        with c7:
            case_year = st.text_input("Year", value="2024")

        if st.button("Search Case Hierarchy", type="primary"):
            with st.spinner("Submitting search to eCourts..."):
                try:
                    summaries, detailed_case = scraper.scrape_by_case_number(
                        state_code="26",
                        dist_code="10",
                        court_complex_code="1260011@1,2,3,4@Y",
                        est_code="1",
                        case_type="77^1",
                        case_no=case_no,
                        year=case_year,
                        allow_fallback=True,
                    )
                    if detailed_case:
                        st.session_state.scraped_case = detailed_case
                        st.success(f"Matched and retrieved case: {detailed_case.cnr_number}")
                    elif summaries:
                        st.info(f"Found {len(summaries)} matching records.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Display Scraped Case Results
    if st.session_state.scraped_case:
        case = st.session_state.scraped_case
        st.markdown("---")

        # Top Overview
        pet_name = case.petitioners[0].name if case.petitioners else "Petitioner"
        resp_name = case.respondents[0].name if case.respondents else "Respondent"

        col_title, col_actions = st.columns([3, 1])
        with col_title:
            st.subheader(f"🏛️ {pet_name} Vs {resp_name}")
            st.markdown(
                f"**CNR:** `{case.cnr_number}` | **Reg No:** `{case.case_details.registration_number or 'N/A'}` | "
                f"**Type:** `{case.case_details.case_type or 'Civil Suit'}` | **Source:** `{case.source}`"
            )
        with col_actions:
            if st.button("📝 Pre-fill Legal Draft Studio"):
                st.session_state.draft_input_prefilled = LegalDraftingEngine.populate_from_case(case)
                st.info("Draft pre-filled! Switch to the 'Legal Draft Studio' tab in the sidebar to review.")

        # Metric Stats
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("First Hearing", case.case_status.first_hearing_date or "N/A")
        m2.metric("Next / Decision Date", case.case_status.decision_date or case.case_status.next_hearing_date or "N/A")
        m3.metric("Case Stage", case.case_status.case_stage or "Pending")
        m4.metric("Disposal", case.case_status.nature_of_disposal or "Sub-Judice")

        # Detail Sub-tabs
        dt1, dt2, dt3, dt4 = st.tabs(["👥 Parties & Advocates", "📋 Case Details & Acts", "⏳ Hearing History", "📜 Orders & Judgments"])

        with dt1:
            c_p, c_r = st.columns(2)
            with c_p:
                st.markdown("**Petitioner(s) / Plaintiff(s):**")
                for idx, p in enumerate(case.petitioners, 1):
                    st.markdown(f"- **{p.name}**  \n  *Advocate:* {p.advocate or 'N/A'}  \n  *Address:* {p.address or 'N/A'}")
            with c_r:
                st.markdown("**Respondent(s) / Defendant(s):**")
                for idx, r in enumerate(case.respondents, 1):
                    st.markdown(f"- **{r.name}**  \n  *Advocate:* {r.advocate or 'N/A'}  \n  *Address:* {r.address or 'N/A'}")

        with dt2:
            st.json(case.case_details.model_dump())
            if case.acts:
                st.markdown("**Statutory Acts:**")
                for act in case.acts:
                    st.markdown(f"- **{act.act}** (Section: `{act.section or 'General'}`)")

        with dt3:
            st.markdown(f"**Total Hearings: {len(case.hearing_history)}**")
            for h in case.hearing_history:
                st.markdown(f"📅 **{h.hearing_date or 'N/A'}** — *{h.purpose or 'Judicial Business'}* | Judge: {h.judge or 'Presiding Judge'}")

        with dt4:
            st.markdown(f"**Total Orders: {len(case.orders)}**")
            for o in case.orders:
                st.markdown(f"📄 **Order #{o.order_number or '1'}** ({o.order_date}) - {o.order_details}")
                if o.pdf_url:
                    st.markdown(f"[🔗 View / Download Order Document]({o.pdf_url})")

        st.download_button(
            "📥 Download Full Case JSON",
            data=json.dumps(case.model_dump(), indent=2),
            file_name=f"case_{case.cnr_number}.json",
            mime="application/json",
        )


# ==========================================
# 2. Legal Draft Studio
# ==========================================
elif app_mode == "📝 Legal Draft Studio":
    st.markdown('<div class="main-header">Legal Draft Template Generator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header"><span class="badge-pill">Drafting Studio</span> '
        'Pure-Python Rule-Based Legal Document Assembler • <strong>Zero LLMs • Zero External APIs</strong>.</div>',
        unsafe_allow_html=True,
    )

    templates_catalog = LegalDraftingEngine.list_templates()
    template_options = {t["id"]: t["name"] for t in templates_catalog}

    # Left col: form, Right col: preview
    col_form, col_preview = st.columns([1, 1])

    with col_form:
        st.subheader("Document Parameters")
        chosen_tid = st.selectbox("Select Legal Template", list(template_options.keys()), format_func=lambda x: template_options[x])

        prefill = st.session_state.draft_input_prefilled

        court_val = prefill.court_name if prefill else "IN THE COURT OF DISTRICT JUDGE (COMMERCIAL COURT) AT SAKET, NEW DELHI"
        suit_no_val = prefill.case_type_number_year if prefill else "CS (COMM) NO. 233 OF 2024"
        cnr_val = prefill.cnr_number if prefill else "DLST010047302024"
        p1_val = prefill.plaintiffs[0].name if prefill and prefill.plaintiffs else "Punjab National Bank"
        d1_val = prefill.defendants[0].name if prefill and prefill.defendants else "Sunil Kumar"
        claim_val = prefill.total_claim_amount if prefill else 2450000.0

        court_name = st.text_input("Presiding Court Heading", value=court_val)
        suit_no = st.text_input("Suit / Case Number", value=suit_no_val)
        cnr_no = st.text_input("CNR Number", value=cnr_val)

        st.markdown("**Parties**")
        p_name = st.text_input("Plaintiff / Claimant Name", value=p1_val)
        p_addr = st.text_input("Plaintiff Address", value="Saket Branch Office, New Delhi - 110017")

        d_name = st.text_input("Defendant / Opposite Party Name", value=d1_val)
        d_addr = st.text_input("Defendant Address", value="H.No. 45, Saket Community Center, New Delhi")

        st.markdown("**Valuation & Claims**")
        claim_amt = st.number_input("Total Claim Valuation (INR)", value=float(claim_val), step=50000.0)

        st.markdown("**Facts & Timeline**")
        facts_text = st.text_area(
            "Enter Chronological Facts (One per line)",
            value=(
                "10-05-2024: Commercial credit facility granted to Defendant.\n"
                "15-10-2024: Defendant defaulted on agreed monthly repayments.\n"
                "01-11-2024: Statutory legal demand notice issued."
            ),
        )

        facts_items = []
        for line in facts_text.strip().split("\n"):
            if ":" in line:
                dt_part, narr_part = line.split(":", 1)
                facts_items.append(FactItem(date=dt_part.strip(), narrative=narr_part.strip()))
            elif line.strip():
                facts_items.append(FactItem(narrative=line.strip()))

        draft_input = DraftInput(
            template_id=chosen_tid,
            court_name=court_name,
            case_type_number_year=suit_no,
            cnr_number=cnr_no,
            plaintiffs=[PartyInput(name=p_name, address=p_addr, is_corporate="bank" in p_name.lower())],
            defendants=[PartyInput(name=d_name, address=d_addr)],
            advocate=AdvocateInput(name="DINANATH THAKUR", bar_council_number="D/2341/2011"),
            total_claim_amount=claim_amt,
            cause_of_action_date="10-05-2024",
            facts=facts_items,
            place="New Delhi",
            date=datetime.now().strftime("%d-%m-%Y"),
        )

    with col_preview:
        st.subheader("Document Preview")
        output = LegalDraftingEngine.generate_draft(draft_input)

        p_tab1, p_tab2, p_tab3 = st.tabs(["📄 Formatted Legal View", "📝 Markdown", "📊 JSON Structure"])

        with p_tab1:
            st.markdown(f'<div class="legal-box">{output.html}</div>', unsafe_allow_html=True)

        with p_tab2:
            st.code(output.markdown, language="markdown")

        with p_tab3:
            st.json(output.structured_sections)

        st.markdown("---")
        # Export Actions
        docx_data = LegalDraftingEngine.export_to_docx(output)
        st.download_button(
            "📥 Download Microsoft Word (.docx)",
            data=docx_data,
            file_name=f"{chosen_tid}_{suit_no.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )


# ==========================================
# 3. System Architecture & Docs
# ==========================================
elif app_mode == "🏛️ System Architecture & Docs":
    st.markdown('<div class="main-header">System Architecture & Technical Choices</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Explanation of network flow reverse engineering, delimiter decoding, and deterministic drafting engine.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ### 🔍 eCourts Network Flow Reproduction
        1. **Session & Cookie Persistence:** Handles `SERVICES_SESSID` and `JSESSION` cookies automatically across requests.
        2. **Dynamic Delimiter & Rotating Header:** eCourts dynamically encrypts requests using a rotating JS delimiter inside `components.js?v=...` and injects a dynamic header name (e.g. `Biure465: delimeter`). Our client dynamically fetches and extracts these tokens on startup.
        3. **Synchronized `app_token`:** Reads the 64-character SHA256 DOM token and updates it from AJAX delimiter responses (`#####<token>#####`).
        4. **Offline ONNX OCR (`ddddocr`):** Lightweight offline OCR solves Securimage captchas locally without paid third-party APIs.
        5. **Resilience Layer:** Provides pre-verified genuine datasets if foreign cloud IPs (Render/Streamlit US datacenters) are geo-blocked by NIC firewalls.

        ---

        ### 📝 Pure-Python Legal Template Generator
        1. **Strictly Non-LLM:** Deterministic rule-based template generation ensuring zero external API dependencies.
        2. **Indian Legal Conventions:** Formats Court headers, memo of parties, numbered averments, Section 12A commercial mediation compliance, verification, and Statement of Truth under Order VI Rule 15A CPC.
        3. **Indian Currency Engine:** Custom converter transforms numbers into standard words (e.g., `Rs. 24,50,000/- (Rupees Twenty-Four Lakh Fifty Thousand Only)`).
        4. **Multi-Format Outputs:** Generates `.docx` with 1.5-inch court binding margins, Markdown, and printable HTML.
        5. **Cross-Task Bridge:** Pre-fills the draft generator directly from any scraped court case.
        """
    )

