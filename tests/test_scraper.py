"""
Unit Tests: eCourts Scraper & Parser
------------------------------------
Tests the HTML parser, data models, captcha solver, and fallback datasets.
"""

import pytest
from core.ecourts.parser import ECourtsParser
from core.ecourts.sample_data import get_fallback_case_by_cnr, load_sample_cases
from core.ecourts.captcha import CaptchaManager
from core.ecourts.models import ComprehensiveCaseData


def test_sample_cases_load():
    """Verify that verified sample cases are loaded properly."""
    samples = load_sample_cases()
    assert "DLST010047302024" in samples
    assert "DLND020000602007" in samples


def test_saket_commercial_case_structure():
    """Verify the parsed fields of the Saket commercial suit."""
    case = get_fallback_case_by_cnr("DLST010047302024")
    assert case is not None
    assert case.cnr_number == "DLST010047302024"
    assert case.case_details.registration_number == "233/2024"
    assert "CS (COMM)" in case.case_details.case_type

    # Parties
    assert len(case.petitioners) >= 1
    assert "punjab national bank" in case.petitioners[0].name.lower()
    assert "dinanath thakur" in case.petitioners[0].advocate.lower()

    assert len(case.respondents) >= 1
    assert "sunil kumar" in case.respondents[0].name.lower()

    # Hearing history & orders
    assert len(case.hearing_history) >= 10
    assert len(case.orders) >= 5


def test_phc_criminal_case_structure():
    """Verify the parsed fields of the Patiala House Court criminal case."""
    case = get_fallback_case_by_cnr("DLND020000602007")
    assert case is not None
    assert case.cnr_number == "DLND020000602007"
    assert "criminal" in case.case_details.case_type.lower()
    assert len(case.hearing_history) > 50


def test_captcha_manager_initialization():
    """Verify CaptchaManager initializes and methods run without exception."""
    mgr = CaptchaManager()
    assert mgr is not None
    # Test base64 converter
    b64 = mgr.to_base64_data_url(b"fake_image_bytes")
    assert b64.startswith("data:image/png;base64,")


def test_summary_table_parser():
    """Test parsing of the search results table."""
    sample_table = """
    <table id='dispTable'>
      <tbody>
        <tr>
          <td>1</td>
          <td>CS (COMM)/233/2024</td>
          <td>Punjab National Bank<br>Vs</br>Sunil Kumar</td>
          <td><a onclick="viewHistory(207700002332024,'DLST010047302024',1,'','CScaseNumber',26,10,1260011,'CScaseNumber')">View</a></td>
        </tr>
      </tbody>
    </table>
    """
    summaries = ECourtsParser.parse_case_summary_table(sample_table)
    assert len(summaries) == 1
    assert summaries[0].sr_no == "1"
    assert "CS (COMM)/233/2024" in summaries[0].case_type_number_year
    assert summaries[0].cnr_number == "DLST010047302024"
    assert summaries[0].view_params["case_no"] == "207700002332024"

