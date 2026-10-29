"""
Legal Draft Templates Package
"""

from core.drafting.templates.commercial_suit import CommercialSuitTemplate
from core.drafting.templates.legal_notice import LegalNoticeTemplate
from core.drafting.templates.bail_application import BailApplicationTemplate
from core.drafting.templates.consumer_complaint import ConsumerComplaintTemplate
from core.drafting.templates.general_affidavit import GeneralAffidavitTemplate

TEMPLATES_REGISTRY = {
    CommercialSuitTemplate.TEMPLATE_ID: CommercialSuitTemplate,
    LegalNoticeTemplate.TEMPLATE_ID: LegalNoticeTemplate,
    BailApplicationTemplate.TEMPLATE_ID: BailApplicationTemplate,
    ConsumerComplaintTemplate.TEMPLATE_ID: ConsumerComplaintTemplate,
    GeneralAffidavitTemplate.TEMPLATE_ID: GeneralAffidavitTemplate,
}

