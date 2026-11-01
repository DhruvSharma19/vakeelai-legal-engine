import React from "react";
import { ShieldCheck, Cpu, Database, Network, ArrowRight, Layers, FileCode2, Lock } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";

export const ArchitectureView: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Intro Header */}
      <div>
        <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
          Reverse-Engineering & System Architecture
        </h2>
        <p className="text-xs sm:text-sm text-zinc-500 dark:text-zinc-400 mt-1 max-w-3xl">
          Detailed breakdown of the programmatic HTTP protocol replication of the eCourts District Portal (`services.ecourts.gov.in/ecourtindia_v6`) and the pure-Python legal template generation engine.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Card 1: Dynamic Delimiter & Header Bypass */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center space-x-2">
              <Lock className="h-4 w-4 text-indigo-500" />
              <span>1. Dynamic Delimiter & Rotating Header Key</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs space-y-2 text-zinc-600 dark:text-zinc-400 leading-relaxed">
            <p>
              eCourts protects endpoints against simple scraping by rotating an internal delimiter string and a randomized custom HTTP header key inside <code className="text-indigo-600 dark:text-indigo-400 font-mono">components.js?v=...</code>.
            </p>
            <div className="p-3 rounded-lg bg-zinc-950 text-zinc-100 font-mono text-[11px] leading-snug">
              headers: &#123;<br />
              &nbsp;&nbsp;"delimeter": "opiyoe645",<br />
              &nbsp;&nbsp;"Biure465": "opiyoe645" // Random rotated key<br />
              &#125;
            </div>
            <p>
              <strong className="text-zinc-900 dark:text-zinc-100">Implementation:</strong> On session initialization, our HTTP client fetches the active script bundle, extracts the live delimiter and header key via regex AST extraction, and binds them to all subsequent requests.
            </p>
          </CardContent>
        </Card>

        {/* Card 2: Offline ONNX Neural Network OCR */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center space-x-2">
              <Cpu className="h-4 w-4 text-emerald-500" />
              <span>2. Offline ONNX Neural Network CAPTCHA</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs space-y-2 text-zinc-600 dark:text-zinc-400 leading-relaxed">
            <p>
              eCourts issues distorted 6-character alphanumeric Securimage CAPTCHAs. Traditional Tesseract OCR fails due to character twisting and grid noise.
            </p>
            <div className="p-3 rounded-lg bg-zinc-950 text-emerald-400 font-mono text-[11px] leading-snug">
              Input: Image Bytes &rarr; PIL Contrast Filter &rarr; ONNX Runtime Model &rarr; Solution (~15ms CPU)
            </div>
            <p>
              <strong className="text-zinc-900 dark:text-zinc-100">Implementation:</strong> Uses an embedded neural network (<code className="font-mono">ddddocr</code>) executed locally on CPU. Requires zero external paid APIs, zero third-party cloud services, and zero LLMs.
            </p>
          </CardContent>
        </Card>

        {/* Card 3: Session Cookies & Token Synchronization */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center space-x-2">
              <Network className="h-4 w-4 text-blue-500" />
              <span>3. Token Synchronization & Cookie Jar</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs space-y-2 text-zinc-600 dark:text-zinc-400 leading-relaxed">
            <p>
              The portal tracks sessions with <code className="font-mono text-zinc-900 dark:text-zinc-100">SERVICES_SESSID</code> and a 64-character SHA256 <code className="font-mono text-zinc-900 dark:text-zinc-100">app_token</code> in the DOM.
            </p>
            <p>
              After each AJAX request, the server responds with a dynamic token enclosed in a delimiter string <code className="font-mono text-indigo-500">#####&lt;token&gt;#####</code>. Our client intercepts this string and continuously synchronizes the token state to keep the session alive.
            </p>
          </CardContent>
        </Card>

        {/* Card 4: NIC WAF Resilience & High Availability */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center space-x-2">
              <ShieldCheck className="h-4 w-4 text-amber-500" />
              <span>4. NIC WAF Resilience & Datacenter Fallback</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs space-y-2 text-zinc-600 dark:text-zinc-400 leading-relaxed">
            <p>
              The National Informatics Centre (NIC) firewall frequently blocks or throttles foreign cloud hosting IPs (Render, Railway, AWS US-East, Streamlit Cloud).
            </p>
            <p>
              <strong className="text-zinc-900 dark:text-zinc-100">Implementation:</strong> The scraper queries the live eCourts portal first. If the NIC firewall times out or blocks the request with HTTP 403, the system seamlessly activates a verified genuine snapshot for reference cases, ensuring 100% demo reliability.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Legal Drafting Engine Architecture */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold flex items-center space-x-2">
            <FileCode2 className="h-4 w-4 text-zinc-900 dark:text-zinc-100" />
            <span>Pure-Python Legal Template Generator (Zero-LLM Architecture)</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed">
          <p>
            Built strictly in pure Python without LLMs or external APIs using deterministic rule-based engines:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
            <div className="p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/60">
              <div className="font-semibold text-zinc-900 dark:text-zinc-100 mb-1">
                Order VII CPC Rulebook
              </div>
              <p className="text-[11px]">
                Enforces territorial jurisdiction averments, cause of action dates, pecuniary valuation, court fees, and mandatory Section 12A mediation statements.
              </p>
            </div>

            <div className="p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/60">
              <div className="font-semibold text-zinc-900 dark:text-zinc-100 mb-1">
                Statement of Truth Jurat
              </div>
              <p className="text-[11px]">
                Appends the mandatory affidavit verification under Order VI Rule 15A of the CPC as amended by the Commercial Courts Act 2015.
              </p>
            </div>

            <div className="p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/60">
              <div className="font-semibold text-zinc-900 dark:text-zinc-100 mb-1">
                Indian Currency Converter
              </div>
              <p className="text-[11px]">
                Converts numbers into official Indian words (&ldquo;Rupees Fifteen Lakh Fifty Thousand Only&rdquo;) complying with court registry conventions.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
