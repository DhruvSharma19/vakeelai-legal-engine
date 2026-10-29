"""
API Routes: Legal Draft Generator
---------------------------------
Pure-Python legal document template generator endpoints.
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import io

from core.drafting.models import DraftInput, DraftOutput
from core.drafting.engine import LegalDraftingEngine
from core.ecourts.models import ComprehensiveCaseData

router = APIRouter(prefix="/api/drafting", tags=["Legal Draft Generator"])


@router.get("/templates")
def list_templates():
    """Returns list of available pure-Python legal document templates."""
    return LegalDraftingEngine.list_templates()


@router.post("/generate", response_model=DraftOutput)
def generate_draft(draft_input: DraftInput):
    """
    Generates a structured legal draft from user inputs using pure Python (no LLMs).
    """
    try:
        return LegalDraftingEngine.generate_draft(draft_input)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Generation failed: {str(e)}")


@router.post("/prefill-from-case", response_model=DraftInput)
def prefill_draft_from_case(case_data: ComprehensiveCaseData, template_id: str = "commercial_suit"):
    """
    Cross-Task Synergy Bridge:
    Auto-populates draft input fields from a scraped eCourts case.
    """
    try:
        return LegalDraftingEngine.populate_from_case(case_data, template_id=template_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to prefill from case: {str(e)}")


@router.post("/export/docx")
def export_draft_to_docx(draft_input: DraftInput):
    """
    Generates and downloads a formatted Microsoft Word (.docx) document
    with 1.5 line spacing, 1.5 inch court margin, and standard legal fonts.
    """
    try:
        draft = LegalDraftingEngine.generate_draft(draft_input)
        docx_bytes = LegalDraftingEngine.export_to_docx(draft)

        filename = f"{draft_input.template_id}_{draft_input.case_type_number_year or 'legal_draft'}.docx"
        # Sanitize filename
        filename = "".join(c for c in filename if c.isalnum() or c in ("-", "_", ".")).strip()

        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

