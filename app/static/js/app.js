/**
 * VakeelAI Legal Engineering Platform
 * Frontend Application Controller
 * Handles:
 * - Scraper subtabs (CNR vs Case Number)
 * - Captcha bundle loading, audio playback, OCR auto-fill
 * - Dynamic cascading hierarchy (State -> District -> Complex -> Est -> Type)
 * - Searching by CNR and Case Number
 * - Case detail rendering (Parties, Details, Timeline, Orders with PDF links)
 * - Legal Draft Generator with dynamic fact rows and multi-format exports (Word, Markdown, HTML, JSON)
 * - Cross-Task Pre-fill Bridge
 */

let currentCaseData = null;
let currentDraftOutput = null;
let currentAudioUrl = null;

document.addEventListener('DOMContentLoaded', () => {
  // Initial captcha load
  loadCaptcha('casestatus');
  // Initial draft generation with default values
  generateLegalDraft();
});

// Main Tab Navigation
function switchMainTab(tab) {
  document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.add('hidden'));

  const navBtn = document.getElementById(`nav-${tab}`);
  const pane = document.getElementById(`section-${tab}`);

  if (navBtn) navBtn.classList.add('active');
  if (pane) pane.classList.remove('hidden');

  if (window.lucide) window.lucide.createIcons();
}

// Scraper Subtab Switcher (CNR vs Case Number)
function switchScraperSubtab(subtab) {
  const btnCnr = document.getElementById('subtab-cnr');
  const btnCase = document.getElementById('subtab-case');
  const formCnr = document.getElementById('subform-cnr');
  const formCase = document.getElementById('subform-case');

  if (subtab === 'cnr') {
    btnCnr.className = 'subtab-btn pb-3 text-sm font-semibold border-b-2 border-brand-600 text-brand-700 flex items-center space-x-2';
    btnCase.className = 'subtab-btn pb-3 text-sm font-semibold border-b-2 border-transparent text-slate-500 hover:text-slate-700 flex items-center space-x-2';
    formCnr.classList.remove('hidden');
    formCase.classList.add('hidden');
    loadCaptcha('home');
  } else {
    btnCase.className = 'subtab-btn pb-3 text-sm font-semibold border-b-2 border-brand-600 text-brand-700 flex items-center space-x-2';
    btnCnr.className = 'subtab-btn pb-3 text-sm font-semibold border-b-2 border-transparent text-slate-500 hover:text-slate-700 flex items-center space-x-2';
    formCase.classList.remove('hidden');
    formCnr.classList.add('hidden');
    loadCaptcha('casestatus');
  }
}

// Load Captcha Bundle (Image, Audio, Auto-solved text)
async function loadCaptcha(page = 'casestatus') {
  const cnrImg = document.getElementById('cnr-captcha-img');
  const caseImg = document.getElementById('case-captcha-img');
  const cnrLoad = document.getElementById('cnr-captcha-loading');
  const caseLoad = document.getElementById('case-captcha-loading');
  const cnrInput = document.getElementById('cnr-captcha-input');
  const caseInput = document.getElementById('case-captcha-input');

  if (cnrLoad) cnrLoad.classList.remove('hidden');
  if (caseLoad) caseLoad.classList.remove('hidden');
  if (cnrImg) cnrImg.classList.add('hidden');
  if (caseImg) caseImg.classList.add('hidden');

  try {
    const res = await fetch(`/api/ecourts/captcha?page=${page}`);
    const data = await res.json();

    if (data.success && data.image_data_url) {
      if (cnrImg) {
        cnrImg.src = data.image_data_url;
        cnrImg.classList.remove('hidden');
      }
      if (caseImg) {
        caseImg.src = data.image_data_url;
        caseImg.classList.remove('hidden');
      }
      if (cnrInput) cnrInput.value = data.solved_captcha || '';
      if (caseInput) caseInput.value = data.solved_captcha || '';
      currentAudioUrl = data.audio_url || null;
    }
  } catch (err) {
    console.warn('Captcha load issue:', err);
  } finally {
    if (cnrLoad) cnrLoad.classList.add('hidden');
    if (caseLoad) caseLoad.classList.add('hidden');
  }
}

function playCaptchaAudio() {
  if (!currentAudioUrl) {
    alert('Audio captcha is not available for this session.');
    return;
  }
  const audio = document.getElementById('captcha-audio-player');
  audio.src = currentAudioUrl;
  audio.play().catch(e => console.error('Audio play failed:', e));
}

function setCNR(val) {
  document.getElementById('cnr-input').value = val;
}

// Search by CNR
async function executeCNRSearch() {
  const cnr = document.getElementById('cnr-input').value.trim();
  const captcha = document.getElementById('cnr-captcha-input').value.trim();

  if (!cnr || cnr.length !== 16) {
    alert('Please enter a valid 16-character CNR number.');
    return;
  }

  showScraperLoading(true);

  try {
    const res = await fetch('/api/ecourts/search/cnr', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cnr_number: cnr,
        captcha_code: captcha || null,
        use_resilience_fallback: true
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Search failed');
    }

    const caseData = await res.json();
    currentCaseData = caseData;
    renderCaseDetails(caseData);
  } catch (err) {
    alert('Case Search Error: ' + err.message);
  } finally {
    showScraperLoading(false);
  }
}

// Search by Case Number
async function executeCaseNumberSearch() {
  const state = document.getElementById('sel-state').value;
  const dist = document.getElementById('sel-district').value;
  const complex = document.getElementById('sel-complex').value;
  const est = document.getElementById('sel-est').value;
  const caseType = document.getElementById('sel-casetype').value;
  const caseNo = document.getElementById('case-no-input').value.trim();
  const year = document.getElementById('case-year-input').value.trim();
  const captcha = document.getElementById('case-captcha-input').value.trim();

  if (!caseNo || !year) {
    alert('Please enter both Case Number and Year.');
    return;
  }

  showScraperLoading(true);

  try {
    const res = await fetch('/api/ecourts/search/case-number', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        state_code: state,
        dist_code: dist,
        court_complex_code: complex,
        est_code: est,
        case_type: caseType,
        case_no: caseNo,
        year: year,
        captcha_code: captcha || null,
        use_resilience_fallback: true
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Search failed');
    }

    const payload = await res.json();
    if (payload.case) {
      currentCaseData = payload.case;
      renderCaseDetails(payload.case);
    } else if (payload.summaries && payload.summaries.length > 0) {
      alert(`Found ${payload.summaries.length} cases matching. Drilldown triggered.`);
    } else {
      alert('No matching cases found for the given criteria.');
    }
  } catch (err) {
    alert('Search Error: ' + err.message);
  } finally {
    showScraperLoading(false);
  }
}

function prefillSaketExample() {
  document.getElementById('sel-state').value = '26';
  document.getElementById('sel-district').value = '10';
  document.getElementById('sel-complex').value = '1260011@1,2,3,4@Y';
  document.getElementById('sel-est').value = '1';
  document.getElementById('sel-casetype').value = '77^1';
  document.getElementById('case-no-input').value = '233';
  document.getElementById('case-year-input').value = '2024';
}

function showScraperLoading(show) {
  const loader = document.getElementById('scraper-loading');
  const result = document.getElementById('case-result-container');
  if (show) {
    loader.classList.remove('hidden');
    result.classList.add('hidden');
  } else {
    loader.classList.add('hidden');
  }
}

// Render Case Details onto UI
function renderCaseDetails(caseData) {
  const container = document.getElementById('case-result-container');
  container.classList.remove('hidden');

  // Top Card
  document.getElementById('badge-case-type').textContent = caseData.case_details.case_type || 'CASE';
  document.getElementById('view-cnr').textContent = caseData.cnr_number;
  document.getElementById('view-reg-no').textContent = caseData.case_details.registration_number || '---';
  document.getElementById('view-judge').textContent = caseData.case_status.court_number_and_judge || 'District Judge';

  const petName = caseData.petitioners.length ? caseData.petitioners[0].name : 'Petitioner';
  const respName = caseData.respondents.length ? caseData.respondents[0].name : 'Respondent';
  document.getElementById('view-parties-vs').textContent = `${petName} Vs ${respName}`;

  document.getElementById('case-source-label').textContent = 
    caseData.source === 'live' ? 'Live eCourts Portal' : 'Verified Resilience Dataset';

  // Stats
  document.getElementById('stat-first-hearing').textContent = caseData.case_status.first_hearing_date || '---';
  document.getElementById('stat-decision-date').textContent = 
    caseData.case_status.decision_date || caseData.case_status.next_hearing_date || '---';
  document.getElementById('stat-stage').textContent = caseData.case_status.case_stage || 'Pending';
  document.getElementById('stat-filing-no').textContent = caseData.case_details.filing_number || '---';

  // 1. Parties List
  const petList = document.getElementById('list-petitioners');
  petList.innerHTML = caseData.petitioners.map((p, i) => `
    <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
      <div class="font-bold text-sm text-slate-800">${i + 1}. ${p.name}</div>
      ${p.advocate ? `<div class="text-xs text-brand-700 font-semibold mt-1 flex items-center space-x-1">
        <span>Advocate:</span> <strong>${p.advocate}</strong>
      </div>` : ''}
      ${p.address ? `<div class="text-xs text-slate-500 mt-0.5">${p.address}</div>` : ''}
    </div>
  `).join('') || '<div class="text-xs text-slate-400">None specified</div>';

  const respList = document.getElementById('list-respondents');
  respList.innerHTML = caseData.respondents.map((r, i) => `
    <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
      <div class="font-bold text-sm text-slate-800">${i + 1}. ${r.name}</div>
      ${r.advocate ? `<div class="text-xs text-brand-700 font-semibold mt-1">Advocate: ${r.advocate}</div>` : ''}
      ${r.address ? `<div class="text-xs text-slate-500 mt-0.5">${r.address}</div>` : ''}
    </div>
  `).join('') || '<div class="text-xs text-slate-400">None specified</div>';

  // 2. Filing & Acts
  const filingTable = document.getElementById('table-filing-details');
  filingTable.innerHTML = `
    <tr><td class="py-1.5 text-slate-500 font-medium">Case Type</td><td class="py-1.5 text-slate-800 font-semibold text-right">${caseData.case_details.case_type || '---'}</td></tr>
    <tr><td class="py-1.5 text-slate-500 font-medium">Filing Number</td><td class="py-1.5 text-slate-800 font-semibold text-right">${caseData.case_details.filing_number || '---'}</td></tr>
    <tr><td class="py-1.5 text-slate-500 font-medium">Filing Date</td><td class="py-1.5 text-slate-800 font-semibold text-right">${caseData.case_details.filing_date || '---'}</td></tr>
    <tr><td class="py-1.5 text-slate-500 font-medium">Registration Number</td><td class="py-1.5 text-slate-800 font-semibold text-right">${caseData.case_details.registration_number || '---'}</td></tr>
    <tr><td class="py-1.5 text-slate-500 font-medium">Registration Date</td><td class="py-1.5 text-slate-800 font-semibold text-right">${caseData.case_details.registration_date || '---'}</td></tr>
    <tr><td class="py-1.5 text-slate-500 font-medium">CNR Number</td><td class="py-1.5 text-brand-700 font-mono font-bold text-right">${caseData.cnr_number}</td></tr>
  `;

  const actsList = document.getElementById('list-acts');
  actsList.innerHTML = caseData.acts.map(a => `
    <div class="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex justify-between items-center text-xs">
      <span class="font-bold text-slate-700">${a.act}</span>
      <span class="px-2 py-0.5 rounded bg-brand-50 text-brand-700 font-semibold border border-brand-200">${a.section || 'General'}</span>
    </div>
  `).join('') || '<div class="text-xs text-slate-400">No specific acts recorded</div>';

  // 3. Hearing History
  document.getElementById('history-count').textContent = caseData.hearing_history.length;
  const historyTimeline = document.getElementById('history-timeline');
  historyTimeline.innerHTML = caseData.hearing_history.map(h => `
    <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-2 text-xs">
      <div class="space-y-0.5">
        <div class="font-bold text-slate-800">${h.judge || 'Presiding Judge'}</div>
        <div class="text-slate-500">Business Date: <strong>${h.business_on_date || '---'}</strong></div>
      </div>
      <div class="flex items-center space-x-3">
        <span class="px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-700 font-semibold border border-indigo-200">
          ${h.purpose || 'Judicial Proceedings'}
        </span>
        <span class="font-mono text-slate-600 font-medium">${h.hearing_date || ''}</span>
      </div>
    </div>
  `).join('') || '<div class="text-xs text-slate-400">No hearings recorded</div>';

  // 4. Orders & Judgments
  document.getElementById('orders-count').textContent = caseData.orders.length;
  const ordersList = document.getElementById('orders-list');
  ordersList.innerHTML = caseData.orders.map(o => `
    <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between text-xs">
      <div class="space-y-0.5">
        <div class="font-bold text-slate-800 flex items-center space-x-2">
          <span>Order #${o.order_number || '1'}</span>
          ${o.is_judgment ? '<span class="px-2 py-0.5 rounded bg-rose-50 text-rose-700 font-bold border border-rose-200">FINAL JUDGMENT</span>' : ''}
        </div>
        <div class="text-slate-500">${o.order_details} • Dated: <strong>${o.order_date}</strong></div>
      </div>
      <div>
        ${o.pdf_url ? `
          <a href="${o.pdf_url}" target="_blank" class="px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white font-semibold flex items-center space-x-1.5 transition">
            <i data-lucide="file-text" class="w-3.5 h-3.5"></i>
            <span>View PDF</span>
          </a>
        ` : '<span class="text-slate-400">Not Available</span>'}
      </div>
    </div>
  `).join('') || '<div class="text-xs text-slate-400">No orders uploaded</div>';

  if (window.lucide) window.lucide.createIcons();
}

function switchCaseDetailTab(tab) {
  document.querySelectorAll('.cd-tab-btn').forEach(b => {
    b.className = 'cd-tab-btn py-3.5 text-xs font-bold uppercase tracking-wider border-b-2 border-transparent text-slate-500 hover:text-slate-700';
  });
  document.querySelectorAll('.cd-pane').forEach(p => p.classList.add('hidden'));

  const btn = document.getElementById(`cd-tab-${tab}`);
  const pane = document.getElementById(`cd-pane-${tab}`);
  if (btn) btn.className = 'cd-tab-btn py-3.5 text-xs font-bold uppercase tracking-wider border-b-2 border-brand-600 text-brand-700';
  if (pane) pane.classList.remove('hidden');

  if (window.lucide) window.lucide.createIcons();
}

// Download / Copy Case JSON
function downloadCaseJson() {
  if (!currentCaseData) return;
  const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(currentCaseData, null, 2));
  const dlAnchor = document.createElement('a');
  dlAnchor.setAttribute('href', dataStr);
  dlAnchor.setAttribute('download', `case_${currentCaseData.cnr_number}.json`);
  dlAnchor.click();
}

function copyCaseJson() {
  if (!currentCaseData) return;
  navigator.clipboard.writeText(JSON.stringify(currentCaseData, null, 2));
  alert('Case JSON copied to clipboard!');
}

// Cross-Task Synergy: Pre-fill Legal Draft Studio from Scraped Case
function prefillDraftFromCurrentCase() {
  if (!currentCaseData) return;

  switchMainTab('drafting');

  document.getElementById('draft-template').value = 'commercial_suit';
  document.getElementById('draft-court-name').value = 'IN THE COURT OF DISTRICT JUDGE (COMMERCIAL COURT) AT SAKET, NEW DELHI';
  document.getElementById('draft-suit-no').value = `${currentCaseData.case_details.case_type || 'CS (COMM)'} NO. ${currentCaseData.case_details.registration_number || '233/2024'}`;
  document.getElementById('draft-cnr').value = currentCaseData.cnr_number;

  if (currentCaseData.petitioners.length) {
    document.getElementById('draft-p1-name').value = currentCaseData.petitioners[0].name;
    document.getElementById('draft-p1-addr').value = currentCaseData.petitioners[0].address || 'Branch Office at Saket, New Delhi';
    if (currentCaseData.petitioners[0].advocate) {
      document.getElementById('draft-adv-name').value = currentCaseData.petitioners[0].advocate;
    }
  }

  if (currentCaseData.respondents.length) {
    document.getElementById('draft-d1-name').value = currentCaseData.respondents[0].name;
    document.getElementById('draft-d1-addr').value = currentCaseData.respondents[0].address || 'R/o South District, New Delhi';
  }

  generateLegalDraft();
}

// Legal Draft Generator Logic
function onTemplateSelectionChange() {
  const tid = document.getElementById('draft-template').value;
  if (tid === 'bail_application') {
    document.getElementById('draft-court-name').value = 'IN THE COURT OF SESSIONS JUDGE, NEW DELHI';
    document.getElementById('draft-suit-no').value = 'BAIL APPLICATION NO. _____ OF 2024';
  } else if (tid === 'consumer_complaint') {
    document.getElementById('draft-court-name').value = 'BEFORE THE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION, NEW DELHI';
    document.getElementById('draft-suit-no').value = 'CONSUMER COMPLAINT NO. _____ OF 2024';
  } else if (tid === 'legal_notice') {
    document.getElementById('draft-court-name').value = 'LEGAL NOTICE UNDER SECTION 80 CPC';
    document.getElementById('draft-suit-no').value = 'REF: LN/2024/09';
  } else {
    document.getElementById('draft-court-name').value = 'IN THE COURT OF DISTRICT JUDGE (COMMERCIAL COURT) AT SAKET, NEW DELHI';
    document.getElementById('draft-suit-no').value = 'CS (COMM) NO. 233 OF 2024';
  }
  generateLegalDraft();
}

function addFactInputRow() {
  const container = document.getElementById('facts-container');
  const div = document.createElement('div');
  div.className = 'flex gap-2';
  div.innerHTML = `
    <input type="text" placeholder="Date" class="fact-date w-28 px-2 py-1.5 text-xs rounded-lg border border-slate-300 font-mono shrink-0">
    <input type="text" placeholder="Fact narrative" class="fact-narrative flex-1 px-2.5 py-1.5 text-xs rounded-lg border border-slate-300">
  `;
  container.appendChild(div);
}

function collectDraftInput() {
  const facts = [];
  const factRows = document.querySelectorAll('#facts-container .flex');
  factRows.forEach(row => {
    const dt = row.querySelector('.fact-date').value.trim();
    const narr = row.querySelector('.fact-narrative').value.trim();
    if (narr) {
      facts.push({ date: dt || null, narrative: narr });
    }
  });

  return {
    template_id: document.getElementById('draft-template').value,
    court_name: document.getElementById('draft-court-name').value,
    case_type_number_year: document.getElementById('draft-suit-no').value,
    cnr_number: document.getElementById('draft-cnr').value || null,
    plaintiffs: [{
      name: document.getElementById('draft-p1-name').value,
      address: document.getElementById('draft-p1-addr').value,
      is_corporate: document.getElementById('draft-p1-name').value.toLowerCase().includes('bank')
    }],
    defendants: [{
      name: document.getElementById('draft-d1-name').value,
      address: document.getElementById('draft-d1-addr').value
    }],
    advocate: {
      name: document.getElementById('draft-adv-name').value,
      bar_council_number: document.getElementById('draft-adv-reg').value,
      office_address: 'Chamber No. 512, Lawyers Chambers Block, Saket Courts Complex, New Delhi'
    },
    total_claim_amount: parseFloat(document.getElementById('draft-claim-amt').value) || 0,
    cause_of_action_date: document.getElementById('draft-coa-date').value,
    facts: facts,
    place: 'New Delhi',
    date: new Date().toLocaleDateString('en-GB')
  };
}

async function generateLegalDraft() {
  const payload = collectDraftInput();

  try {
    const res = await fetch('/api/drafting/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Draft generation failed');
    }

    const draft = await res.json();
    currentDraftOutput = draft;

    // Render Preview
    document.getElementById('draft-preview-content').innerHTML = draft.html;
    document.getElementById('draft-markdown-content').textContent = draft.markdown;
    document.getElementById('draft-json-content').textContent = JSON.stringify(draft.structured_sections, null, 2);

  } catch (err) {
    console.error('Draft generation error:', err);
  }
}

function switchDraftPreviewMode(mode) {
  document.querySelectorAll('.dp-tab').forEach(b => {
    b.className = 'dp-tab px-3 py-1.5 text-xs font-bold rounded-lg text-slate-600 hover:bg-slate-200 transition';
  });

  document.getElementById('draft-pane-preview').classList.add('hidden');
  document.getElementById('draft-pane-markdown').classList.add('hidden');
  document.getElementById('draft-pane-json').classList.add('hidden');

  const btn = document.getElementById(`dp-tab-${mode}`);
  const pane = document.getElementById(`draft-pane-${mode}`);
  if (btn) btn.className = 'dp-tab px-3 py-1.5 text-xs font-bold rounded-lg bg-indigo-600 text-white transition';
  if (pane) pane.classList.remove('hidden');
}

async function exportDocx() {
  const payload = collectDraftInput();
  try {
    const res = await fetch('/api/drafting/export/docx', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error('DOCX export failed');

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${payload.template_id}_draft.docx`;
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (e) {
    alert('Word Export Error: ' + e.message);
  }
}

function printLegalDraft() {
  if (!currentDraftOutput) return;
  const printWin = window.open('', '_blank');
  printWin.document.write(currentDraftOutput.html);
  printWin.document.close();
  printWin.focus();
  setTimeout(() => printWin.print(), 250);
}

function copyDraftText() {
  if (!currentDraftOutput) return;
  navigator.clipboard.writeText(currentDraftOutput.plain_text);
  alert('Legal draft copied to clipboard!');
}

