"""
Low-Level eCourts Network Client
--------------------------------
Reverse-engineers and programmatically executes the exact browser network flow of:
https://services.ecourts.gov.in/ecourtindia_v6/

Design Choices & Technical Innovations:
---------------------------------------
1. Session & Cookie Persistence:
   Maintains `SERVICES_SESSID` and `JSESSION` cookies using `requests.Session`.
2. Dynamic Delimiter & Header Rotation Bypass:
   eCourts dynamically changes an internal JavaScript delimiter and rotates a secondary
   custom request header (e.g. `delimeter: "opiyoe645"`, `Biure465: "opiyoe645"`)
   embedded in versioned script bundles (`components.js?v=...`).
   This client parses the active script tag on every session init, extracts the live
   header dictionary and delimiter, and automatically injects them into all subsequent requests.
3. Live `app_token` Synchronization:
   Extracts initial SHA256 `app_token` from the DOM, and updates it whenever an AJAX
   response sends back a refreshed token (via JSON key or `#####<token>#####` delimiter).
4. Resilience & Fallback:
   If the eCourts server is unresponsive or blocking datacenter IPs, errors are cleanly
   caught and reported, allowing upper layers to fall back seamlessly without crashing.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple, List
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ECourtsClient:
    """
    HTTP Client that mirrors browser DevTools network flow against the eCourts portal.
    """

    BASE_URL = "https://services.ecourts.gov.in/ecourtindia_v6"

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    def __init__(self, timeout: int = 15):
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self.timeout = timeout

        self.app_token: str = ""
        self.delimeter: str = "opiyoe645"
        self.dynamic_headers: Dict[str, str] = {"delimeter": self.delimeter}
        self.last_captcha_img_url: Optional[str] = None
        self.last_captcha_audio_url: Optional[str] = None
        self.initialized_page: Optional[str] = None  # 'home' or 'casestatus'

    def init_session(self, page: str = "casestatus") -> bool:
        """
        Loads the entry page, sets cookies, extracts the app_token,
        fetches components.js to parse the active rotating headers and delimiter.
        """
        try:
            target_url = f"{self.BASE_URL}/?p=casestatus/index" if page == "casestatus" else f"{self.BASE_URL}/"
            resp = self.session.get(target_url, timeout=self.timeout)
            if resp.status_code != 200:
                logger.warning(f"Failed to load eCourts {page} page: status {resp.status_code}")
                return False

            html = resp.text

            # 1. Extract app_token from hidden input
            m_tok = re.search(r"id=[\"']app_token[\"']\s*value=[\"']([^\"']*)[\"']", html)
            if not m_tok:
                m_tok = re.search(r"value=[\"']([^\"']+)[\"']\s*id=[\"']app_token[\"']", html)
            if m_tok:
                self.app_token = m_tok.group(1).strip()
            else:
                self.app_token = ""

            # 2. Extract captcha URL if present on initial page
            m_cap = re.search(r"id=[\"']captcha_image[\"'][^>]*src=[\"']([^\"']+)[\"']", html)
            if m_cap:
                raw_cap_src = m_cap.group(1)
                self.last_captcha_img_url = (
                    raw_cap_src if raw_cap_src.startswith("http") else f"{self.BASE_URL}/{raw_cap_src.lstrip('/')}"
                )

            # 3. Extract components.js script tag
            m_comp = re.search(r"src=[\"'](/ecourtindia_v6/js/components\.js\?[^\"']+)[\"']", html)
            if m_comp:
                comp_url = f"https://services.ecourts.gov.in{m_comp.group(1)}"
                comp_resp = self.session.get(comp_url, timeout=self.timeout)
                if comp_resp.status_code == 200:
                    self._parse_components_js(comp_resp.text)

            self.initialized_page = page
            return True

        except Exception as e:
            logger.error(f"Error initializing eCourts session: {e}")
            return False

    def _parse_components_js(self, js_text: str):
        """
        Parses `components.js` to extract dynamic delimiter and rotating header fields.
        """
        m_del = re.search(r"delimeter\s*=\s*[\"']([^\"']+)[\"']", js_text)
        if m_del:
            self.delimeter = m_del.group(1).strip()

        # Parse headers block:
        # headers: { "delimeter": delimeter, "Biure465": delimeter }
        m_hdrs = re.search(r"headers:\s*\{([^}]+)\}", js_text)
        self.dynamic_headers = {"delimeter": self.delimeter}

        if m_hdrs:
            for line in m_hdrs.group(1).split(","):
                if ":" in line:
                    key = line.split(":", 1)[0].strip().strip("\"'")
                    if key:
                        self.dynamic_headers[key] = self.delimeter

    def post_ajax(self, endpoint: str, data: Dict[str, Any], referer_page: str = "casestatus/index") -> Dict[str, Any]:
        """
        Executes an AJAX POST request mirroring `ajaxCall` in `components.js`.
        Handles auto-token updates and header injections.
        """
        url = f"{self.BASE_URL}/?p={endpoint}"
        payload = dict(data)
        payload["ajax_req"] = "true"
        payload["app_token"] = self.app_token

        headers = {
            "User-Agent": self.DEFAULT_HEADERS["User-Agent"],
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.BASE_URL}/?p={referer_page}",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            **self.dynamic_headers,
        }

        resp = self.session.post(url, data=payload, headers=headers, timeout=self.timeout)

        # Check for token update in raw text (#####<token>##### pattern)
        if "#####" in resp.text:
            parts = resp.text.split("#####")
            if len(parts) > 1 and len(parts[1]) >= 32:
                self.app_token = parts[1].strip()

        try:
            res_json = resp.json()
            if isinstance(res_json, dict) and res_json.get("app_token"):
                self.app_token = res_json["app_token"]
            return res_json
        except Exception:
            return {"raw_text": resp.text, "status_code": resp.status_code}

    def fetch_captcha_image_and_audio(self, force_refresh: bool = False) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
        """
        Fetches the current captcha image bytes and audio URL.
        If on casestatus page, invokes `casestatus/getCaptcha` first.
        Returns: (image_bytes, image_url, audio_url)
        """
        try:
            img_url = self.last_captcha_img_url

            if self.initialized_page == "casestatus" or force_refresh:
                res = self.post_ajax("casestatus/getCaptcha", {}, referer_page="casestatus/index")
                div_html = res.get("div_captcha", "")
                m_img = re.search(r"src=[\"'](/ecourtindia_v6/vendor/securimage/securimage_show\.php\?[^\"']+)[\"']", div_html)
                if m_img:
                    img_url = f"https://services.ecourts.gov.in{m_img.group(1)}"
                    self.last_captcha_img_url = img_url

                m_aud = re.search(r"src=[\"'](/ecourtindia_v6/vendor/securimage/securimage_play\.php\?[^\"']+)[\"']", div_html)
                if m_aud:
                    self.last_captcha_audio_url = f"https://services.ecourts.gov.in{m_aud.group(1)}"

            if not img_url:
                # Default fallback URL for securimage
                img_url = f"{self.BASE_URL}/vendor/securimage/securimage_show.php"

            img_resp = self.session.get(img_url, timeout=self.timeout)
            if img_resp.status_code == 200:
                return img_resp.content, img_url, self.last_captcha_audio_url

            return None, None, None

        except Exception as e:
            logger.error(f"Error fetching captcha: {e}")
            return None, None, None

    # Cascade Methods
    def fill_district(self, state_code: str) -> Dict[str, Any]:
        """Fetches districts for a selected state."""
        return self.post_ajax("casestatus/fillDistrict", {"state_code": state_code})

    def fill_complex(self, state_code: str, dist_code: str) -> Dict[str, Any]:
        """Fetches court complexes for a selected state and district."""
        return self.post_ajax("casestatus/fillcomplex", {"state_code": state_code, "dist_code": dist_code})

    def fill_establishment(self, state_code: str, dist_code: str, court_complex_code: str) -> Dict[str, Any]:
        """Fetches establishments for a selected court complex."""
        return self.post_ajax(
            "casestatus/fillCourtEstablishment",
            {
                "state_code": state_code,
                "dist_code": dist_code,
                "court_complex_code": court_complex_code,
            },
        )

    def fill_case_type(self, state_code: str, dist_code: str, court_complex_code: str, est_code: str) -> Dict[str, Any]:
        """Fetches available case types for an establishment."""
        return self.post_ajax(
            "casestatus/fillCaseType",
            {
                "state_code": state_code,
                "dist_code": dist_code,
                "court_complex_code": court_complex_code,
                "est_code": est_code,
                "search_type": "c_no",
            },
        )

    # Search Execution Methods
    def search_by_cnr(self, cnr_number: str, captcha_code: str) -> Dict[str, Any]:
        """
        Executes CNR search via `POST cnr_status/searchByCNR/`.
        Returns portal response with `casetype_list` containing full case HTML on success.
        """
        payload = {
            "cino": cnr_number.strip().upper(),
            "fcaptcha_code": captcha_code.strip(),
        }
        return self.post_ajax("cnr_status/searchByCNR/", payload, referer_page="")

    def search_by_case_number(
        self,
        state_code: str,
        dist_code: str,
        court_complex_code: str,
        est_code: str,
        case_type: str,
        case_no: str,
        year: str,
        captcha_code: str,
    ) -> Dict[str, Any]:
        """
        Executes Case Number search via `POST casestatus/submitCaseNo`.
        Returns portal response with `case_data` containing the results table.
        """
        # Complex code format may be 1260011@1,2,3,4@Y; extract complex id
        complex_id = court_complex_code.split("@")[0] if "@" in court_complex_code else court_complex_code

        payload = {
            "search_case_no": case_no.strip(),
            "rgyear": year.strip(),
            "case_captcha_code": captcha_code.strip(),
            "state_code": state_code.strip(),
            "dist_code": dist_code.strip(),
            "court_complex_code": complex_id,
            "est_code": est_code.strip(),
            "case_type": case_type.strip(),
            "case_no": case_no.strip(),
        }
        return self.post_ajax("casestatus/submitCaseNo", payload, referer_page="casestatus/index")

    def view_case_history(
        self,
        court_code: str,
        state_code: str,
        dist_code: str,
        complex_code: str,
        case_no: str,
        cino: str,
    ) -> Dict[str, Any]:
        """
        Drills down into a specific case from the search results table via `home/viewHistory`.
        Returns full case HTML in `data_list`.
        """
        payload = {
            "court_code": court_code,
            "state_code": state_code,
            "dist_code": dist_code,
            "court_complex_code": complex_code,
            "case_no": case_no,
            "cino": cino,
            "hideparty": "",
            "search_flag": "CScaseNumber",
            "search_by": "CScaseNumber",
        }
        return self.post_ajax("home/viewHistory", payload, referer_page="casestatus/index")

    def display_pdf(self, normal_v: str, case_val: str, court_code: str, filename: str) -> Dict[str, Any]:
        """
        Invokes `home/display_pdf` to retrieve the PDF file path for an order.
        """
        payload = {
            "normal_v": normal_v,
            "case_val": case_val,
            "court_code": court_code,
            "filename": filename,
            "appFlag": "",
        }
        return self.post_ajax("home/display_pdf", payload, referer_page="casestatus/index")
