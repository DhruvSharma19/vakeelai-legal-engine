import React, { useState } from "react";
import {
  FileText,
  Users,
  Calendar,
  Clock,
  Shield,
  Download,
  ExternalLink,
  ArrowRight,
  Copy,
  Check,
  CheckCircle2,
  AlertCircle,
  FileCheck2,
  Scale,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "./ui/dialog";
import { CaseRecord, OrderRecord } from "../types";

interface CaseViewProps {
  caseData: CaseRecord;
  onPrefillDraft: (data: CaseRecord) => void;
}

export const CaseView: React.FC<CaseViewProps> = ({ caseData, onPrefillDraft }) => {
  const [activeSubTab, setActiveSubTab] = useState("overview");
  const [selectedOrder, setSelectedOrder] = useState<OrderRecord | null>(null);
  const [copiedJson, setCopiedJson] = useState(false);

  const containerVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.35, staggerChildren: 0.07 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 },
  };

  const isDecreedOrDisposed =
    caseData.case_status?.case_status?.toLowerCase().includes("disposed") ||
    caseData.case_status?.nature_of_disposal?.toLowerCase().includes("decreed") ||
    caseData.case_status?.case_status?.toLowerCase().includes("decreed");

  const copyJsonToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(caseData, null, 2));
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Primary Hero Header */}
      <motion.div variants={itemVariants}>
        <Card className="border-l-4 border-l-zinc-900 dark:border-l-zinc-100 shadow-md">
          <CardHeader className="pb-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="outline" className="font-mono text-xs px-2 py-0.5">
                    CNR: {caseData.cnr}
                  </Badge>
                  <Badge
                    variant={isDecreedOrDisposed ? "success" : "warning"}
                    className="text-xs"
                  >
                    {caseData.case_status?.case_status || "Registered"}
                  </Badge>
                  {caseData.source && (
                    <Badge variant="secondary" className="text-[10px]">
                      {caseData.source === "live_ecourts" ? "Verified Live Gateway" : "Verified Snapshot"}
                    </Badge>
                  )}
                </div>
                <h2 className="text-xl sm:text-2xl font-bold tracking-tight mt-2 text-zinc-900 dark:text-zinc-50">
                  {caseData.petitioners?.[0]?.name || "Petitioner"}
                  <span className="text-zinc-400 font-normal px-2">vs</span>
                  {caseData.respondents?.[0]?.name || "Respondent"}
                </h2>
                <p className="text-xs sm:text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                  {caseData.court_establishment || "District Court Complex"} •{" "}
                  {caseData.case_details?.case_type || "Civil / Commercial Suit"}
                </p>
              </div>

              {/* Prefill Action Button */}
              <div className="flex items-center space-x-2 shrink-0">
                <Button
                  onClick={() => onPrefillDraft(caseData)}
                  className="space-x-1.5 shadow-sm text-xs sm:text-sm bg-indigo-600 hover:bg-indigo-700 text-white dark:bg-indigo-600 dark:hover:bg-indigo-700"
                >
                  <FileCheck2 className="h-4 w-4" />
                  <span>Draft Legal Pleading</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          </CardHeader>

          {/* Quick Metrics Bar */}
          <CardContent className="pt-2">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 rounded-lg bg-zinc-50 dark:bg-zinc-900/60 border border-zinc-200/60 dark:border-zinc-800 text-xs">
              <div>
                <span className="text-zinc-500 dark:text-zinc-400 block text-[11px]">
                  Filing Number
                </span>
                <span className="font-mono font-medium text-zinc-900 dark:text-zinc-100">
                  {caseData.case_details?.filing_number || "N/A"}
                </span>
              </div>
              <div>
                <span className="text-zinc-500 dark:text-zinc-400 block text-[11px]">
                  Filing Date
                </span>
                <span className="font-medium text-zinc-900 dark:text-zinc-100">
                  {caseData.case_details?.filing_date || "N/A"}
                </span>
              </div>
              <div>
                <span className="text-zinc-500 dark:text-zinc-400 block text-[11px]">
                  Registration Date
                </span>
                <span className="font-medium text-zinc-900 dark:text-zinc-100">
                  {caseData.case_details?.registration_date || "N/A"}
                </span>
              </div>
              <div>
                <span className="text-zinc-500 dark:text-zinc-400 block text-[11px]">
                  Decision / Next Date
                </span>
                <span className="font-medium text-emerald-600 dark:text-emerald-400">
                  {caseData.case_status?.decision_date ||
                    caseData.case_status?.next_hearing_date ||
                    "Disposed"}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Sub-Tabs Navigation */}
      <Tabs value={activeSubTab} onValueChange={setActiveSubTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="space-x-1.5 text-xs sm:text-sm">
            <Users className="h-3.5 w-3.5" />
            <span>Parties & Acts</span>
          </TabsTrigger>
          <TabsTrigger value="history" className="space-x-1.5 text-xs sm:text-sm">
            <Calendar className="h-3.5 w-3.5" />
            <span>Hearings ({caseData.history?.length || 0})</span>
          </TabsTrigger>
          <TabsTrigger value="orders" className="space-x-1.5 text-xs sm:text-sm">
            <FileText className="h-3.5 w-3.5" />
            <span>Orders ({caseData.orders?.length || 0})</span>
          </TabsTrigger>
          <TabsTrigger value="json" className="space-x-1.5 text-xs sm:text-sm font-mono">
            <span>JSON</span>
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Parties & Acts Overview */}
        <TabsContent value="overview" className="space-y-4 mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Petitioners Card */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2 text-zinc-900 dark:text-zinc-100">
                  <span className="h-2 w-2 rounded-full bg-blue-500" />
                  <span>Petitioner / Plaintiff</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {caseData.petitioners?.map((party, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg border border-zinc-200/80 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/40"
                  >
                    <div className="font-semibold text-sm text-zinc-900 dark:text-zinc-100">
                      {idx + 1}. {party.name}
                    </div>
                    {party.advocate && (
                      <div className="text-xs text-zinc-600 dark:text-zinc-400 mt-1 flex items-center space-x-1">
                        <span className="font-medium">Advocate:</span>
                        <span className="text-indigo-600 dark:text-indigo-400">
                          {party.advocate}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Respondents Card */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold flex items-center space-x-2 text-zinc-900 dark:text-zinc-100">
                  <span className="h-2 w-2 rounded-full bg-amber-500" />
                  <span>Respondent / Defendant</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {caseData.respondents?.map((party, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg border border-zinc-200/80 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/40"
                  >
                    <div className="font-semibold text-sm text-zinc-900 dark:text-zinc-100">
                      {idx + 1}. {party.name}
                    </div>
                    {party.advocate && (
                      <div className="text-xs text-zinc-600 dark:text-zinc-400 mt-1 flex items-center space-x-1">
                        <span className="font-medium">Advocate:</span>
                        <span className="text-indigo-600 dark:text-indigo-400">
                          {party.advocate}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Acts and Sections */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold flex items-center space-x-2">
                <Shield className="h-4 w-4 text-zinc-600 dark:text-zinc-400" />
                <span>Statutory Acts & Sections Invoked</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {caseData.acts && caseData.acts.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {caseData.acts.map((act, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2.5 rounded-lg border border-zinc-200/60 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/40 text-xs"
                    >
                      <span className="font-medium text-zinc-800 dark:text-zinc-200">
                        {act.under_act}
                      </span>
                      <Badge variant="outline" className="font-mono text-[11px]">
                        Section: {act.under_section || "General"}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-zinc-500">No specific acts recorded in summary registry.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Chronological Hearing History */}
        <TabsContent value="history" className="mt-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold">
                Chronological Hearing Proceedings
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/80 text-zinc-600 dark:text-zinc-400 font-semibold">
                      <th className="py-3 px-4">Hearing Date</th>
                      <th className="py-3 px-4">Purpose of Hearing</th>
                      <th className="py-3 px-4">Business Recorded</th>
                      <th className="py-3 px-4">Next Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                    {caseData.history?.map((h, idx) => (
                      <tr
                        key={idx}
                        className="hover:bg-zinc-50/80 dark:hover:bg-zinc-900/40 transition-colors"
                      >
                        <td className="py-3 px-4 font-mono font-medium whitespace-nowrap text-zinc-900 dark:text-zinc-100">
                          {h.hearing_date}
                        </td>
                        <td className="py-3 px-4 text-zinc-700 dark:text-zinc-300">
                          <Badge variant="secondary" className="font-normal text-[11px]">
                            {h.purpose_of_hearing}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-zinc-600 dark:text-zinc-400 font-mono text-[11px]">
                          {h.business_recorded || "Recorded"}
                        </td>
                        <td className="py-3 px-4 font-mono text-zinc-500 whitespace-nowrap">
                          {h.next_hearing_date || "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: Orders and Judgments */}
        <TabsContent value="orders" className="mt-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold">
                Court Orders, Injunctions & Judgments
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {caseData.orders && caseData.orders.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {caseData.orders.map((ord, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl border border-zinc-200 dark:border-zinc-800 hover:border-zinc-400 dark:hover:border-zinc-600 bg-white dark:bg-zinc-900/60 shadow-2xs transition-all flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex items-center justify-between mb-1.5">
                          <Badge variant="outline" className="font-mono text-xs">
                            Order #{ord.order_number}
                          </Badge>
                          <span className="text-xs font-mono text-zinc-500">
                            {ord.order_date}
                          </span>
                        </div>
                        <p className="text-xs text-zinc-600 dark:text-zinc-400 line-clamp-2">
                          {ord.order_details || "Daily Order / Proceedings"}
                        </p>
                      </div>

                      <div className="flex items-center space-x-2 mt-3 pt-2 border-t border-zinc-100 dark:border-zinc-800">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => setSelectedOrder(ord)}
                          className="w-full text-xs h-8 space-x-1"
                        >
                          <FileText className="h-3.5 w-3.5" />
                          <span>View Order Record</span>
                        </Button>
                        {ord.pdf_url && (
                          <a
                            href={ord.pdf_url}
                            target="_blank"
                            rel="noreferrer"
                            className="p-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-300 transition-colors"
                            title="Direct PDF Download"
                          >
                            <Download className="h-4 w-4" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-zinc-500">No official order records attached.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 4: Clean Structured JSON */}
        <TabsContent value="json" className="mt-4">
          <Card>
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-semibold font-mono">
                Structured Case JSON Payload
              </CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={copyJsonToClipboard}
                className="text-xs space-x-1 h-8"
              >
                {copiedJson ? (
                  <>
                    <Check className="h-3.5 w-3.5 text-emerald-600" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3.5 w-3.5" />
                    <span>Copy JSON</span>
                  </>
                )}
              </Button>
            </CardHeader>
            <CardContent>
              <pre className="p-4 rounded-lg bg-zinc-950 text-zinc-100 font-mono text-xs overflow-x-auto max-h-96 leading-relaxed border border-zinc-800">
                {JSON.stringify(caseData, null, 2)}
              </pre>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Order Modal Viewer */}
      <Dialog open={!!selectedOrder} onOpenChange={() => setSelectedOrder(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Scale className="h-5 w-5 text-zinc-900 dark:text-zinc-100" />
              <span>Court Order #{selectedOrder?.order_number}</span>
            </DialogTitle>
            <DialogDescription>
              Recorded on {selectedOrder?.order_date} • {caseData.court_establishment}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 my-2 text-xs sm:text-sm">
            <div className="p-4 rounded-lg bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 font-mono text-xs leading-relaxed">
              <p className="text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap">
                {selectedOrder?.order_details ||
                  "Detailed proceeding minutes and judicial order uploaded to court records."}
              </p>
            </div>

            {selectedOrder?.display_pdf_args && (
              <div className="p-2.5 rounded-md bg-zinc-100 dark:bg-zinc-800 text-[11px] font-mono text-zinc-600 dark:text-zinc-400">
                eCourts PDF Hash: {selectedOrder.display_pdf_args}
              </div>
            )}
          </div>

          <div className="flex items-center justify-end space-x-2 pt-2 border-t border-zinc-100 dark:border-zinc-800">
            {selectedOrder?.pdf_url && (
              <Button asChild variant="default" size="sm" className="space-x-1.5 text-xs">
                <a href={selectedOrder.pdf_url} target="_blank" rel="noreferrer">
                  <Download className="h-3.5 w-3.5" />
                  <span>Download Court PDF</span>
                </a>
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </motion.div>
  );
};
