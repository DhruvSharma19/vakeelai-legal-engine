import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, X, Search, Hash, Scale, Code2 } from "lucide-react";
import { Navbar } from "./components/Navbar";
import { CNRSearch } from "./components/CNRSearch";
import { CaseNumberSearch } from "./components/CaseNumberSearch";
import { CaseView } from "./components/CaseView";
import { DraftingStudio } from "./components/DraftingStudio";
import { ArchitectureView } from "./components/ArchitectureView";
import { Card, CardHeader, CardTitle, CardContent } from "./components/ui/card";
import { CaseRecord } from "./types";

export function App() {
  const [activeTab, setActiveTab] = useState<string>("scraper");
  const [searchMethod, setSearchMethod] = useState<"cnr" | "case_number">("cnr");
  const [currentCase, setCurrentCase] = useState<CaseRecord | null>(null);
  const [prefillCase, setPrefillCase] = useState<CaseRecord | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleCaseFound = (data: CaseRecord) => {
    setCurrentCase(data);
    setError(null);
  };

  const handlePrefillDraft = (data: CaseRecord) => {
    setPrefillCase(data);
    setActiveTab("drafting");
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50 flex flex-col font-sans transition-colors duration-200">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Global Error Banner */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="p-4 rounded-xl border border-red-200 bg-red-50 dark:border-red-900/50 dark:bg-red-950/40 text-red-800 dark:text-red-300 text-xs sm:text-sm flex items-start justify-between shadow-xs"
            >
              <div className="flex items-start space-x-2.5">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-red-600 dark:text-red-400" />
                <div className="leading-relaxed">{error}</div>
              </div>
              <button
                onClick={() => setError(null)}
                className="p-1 hover:bg-red-100 dark:hover:bg-red-900/40 rounded text-red-500 cursor-pointer ml-3"
              >
                <X className="h-4 w-4" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Tab Content with Framer Motion Page Transition */}
        <AnimatePresence mode="wait">
          {activeTab === "scraper" && (
            <motion.div
              key="scraper"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25, ease: "easeOut" }}
              className="space-y-6"
            >
              {/* Search Card Container */}
              <Card className="shadow-xs border-zinc-200/80 dark:border-zinc-800">
                <CardHeader className="pb-3 border-b border-zinc-100 dark:border-zinc-800">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <CardTitle className="text-base font-bold text-zinc-900 dark:text-zinc-50 flex items-center space-x-2">
                        <span>eCourts District Court Registry Scraper</span>
                      </CardTitle>
                      <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
                        Programmatic session management, rotating AST token bypass, and offline neural OCR.
                      </p>
                    </div>

                    {/* Search Method Switcher Pills */}
                    <div className="flex items-center space-x-1 bg-zinc-100 dark:bg-zinc-900 p-1 rounded-lg border border-zinc-200 dark:border-zinc-800">
                      <button
                        onClick={() => setSearchMethod("cnr")}
                        className={`text-xs px-3 py-1.5 rounded-md font-medium transition-all cursor-pointer flex items-center space-x-1.5 ${
                          searchMethod === "cnr"
                            ? "bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-xs"
                            : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900"
                        }`}
                      >
                        <Hash className="h-3.5 w-3.5" />
                        <span>CNR Search</span>
                      </button>

                      <button
                        onClick={() => setSearchMethod("case_number")}
                        className={`text-xs px-3 py-1.5 rounded-md font-medium transition-all cursor-pointer flex items-center space-x-1.5 ${
                          searchMethod === "case_number"
                            ? "bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-xs"
                            : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900"
                        }`}
                      >
                        <Search className="h-3.5 w-3.5" />
                        <span>Case Number Search</span>
                      </button>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="pt-4">
                  {searchMethod === "cnr" ? (
                    <CNRSearch
                      onCaseFound={handleCaseFound}
                      isLoading={isLoading}
                      setIsLoading={setIsLoading}
                      setError={setError}
                    />
                  ) : (
                    <CaseNumberSearch
                      onCaseFound={handleCaseFound}
                      isLoading={isLoading}
                      setIsLoading={setIsLoading}
                      setError={setError}
                    />
                  )}
                </CardContent>
              </Card>

              {/* Render Retrieved Case View */}
              {currentCase && (
                <CaseView
                  caseData={currentCase}
                  onPrefillDraft={handlePrefillDraft}
                />
              )}
            </motion.div>
          )}

          {activeTab === "drafting" && (
            <motion.div
              key="drafting"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25, ease: "easeOut" }}
            >
              <DraftingStudio
                prefillCase={prefillCase}
                onClearPrefill={() => setPrefillCase(null)}
              />
            </motion.div>
          )}

          {activeTab === "architecture" && (
            <motion.div
              key="architecture"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25, ease: "easeOut" }}
            >
              <ArchitectureView />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-200/80 bg-white dark:border-zinc-800 dark:bg-zinc-950 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-zinc-500 dark:text-zinc-400 gap-3">
          <div>
            <span className="font-semibold text-zinc-800 dark:text-zinc-200">
              VakeelAI Legal Intelligence Platform
            </span>{" "}
            • Built for High-Performance Legal Operations
          </div>
          <div className="flex items-center space-x-4">
            <a
              href="https://github.com/DhruvSharma19/vakeelai-legal-engine"
              target="_blank"
              rel="noreferrer"
              className="hover:text-zinc-900 dark:hover:text-zinc-100 underline-offset-4 hover:underline"
            >
              GitHub Repository
            </a>
            <span>•</span>
            <span className="font-mono text-[11px]">MIT Licensed</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

