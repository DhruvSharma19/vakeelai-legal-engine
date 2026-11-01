import React, { useState, useEffect } from "react";
import { Search, RefreshCw, Volume2, Sparkles, CheckCircle2 } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { CaptchaResponse, CaseRecord } from "../types";

interface CNRSearchProps {
  onCaseFound: (data: CaseRecord) => void;
  isLoading: boolean;
  setIsLoading: (val: boolean) => void;
  setError: (msg: string | null) => void;
}

export const CNRSearch: React.FC<CNRSearchProps> = ({
  onCaseFound,
  isLoading,
  setIsLoading,
  setError,
}) => {
  const [cnr, setCnr] = useState("DLST010047302024");
  const [captchaData, setCaptchaData] = useState<CaptchaResponse | null>(null);
  const [captchaInput, setCaptchaInput] = useState("");
  const [captchaLoading, setCaptchaLoading] = useState(false);
  const [audioPlaying, setAudioPlaying] = useState(false);

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

  const handlePlayAudio = () => {
    if (!captchaData?.audio_url) return;
    setAudioPlaying(true);
    const audio = new Audio(captchaData.audio_url);
    audio.play();
    audio.onended = () => setAudioPlaying(false);
    audio.onerror = () => setAudioPlaying(false);
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const cleanCnr = cnr.trim().toUpperCase();
    if (!cleanCnr || cleanCnr.length !== 16) {
      setError("Please enter a valid 16-character alphanumeric CNR number.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const payload = {
        cnr_number: cleanCnr,
        captcha_code: captchaInput.trim() || undefined,
        use_resilience_fallback: true,
      };

      const res = await fetch("/api/ecourts/search/cnr", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await res.json();
      if (!res.ok) {
        throw new Error(result.detail || "Failed to retrieve case from eCourts portal");
      }

      onCaseFound(result);
    } catch (err: any) {
      setError(err.message || "An error occurred while communicating with eCourts");
      fetchCaptcha();
    } finally {
      setIsLoading(false);
    }
  };

  const sampleCnrs = [
    {
      cnr: "DLST010047302024",
      label: "Commercial Suit (Saket)",
      case: "PNB vs Sunil Kumar",
    },
    {
      cnr: "DLND020000602007",
      label: "Criminal Case (Patiala House)",
      case: "State vs Accused",
    },
  ];

  return (
    <div className="space-y-4">
      {/* Sample CNR Quick Selectors */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
          Verified Test Cases:
        </span>
        {sampleCnrs.map((item) => (
          <button
            key={item.cnr}
            type="button"
            onClick={() => {
              setCnr(item.cnr);
              setError(null);
            }}
            className={`text-xs px-2.5 py-1 rounded-md border transition-all cursor-pointer ${
              cnr === item.cnr
                ? "bg-zinc-900 text-white border-zinc-900 dark:bg-zinc-100 dark:text-zinc-900 dark:border-zinc-100 font-medium shadow-xs"
                : "bg-zinc-50 dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800"
            }`}
          >
            <span className="font-mono">{item.cnr}</span> ({item.label})
          </button>
        ))}
      </div>

      <form onSubmit={handleSearch} className="space-y-4">
        {/* CNR Input */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-600 dark:text-zinc-400 mb-1.5">
            16-Digit CNR Number <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <Input
              type="text"
              value={cnr}
              onChange={(e) => setCnr(e.target.value.toUpperCase())}
              placeholder="e.g. DLST010047302024"
              maxLength={16}
              className="h-11 font-mono text-base tracking-wider uppercase pr-20"
              required
            />
            <div className="absolute right-3 top-2.5 flex items-center space-x-1">
              <Badge
                variant={cnr.length === 16 ? "success" : "secondary"}
                className="text-[10px] font-mono"
              >
                {cnr.length}/16
              </Badge>
            </div>
          </div>
          <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">
            Format: State (2) + District (2) + Complex (2) + Case Sequence (6) + Year (4)
          </p>
        </div>

        {/* Captcha Section */}
        <div className="p-3.5 rounded-lg border border-zinc-200/80 bg-zinc-50/60 dark:border-zinc-800 dark:bg-zinc-900/40 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold text-zinc-700 dark:text-zinc-300">
                Portal Security Verification
              </span>
              <Badge variant="success" className="text-[10px] space-x-1 py-0">
                <Sparkles className="h-2.5 w-2.5" />
                <span>Offline ONNX OCR Active</span>
              </Badge>
            </div>
            <div className="flex items-center space-x-1">
              {captchaData?.audio_url && (
                <button
                  type="button"
                  onClick={handlePlayAudio}
                  disabled={audioPlaying}
                  className="p-1 text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 rounded cursor-pointer"
                  title="Listen to Captcha Audio"
                >
                  <Volume2 className={`h-4 w-4 ${audioPlaying ? "animate-pulse text-indigo-500" : ""}`} />
                </button>
              )}
              <button
                type="button"
                onClick={fetchCaptcha}
                disabled={captchaLoading}
                className="p-1 text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 rounded cursor-pointer"
                title="Refresh Captcha"
              >
                <RefreshCw className={`h-4 w-4 ${captchaLoading ? "animate-spin" : ""}`} />
              </button>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3">
            {/* Captcha Image Display */}
            <div className="h-10 w-36 bg-white dark:bg-zinc-950 rounded border border-zinc-300 dark:border-zinc-700 flex items-center justify-center overflow-hidden shadow-xs shrink-0">
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

            {/* Captcha Input */}
            <div className="w-full relative">
              <Input
                type="text"
                value={captchaInput}
                onChange={(e) => setCaptchaInput(e.target.value)}
                placeholder="Enter CAPTCHA code"
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

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={isLoading || cnr.length !== 16}
          className="w-full h-11 text-sm font-semibold tracking-wide space-x-2 shadow-sm"
        >
          {isLoading ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Querying eCourts Gateway & Synchronizing Token...</span>
            </>
          ) : (
            <>
              <Search className="h-4 w-4" />
              <span>Fetch eCourts Intelligence</span>
            </>
          )}
        </Button>
      </form>
    </div>
  );
};
