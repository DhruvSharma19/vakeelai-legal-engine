"""
API Routes: eCourts District Court Scraper
------------------------------------------
FastAPI endpoints for:
- Session-based Captcha fetching & solving
- Court hierarchy cascades (State -> District -> Complex -> Establishment -> Case Type)
- CNR Search (16-character unique ID)
- Case Number Search (Hierarchy + Number + Year)
- Case drilldown & PDF proxy
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from core.ecourts.scraper import DistrictCourtScraper
from core.ecourts.models import ComprehensiveCaseData, CaseSummary
from core.ecourts.client import ECourtsClient

router = APIRouter(prefix="/api/ecourts", tags=["eCourts Scraper"])
scraper = DistrictCourtScraper(timeout=15)


class CNRSearchRequest(BaseModel):
    cnr_number: str = Field(..., description="16-character alphanumeric CNR number, e.g. DLND020000602007")
    captcha_code: Optional[str] = Field(None, description="Optional user-supplied captcha. If omitted, offline OCR solves it.")
    use_resilience_fallback: bool = Field(True, description="Enable verified fallback if NIC firewall blocks connection")


class CaseNumberSearchRequest(BaseModel):
    state_code: str = Field("26", description="State code (e.g. 26 for Delhi)")
    dist_code: str = Field("10", description="District code (e.g. 10 for South)")
    court_complex_code: str = Field("1260011@1,2,3,4@Y", description="Complex code (e.g. Saket)")
    est_code: str = Field("1", description="Establishment code (e.g. 1 for Dist & Sessions Judge)")
    case_type: str = Field("77^1", description="Case type code (e.g. 77^1 for CS (COMM))")
    case_no: str = Field("233", description="Case number")
    year: str = Field("2024", description="Year")
    captcha_code: Optional[str] = Field(None, description="Optional manual captcha code")
    use_resilience_fallback: bool = Field(True, description="Enable verified fallback if NIC firewall blocks connection")


@router.get("/captcha")
def get_fresh_captcha(page: str = Query("casestatus", description="'home' or 'casestatus'")):
    """
    Initializes a new session on eCourts, retrieves the captcha image and audio,
    and runs offline OCR recognition.
    """
    bundle = scraper.get_captcha_bundle(page=page)
    return bundle


@router.get("/states")
def get_states():
    """Returns list of supported Indian states."""
    return scraper.get_states()


@router.get("/districts")
def get_districts(state_code: str = Query(..., description="State code, e.g. 26")):
    """Returns districts for a state."""
    return scraper.get_districts(state_code)


@router.get("/complexes")
def get_court_complexes(state_code: str = Query(...), dist_code: str = Query(...)):
    """Returns court complexes for state and district."""
    return scraper.get_court_complexes(state_code, dist_code)


@router.get("/establishments")
def get_establishments(state_code: str = Query(...), dist_code: str = Query(...), complex_code: str = Query(...)):
    """Returns establishments for court complex."""
    return scraper.get_establishments(state_code, dist_code, complex_code)


@router.get("/case-types")
def get_case_types(
    state_code: str = Query(...),
    dist_code: str = Query(...),
    complex_code: str = Query(...),
    est_code: str = Query(...),
):
    """Returns case types for court establishment."""
    return scraper.get_case_types(state_code, dist_code, complex_code, est_code)


@router.post("/search/cnr", response_model=ComprehensiveCaseData)
def search_by_cnr(req: CNRSearchRequest):
    """
    Scrapes a court case by its 16-character CNR Number.
    Supports both automatic OCR solving and manual captcha.
    """
    try:
        case = scraper.scrape_by_cnr(
            cnr_number=req.cnr_number,
            user_captcha=req.captcha_code,
            allow_fallback=req.use_resilience_fallback,
        )
        return case
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Scraper error: {str(e)}")


@router.post("/search/case-number")
def search_by_case_number(req: CaseNumberSearchRequest):
    """
    Searches for a case by State, District, Court Complex, Establishment, Case Type, Case Number, and Year.
    Returns search summaries and detailed case data if an exact match is resolved.
    """
    try:
        summaries, detailed_case = scraper.scrape_by_case_number(
            state_code=req.state_code,
            dist_code=req.dist_code,
            court_complex_code=req.court_complex_code,
            est_code=req.est_code,
            case_type=req.case_type,
            case_no=req.case_no,
            year=req.year,
            user_captcha=req.captcha_code,
            allow_fallback=req.use_resilience_fallback,
        )
        return {
            "summaries": [s.model_dump() for s in summaries],
            "case": detailed_case.model_dump() if detailed_case else None,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Case number search error: {str(e)}")


@router.get("/pdf-url")
def get_order_pdf_url(
    normal_v: str = Query(...),
    case_val: str = Query(...),
    court_code: str = Query(...),
    filename: str = Query(...),
):
    """
    Resolves encrypted order parameters into a relative or direct order URL on eCourts.
    """
    try:
        client = ECourtsClient()
        if client.init_session(page="casestatus"):
            res = client.display_pdf(normal_v, case_val, court_code, filename)
            order_path = res.get("order")
            if order_path:
                return {"success": True, "pdf_url": f"https://services.ecourts.gov.in/ecourtindia_v6/{order_path.lstrip('/')}"}
        return {"success": False, "pdf_url": None, "message": "Order PDF cannot be decrypted from session"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

