export interface CaseDetails {
  case_type?: string;
  filing_number?: string;
  filing_date?: string;
  registration_number?: string;
  registration_date?: string;
  cnr?: string;
}

export interface CaseStatus {
  first_hearing_date?: string;
  decision_date?: string;
  case_status?: string;
  nature_of_disposal?: string;
  court_number_and_judge?: string;
  next_hearing_date?: string;
  cause_list_type?: string;
}

export interface Party {
  name: string;
  type: string;
  advocate?: string;
  address?: string;
}

export interface ActRecord {
  under_act: string;
  under_section: string;
}

export interface HearingHistory {
  hearing_date: string;
  purpose_of_hearing: string;
  business_recorded: string;
  next_hearing_date?: string;
  judge?: string;
}

export interface OrderRecord {
  order_number: string;
  order_date: string;
  order_details?: string;
  pdf_url?: string;
  display_pdf_args?: string;
}

export interface CaseRecord {
  cnr: string;
  court_establishment?: string;
  case_details?: CaseDetails;
  case_status?: CaseStatus;
  petitioners: Party[];
  respondents: Party[];
  acts: ActRecord[];
  history: HearingHistory[];
  orders: OrderRecord[];
  search_method?: string;
  source?: string;
}

export interface CaptchaResponse {
  success: boolean;
  image_data_url?: string;
  audio_url?: string;
  solved_captcha?: string;
}

export interface PartyInput {
  name: string;
  relation_type?: string;
  relation_name?: string;
  age?: number;
  occupation?: string;
  address: string;
  email?: string;
  phone?: string;
  is_corporate?: boolean;
}

export interface AdvocateInput {
  name: string;
  bar_council_number?: string;
  office_address?: string;
  email?: string;
  phone?: string;
}

export interface FactItem {
  date?: string;
  narrative: string;
  annexure_label?: string;
}

export interface PrayerItem {
  clause_letter: string;
  relief_text: string;
}

export interface DraftInput {
  template_id: string;
  court_name: string;
  jurisdiction_title?: string;
  case_type_number_year?: string;
  cnr_number?: string;
  plaintiffs: PartyInput[];
  defendants: PartyInput[];
  advocate?: AdvocateInput;
  matter_title?: string;
  total_claim_amount: number;
  facts: FactItem[];
  prayers: PrayerItem[];
  sec_12a_compliance?: boolean;
  place?: string;
  date?: string;
}

export interface DraftOutput {
  template_id: string;
  template_name: string;
  title: string;
  plain_text: string;
  markdown: string;
  html: string;
  structured_sections: Record<string, any>;
  metadata: Record<string, any>;
}
