import React, { useState, useEffect } from "react";
import { Search, RefreshCw, Building2, CheckCircle2 } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { CaptchaResponse, CaseRecord } from "../types";

interface CaseNumberSearchProps {
  onCaseFound: (data: CaseRecord) => void;
  isLoading: boolean;
  setIsLoading: (val: boolean) => void;
  setError: (msg: string | null) => void;
}

export const CaseNumberSearch: React.FC<CaseNumberSearchProps> = ({
  onCaseFound,
  isLoading,
  setIsLoading,
  setError,
}) => {
  const [stateCode, setStateCode] = useState("26"); // Delhi
  const [districtCode, setDistrictCode] = useState("10"); // South
  const [courtComplexCode, setCourtComplexCode] = useState("1260011@1,2,3,4@Y"); // Saket Court Complex
  const [establishmentCode, setEstablishmentCode] = useState("1"); // District & Sessions Judge, South, Saket
  const [caseType, setCaseType] = useState("77^1"); // CS (COMM)
  const [caseNumber, setCaseNumber] = useState("233");
  const [year, setYear] = useState("2024");

  const [captchaData, setCaptchaData] = useState<CaptchaResponse | null>(null);
  const [captchaInput, setCaptchaInput] = useState("");
  const [captchaLoading, setCaptchaLoading] = useState(false);

  const fetchCaptcha = async () => {
    setCaptchaLoading(true);
    try {
      const res = await fetch("/api/ecourts/captcha");
      if (!res.ok) throw new Error("Failed to fetch CAPTCHA challenge");
      const data: CaptchaResponse = await res.json();
      setCaptchaData(data);
      if (data.solved_captcha) {
        setCaptchaInput(data.solved_captcha);
      }
    } catch (err: any) {
      console.warn("Captcha fetch error:", err);
    } finally {
      setCaptchaLoading(false);
    }
  };

  useEffect(() => {
    fetchCaptcha();
  }, []);

  const handlePreloadSaketSuit = () => {
    setStateCode("26");
    setDistrictCode("10");
    setCourtComplexCode("1260011@1,2,3,4@Y");
    setEstablishmentCode("1");
    setCaseType("77^1");
    setCaseNumber("233");
    setYear("2024");
    setError(null);
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!caseNumber.trim() || !year.trim()) {
      setError("Please specify Case Number and Filing Year.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const payload = {
        state_code: stateCode,
        dist_code: districtCode,
        court_complex_code: courtComplexCode,
        est_code: establishmentCode,
        case_type: caseType,
        case_no: caseNumber.trim(),
        year: year.trim(),
        captcha_code: captchaInput.trim() || undefined,
        use_resilience_fallback: true,
      };

      const res = await fetch("/api/ecourts/search/case-number", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await res.json();
      if (!res.ok) {
        throw new Error(result.detail || "Failed to locate case in court registry");
      }

      if (result.case) {
        onCaseFound(result.case);
      } else if (result.summaries && result.summaries.length > 0) {
        // If exact case details weren't drilled down, fallback or display summary
        onCaseFound(result.case || result.summaries[0]);
      } else {
        throw new Error("No cases matching the query were found in this court establishment.");
      }
    } catch (err: any) {
      setError(err.message || "An error occurred during case number search");
      fetchCaptcha();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Quick Fill Preset */}
      <div className="flex items-center justify-between p-2.5 rounded-lg border border-indigo-100 bg-indigo-50/50 dark:border-indigo-900/50 dark:bg-indigo-950/20">
        <div className="flex items-center space-x-2">
          <Building2 className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
          <span className="text-xs font-medium text-indigo-900 dark:text-indigo-300">
            Target Case: Saket Court Complex • CS (COMM) 233/2024
          </span>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handlePreloadSaketSuit}
          className="text-xs h-7 border-indigo-200 text-indigo-700 hover:bg-indigo-100 dark:border-indigo-800 dark:text-indigo-300 dark:hover:bg-indigo-900/40"
        >
          Load Parameters
        </Button>
      </div>

      <form onSubmit={handleSearch} className="space-y-4">
        {/* State & District Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
              Select State
            </label>
            <select
              value={stateCode}
              onChange={(e) => setStateCode(e.target.value)}
              className="flex h-9 w-full rounded-lg border border-zinc-200 bg-white px-3 py-1 text-sm shadow-xs focus:outline-none focus:ring-2 focus:ring-zinc-950/20 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
            >
              <option value="26">Delhi</option>
              <option value="1">Maharashtra</option>
              <option value="16">Karnataka</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
              Select District
            </label>
            <select
              value={districtCode}
              onChange={(e) => setDistrictCode(e.target.value)}
              className="flex h-9 w-full rounded-lg border border-zinc-200 bg-white px-3 py-1 text-sm shadow-xs focus:outline-none focus:ring-2 focus:ring-zinc-950/20 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
            >
              <option value="10">South (Saket)</option>
              <option value="2">New Delhi (Patiala House)</option>
              <option value="1">Central (Tis Hazari)</option>
            </select>
          </div>
        </div>

        {/* Court Complex & Establishment Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
              Select Court Complex
            </label>
            <select
              value={courtComplexCode}
              onChange={(e) => setCourtComplexCode(e.target.value)}
              className="flex h-9 w-full rounded-lg border border-zinc-200 bg-white px-3 py-1 text-sm shadow-xs focus:outline-none focus:ring-2 focus:ring-zinc-950/20 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
            >
              <option value="1260011@1,2,3,4@Y">Saket Court Complex</option>
              <option value="1260002@1,2@Y">Patiala House Court Complex</option>
              <option value="1260001@1,2,3,4@Y">Tis Hazari Court Complex</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
              Select Establishment
            </label>
            <select
              value={establishmentCode}
              onChange={(e) => setEstablishmentCode(e.target.value)}
              className="flex h-9 w-full rounded-lg border border-zinc-200 bg-white px-3 py-1 text-sm shadow-xs focus:outline-none focus:ring-2 focus:ring-zinc-950/20 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
            >
              <option value="1">District and Sessions Judge, South, Saket</option>
              <option value="2">Chief Metropolitan Magistrate, South, Saket</option>
            </select>
          </div>
        </div>

        {/* Case Type, Number, and Year Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="sm:col-span-1">
            <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
              Case Type <span className="text-red-500">*</span>
            </label>
            <select
              value={caseType}
              onChange={(e) => setCaseType(e.target.value)}
              className="flex h-9 w-full rounded-lg border border-zinc-200 bg-white px-3 py-1 text-sm shadow-xs focus:outline-none focus:ring-2 focus:ring-zinc-950/20 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100 font-mono text-xs"
            >
              <option value="77^1">CS (COMM) - CIVIL SUIT (COMMERCIAL)</option>
              <option value="1^1">CS - CIVIL SUIT</option>
              <option value="2^1">MCA - MISC CIVIL APPEAL</option>
              <option value="12^2">BAIL APPLN - BAIL APPLICATION</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
              Case Number <span className="text-red-500">*</span>
            </label>
            <Input
              type="text"
              value={caseNumber}
              onChange={(e) => setCaseNumber(e.target.value)}
              placeholder="e.g. 233"
              className="h-9 font-mono"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
              Filing Year <span className="text-red-500">*</span>
            </label>
            <Input
              type="text"
              value={year}
              onChange={(e) => setYear(e.target.value)}
              placeholder="e.g. 2024"
              maxLength={4}
              className="h-9 font-mono"
              required
            />
          </div>
        </div>

        {/* Captcha Section */}
        <div className="p-3.5 rounded-lg border border-zinc-200/80 bg-zinc-50/60 dark:border-zinc-800 dark:bg-zinc-900/40 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-700 dark:text-zinc-300">
              Security Verification
            </span>
            <button
              type="button"
              onClick={fetchCaptcha}
              disabled={captchaLoading}
              className="p-1 text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 rounded cursor-pointer"
            >
              <RefreshCw className={`h-4 w-4 ${captchaLoading ? "animate-spin" : ""}`} />
            </button>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="h-10 w-36 bg-white dark:bg-zinc-950 rounded border border-zinc-300 dark:border-zinc-700 flex items-center justify-center overflow-hidden shrink-0">
              {captchaData?.image_data_url ? (
                <img
                  src={captchaData.image_data_url}
                  alt="eCourts CAPTCHA"
                  className="h-full w-full object-contain filter contrast-125"
                />
              ) : (
                <span className="text-xs text-zinc-400 animate-pulse">Loading...</span>
              )}
            </div>

            <div className="w-full relative">
              <Input
                type="text"
                value={captchaInput}
                onChange={(e) => setCaptchaInput(e.target.value)}
                placeholder="Enter CAPTCHA text"
                maxLength={8}
                className="h-10 font-mono text-sm tracking-widest uppercase"
              />
              {captchaData?.solved_captcha && (
                <div className="absolute right-2.5 top-2 flex items-center space-x-1 text-emerald-600 dark:text-emerald-400 text-[10px] font-mono">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>Auto-Detected</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Submit */}
        <Button
          type="submit"
          disabled={isLoading || !caseNumber || !year}
          className="w-full h-11 text-sm font-semibold tracking-wide space-x-2 shadow-sm"
        >
          {isLoading ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Navigating Court Hierarchy & Extracting Records...</span>
            </>
          ) : (
            <>
              <Search className="h-4 w-4" />
              <span>Search District Court Registry</span>
            </>
          )}
        </Button>
      </form>
    </div>
  );
};
