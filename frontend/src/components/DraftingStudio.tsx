import React, { useState, useEffect } from "react";
import {
  Sparkles,
  Download,
  Copy,
  Check,
  Plus,
  Trash2,
  BookOpen,
  Scale,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./ui/tabs";
import { formatINR } from "../lib/utils";
import { DraftInput, DraftOutput, CaseRecord } from "../types";

interface DraftingStudioProps {
  prefillCase?: CaseRecord | null;
  onClearPrefill?: () => void;
}

export const DraftingStudio: React.FC<DraftingStudioProps> = ({
  prefillCase,
  onClearPrefill,
}) => {
  const [templateId, setTemplateId] = useState("commercial_suit");
  const [courtName, setCourtName] = useState(
    "IN THE COURT OF THE DISTRICT JUDGE (COMMERCIAL COURT) AT SAKET, NEW DELHI"
  );
  const [suitNumber, setSuitNumber] = useState("COMMERCIAL SUIT NO. 233 OF 2024");
  const [cnrNumber, setCnrNumber] = useState("DLST010047302024");
  const [plaintiffName, setPlaintiffName] = useState("Punjab National Bank");
  const [plaintiffDetails, setPlaintiffDetails] = useState(
    "A body corporate constituted under the Banking Companies (Acquisition and Transfer of Undertakings) Act, 1970, having its branch office at Saket, New Delhi"
  );
  const [defendantName, setDefendantName] = useState("Sunil Kumar");
  const [defendantDetails, setDefendantDetails] = useState(
    "Resident of Flat No. 402, Block C, Saket Residency, South District, New Delhi - 110017"
  );
  const [advocateName, setAdvocateName] = useState("A. K. Sharma & Associates");
  const [advocateEnrollment, setAdvocateEnrollment] = useState("D/1452/2012");
  const [advocateChamber, setAdvocateChamber] = useState(
    "Chamber No. 342, Lawyers Chambers Block, Saket District Court, New Delhi"
  );
  const [claimAmount, setClaimAmount] = useState<number>(1850000);
  const [facts, setFacts] = useState<string[]>([
    "The Plaintiff extended a commercial credit facility to the Defendant upon mutual execution of loan and hypothecation agreements.",
    "The Defendant committed chronic payment defaults and failed to regularize the debt despite repeated verbal and written reminders.",
    "The Plaintiff issued a formal demand notice calling upon the Defendant to liquidate the outstanding liability within 15 days.",
    "Mandatory pre-institution mediation under Section 12A of the Commercial Courts Act, 2015 was initiated, which culminated in a Non-Starter Report due to Defendant's non-appearance.",
  ]);
  const [prayers, setPrayers] = useState<string[]>([
    "Pass a decree for recovery of the principal claim together with pendente lite and future interest at 18% per annum until actual realization.",
    "Award full costs of the commercial suit in favor of the Plaintiff.",
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [generatedDraft, setGeneratedDraft] = useState<DraftOutput | null>(null);
  const [activeOutputTab, setActiveOutputTab] = useState("preview");
  const [copiedText, setCopiedText] = useState(false);

  // Cross-Task Synergy Bridge via backend API
  useEffect(() => {
    if (prefillCase) {
      fetch("/api/drafting/prefill-from-case", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(prefillCase),
      })
        .then((res) => (res.ok ? res.json() : null))
        .then((draftInput: DraftInput | null) => {
          if (draftInput) {
            setCourtName(draftInput.court_name);
            if (draftInput.case_type_number_year) setSuitNumber(draftInput.case_type_number_year);
            if (draftInput.cnr_number) setCnrNumber(draftInput.cnr_number);
            if (draftInput.plaintiffs?.[0]) {
              setPlaintiffName(draftInput.plaintiffs[0].name);
              setPlaintiffDetails(draftInput.plaintiffs[0].address || "");
            }
            if (draftInput.defendants?.[0]) {
              setDefendantName(draftInput.defendants[0].name);
              setDefendantDetails(draftInput.defendants[0].address || "");
            }
            if (draftInput.advocate) {
              setAdvocateName(draftInput.advocate.name);
              setAdvocateEnrollment(draftInput.advocate.bar_council_number || "");
            }
            if (draftInput.total_claim_amount) {
              setClaimAmount(draftInput.total_claim_amount);
            }
          }
        })
        .catch((err) => console.warn("Prefill bridge error:", err));
    }
  }, [prefillCase]);

  const templates: { id: string; name: string; tag: string; law: string }[] = [
    {
      id: "commercial_suit",
      name: "Commercial Plaint",
      tag: "Civil Suit",
      law: "Order VII CPC & Commercial Courts Act 2015",
    },
    {
      id: "legal_notice",
      name: "Legal Demand Notice",
      tag: "Pre-Litigation",
      law: "Section 80 CPC / Contract Act",
    },
    {
      id: "bail_application",
      name: "Regular Bail Application",
      tag: "Criminal Pleading",
      law: "Section 439 CrPC / Section 483 BNSS",
    },
    {
      id: "consumer_complaint",
      name: "Consumer Complaint",
      tag: "Tribunal",
      law: "Section 35 Consumer Protection Act 2019",
    },
    {
      id: "general_affidavit",
      name: "Evidentiary Affidavit",
      tag: "Verification",
      law: "Order XIX Rule 1 CPC / Notaries Act",
    },
  ];

  const handleAddFact = () => setFacts([...facts, ""]);
  const handleRemoveFact = (index: number) => {
    setFacts(facts.filter((_, i) => i !== index));
  };
  const handleFactChange = (index: number, val: string) => {
    const updated = [...facts];
    updated[index] = val;
    setFacts(updated);
  };

  const handleAddPrayer = () => setPrayers([...prayers, ""]);
  const handleRemovePrayer = (index: number) => {
    setPrayers(prayers.filter((_, i) => i !== index));
  };
  const handlePrayerChange = (index: number, val: string) => {
    const updated = [...prayers];
    updated[index] = val;
    setPrayers(updated);
  };

  const buildPayload = (): DraftInput => {
    return {
      template_id: templateId,
      court_name: courtName,
      jurisdiction_title: "COMMERCIAL CIVIL JURISDICTION",
      case_type_number_year: suitNumber,
      cnr_number: cnrNumber || undefined,
      plaintiffs: [
        {
          name: plaintiffName,
          address: plaintiffDetails,
          is_corporate: true,
        },
      ],
      defendants: [
        {
          name: defendantName,
          address: defendantDetails,
        },
      ],
      advocate: {
        name: advocateName,
        bar_council_number: advocateEnrollment,
        office_address: advocateChamber,
      },
      total_claim_amount: claimAmount,
      facts: facts
        .filter((f) => f.trim().length > 0)
        .map((f, i) => ({ narrative: f, annexure_label: `ANNEXURE P-${i + 1}` })),
      prayers: prayers
        .filter((p) => p.trim().length > 0)
        .map((p, i) => ({
          clause_letter: String.fromCharCode(97 + i),
          relief_text: p,
        })),
      sec_12a_compliance: true,
      place: "New Delhi",
    };
  };

  const handleGenerate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsLoading(true);

    try {
      const payload = buildPayload();
      const res = await fetch("/api/drafting/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Failed to generate legal draft template");
      const data: DraftOutput = await res.json();
      setGeneratedDraft(data);
      setActiveOutputTab("preview");
    } catch (err: any) {
      alert("Drafting Error: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadDocx = async () => {
    try {
      const payload = buildPayload();
      const res = await fetch("/api/drafting/export/docx", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Word export failed");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${templateId}_legal_draft.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert("Download error: " + err.message);
    }
  };

  const handleCopyMarkdown = () => {
    if (!generatedDraft) return;
    navigator.clipboard.writeText(generatedDraft.markdown);
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Zero LLM / Zero External API Notice */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-2xs gap-3">
        <div className="flex items-center space-x-2.5">
          <div className="h-8 w-8 rounded-lg bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-900 dark:text-zinc-100">
            <Scale className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-xs sm:text-sm text-zinc-900 dark:text-zinc-100">
                Pure-Python Legal Drafting Engine
              </span>
              <Badge variant="success" className="text-[10px] py-0 font-mono">
                100% Deterministic (Zero-LLM)
              </Badge>
            </div>
            <p className="text-[11px] text-zinc-500 dark:text-zinc-400">
              Compliant with the Code of Civil Procedure (CPC), Commercial Courts Act 2015, and BNSS 2023.
            </p>
          </div>
        </div>

        {prefillCase && (
          <div className="flex items-center space-x-2 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 px-2.5 py-1 rounded-lg text-xs text-indigo-700 dark:text-indigo-300">
            <span>Pre-filled from: {prefillCase.cnr}</span>
            <button
              onClick={onClearPrefill}
              className="text-indigo-500 hover:text-indigo-900 dark:hover:text-white font-bold ml-1 cursor-pointer"
            >
              ×
            </button>
          </div>
        )}
      </div>

      {/* Template Type Selector Cards */}
      <div>
        <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 uppercase tracking-wider mb-2">
          Select Pleading or Document Template
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
          {templates.map((tpl) => {
            const isSelected = templateId === tpl.id;
            return (
              <button
                key={tpl.id}
                type="button"
                onClick={() => setTemplateId(tpl.id)}
                className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                  isSelected
                    ? "border-zinc-900 bg-zinc-900 text-white dark:border-zinc-100 dark:bg-zinc-100 dark:text-zinc-900 shadow-sm"
                    : "border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 hover:border-zinc-300 dark:hover:border-zinc-700"
                }`}
              >
                <div>
                  <span className={`text-[10px] font-mono block ${isSelected ? "text-zinc-300 dark:text-zinc-600" : "text-zinc-400"}`}>
                    {tpl.tag}
                  </span>
                  <span className="font-semibold text-xs sm:text-sm mt-0.5 block leading-snug">
                    {tpl.name}
                  </span>
                </div>
                <span className={`text-[10px] mt-2 block line-clamp-1 ${isSelected ? "text-zinc-300 dark:text-zinc-600" : "text-zinc-500"}`}>
                  {tpl.law}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Drafting Form Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Form Inputs (Left Column) */}
        <div className="lg:col-span-5 space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold flex items-center justify-between">
                <span>Pleading Parameters</span>
                <span className="text-xs text-zinc-400 font-normal">Core Metadata</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
                  Court / Forum Header
                </label>
                <Input
                  type="text"
                  value={courtName}
                  onChange={(e) => setCourtName(e.target.value)}
                  className="text-xs uppercase"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
                  Suit / Case Number
                </label>
                <Input
                  type="text"
                  value={suitNumber}
                  onChange={(e) => setSuitNumber(e.target.value)}
                  className="text-xs font-mono"
                />
              </div>

              {/* Parties */}
              <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800 space-y-2">
                <div>
                  <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
                    Plaintiff / Petitioner
                  </label>
                  <Input
                    type="text"
                    value={plaintiffName}
                    onChange={(e) => setPlaintiffName(e.target.value)}
                    className="text-xs font-medium"
                  />
                  <textarea
                    rows={2}
                    value={plaintiffDetails}
                    onChange={(e) => setPlaintiffDetails(e.target.value)}
                    placeholder="Plaintiff description, registered office, or age/residence..."
                    className="w-full text-xs rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-2 mt-1 focus:outline-none focus:ring-1 focus:ring-zinc-900"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
                    Defendant / Respondent
                  </label>
                  <Input
                    type="text"
                    value={defendantName}
                    onChange={(e) => setDefendantName(e.target.value)}
                    className="text-xs font-medium"
                  />
                  <textarea
                    rows={2}
                    value={defendantDetails}
                    onChange={(e) => setDefendantDetails(e.target.value)}
                    placeholder="Defendant address, branch, or particulars..."
                    className="w-full text-xs rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-2 mt-1 focus:outline-none focus:ring-1 focus:ring-zinc-900"
                  />
                </div>
              </div>

              {/* Pecuniary Valuation with Indian Words */}
              <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800">
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400">
                    Pecuniary Valuation / Claim Amount
                  </label>
                  <span className="text-xs font-mono font-medium text-emerald-600 dark:text-emerald-400">
                    {formatINR(claimAmount)}
                  </span>
                </div>
                <Input
                  type="number"
                  value={claimAmount}
                  onChange={(e) => setClaimAmount(parseFloat(e.target.value) || 0)}
                  className="text-xs font-mono"
                />
              </div>

              {/* Advocate Details */}
              <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800 space-y-2">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
                      Advocate Name
                    </label>
                    <Input
                      type="text"
                      value={advocateName}
                      onChange={(e) => setAdvocateName(e.target.value)}
                      className="text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
                      Bar Enrollment
                    </label>
                    <Input
                      type="text"
                      value={advocateEnrollment}
                      onChange={(e) => setAdvocateEnrollment(e.target.value)}
                      className="text-xs font-mono"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Facts & Prayers Card */}
          <Card>
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-semibold">Factual Averments</CardTitle>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddFact}
                className="text-xs h-7 space-x-1"
              >
                <Plus className="h-3 w-3" />
                <span>Add Fact</span>
              </Button>
            </CardHeader>
            <CardContent className="space-y-2.5">
              {facts.map((fact, idx) => (
                <div key={idx} className="flex items-start space-x-2">
                  <span className="text-xs font-mono text-zinc-400 mt-2">{idx + 1}.</span>
                  <textarea
                    rows={2}
                    value={fact}
                    onChange={(e) => handleFactChange(idx, e.target.value)}
                    className="w-full text-xs rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-2 focus:outline-none focus:ring-1 focus:ring-zinc-900"
                  />
                  {facts.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveFact(idx)}
                      className="p-1.5 text-zinc-400 hover:text-red-500 rounded cursor-pointer mt-1"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Prayers Card */}
          <Card>
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-semibold">Prayers / Relief Sought</CardTitle>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddPrayer}
                className="text-xs h-7 space-x-1"
              >
                <Plus className="h-3 w-3" />
                <span>Add Relief</span>
              </Button>
            </CardHeader>
            <CardContent className="space-y-2.5">
              {prayers.map((prayer, idx) => (
                <div key={idx} className="flex items-start space-x-2">
                  <span className="text-xs font-mono text-zinc-400 mt-2">({String.fromCharCode(97 + idx)})</span>
                  <textarea
                    rows={2}
                    value={prayer}
                    onChange={(e) => handlePrayerChange(idx, e.target.value)}
                    className="w-full text-xs rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-2 focus:outline-none focus:ring-1 focus:ring-zinc-900"
                  />
                  {prayers.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemovePrayer(idx)}
                      className="p-1.5 text-zinc-400 hover:text-red-500 rounded cursor-pointer mt-1"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            disabled={isLoading}
            className="w-full h-11 text-sm font-semibold tracking-wide space-x-2 shadow-sm bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
          >
            {isLoading ? (
              <span>Compiling Pleading with Order VII CPC Rules...</span>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                <span>Assemble Court Pleading</span>
              </>
            )}
          </Button>
        </div>

        {/* Output Preview (Right Column) */}
        <div className="lg:col-span-7 space-y-4">
          <Card className="min-h-[620px] flex flex-col justify-between shadow-md">
            <CardHeader className="pb-3 border-b border-zinc-100 dark:border-zinc-800">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <CardTitle className="text-base font-bold text-zinc-900 dark:text-zinc-100">
                    {generatedDraft ? generatedDraft.title : "Drafting Studio Preview"}
                  </CardTitle>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400">
                    {generatedDraft
                      ? `${generatedDraft.template_name} • Standard 1.5-inch Court Margins`
                      : "Configure parameters on the left and assemble pleading to render."}
                  </p>
                </div>

                {generatedDraft && (
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCopyMarkdown}
                      className="text-xs h-8 space-x-1"
                    >
                      {copiedText ? (
                        <>
                          <Check className="h-3 w-3 text-emerald-600" />
                          <span>Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-3 w-3" />
                          <span>Copy</span>
                        </>
                      )}
                    </Button>

                    <Button
                      variant="default"
                      size="sm"
                      onClick={handleDownloadDocx}
                      className="text-xs h-8 space-x-1.5 bg-indigo-600 hover:bg-indigo-700 text-white dark:bg-indigo-600"
                    >
                      <Download className="h-3.5 w-3.5" />
                      <span>Download .docx</span>
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>

            <CardContent className="pt-4 flex-1">
              {generatedDraft ? (
                <div className="space-y-4">
                  <Tabs value={activeOutputTab} onValueChange={setActiveOutputTab}>
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="preview" className="text-xs">
                        Document View
                      </TabsTrigger>
                      <TabsTrigger value="markdown" className="text-xs">
                        Markdown Source
                      </TabsTrigger>
                      <TabsTrigger value="json" className="text-xs font-mono">
                        Schema JSON
                      </TabsTrigger>
                    </TabsList>

                    <TabsContent value="preview" className="mt-3">
                      <div className="p-6 sm:p-8 rounded-lg bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 font-serif text-xs sm:text-sm leading-relaxed text-zinc-900 dark:text-zinc-100 max-h-[550px] overflow-y-auto whitespace-pre-wrap select-text">
                        {generatedDraft.plain_text}
                      </div>
                    </TabsContent>

                    <TabsContent value="markdown" className="mt-3">
                      <pre className="p-4 rounded-lg bg-zinc-950 text-zinc-100 font-mono text-xs overflow-x-auto max-h-[550px] leading-relaxed border border-zinc-800">
                        {generatedDraft.markdown}
                      </pre>
                    </TabsContent>

                    <TabsContent value="json" className="mt-3">
                      <pre className="p-4 rounded-lg bg-zinc-950 text-emerald-400 font-mono text-xs overflow-x-auto max-h-[550px] leading-relaxed border border-zinc-800">
                        {JSON.stringify(generatedDraft.structured_sections, null, 2)}
                      </pre>
                    </TabsContent>
                  </Tabs>
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center p-8 text-zinc-400 space-y-3">
                  <BookOpen className="h-12 w-12 stroke-[1.2] text-zinc-300 dark:text-zinc-700" />
                  <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                    No Pleading Assembled Yet
                  </p>
                  <p className="text-xs max-w-sm text-zinc-400 dark:text-zinc-500">
                    Select a template, customize factual averments and relief, then click &ldquo;Assemble Court Pleading&rdquo; to generate.
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleGenerate}
                    className="text-xs mt-2"
                  >
                    Generate Default Sample Plaint
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
