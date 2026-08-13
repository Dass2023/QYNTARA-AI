"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle, XCircle, AlertTriangle, RefreshCw } from "lucide-react";

interface ValidationCheck {
    name: string;
    status: "PASS" | "FAIL" | "WARN";
    count: number;
    message: string;
}

interface ValidationReport {
    score: number;
    checks: ValidationCheck[];
}

interface ValidationSyncData {
    asset_id: string;
    timestamp: number;
    industry_preset: string;
    report: ValidationReport;
}

export default function ValidationHealth({ assetId }: { assetId: string }) {
    const [data, setData] = useState<ValidationSyncData | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/v1/assets/${assetId}/validation`);
            if (res.ok) {
                const json = await res.json();
                setData(json);
            }
        } catch (e) {
            console.error("Failed to fetch validation data", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [assetId]);

    if (loading) return <div className="p-4 text-zinc-500 animate-pulse">Loading Validation Health...</div>;
    if (!data) return (
        <div className="p-6 border border-zinc-800 rounded-lg bg-zinc-900/50 text-center">
            <h3 className="text-zinc-400 mb-2">No Validation Data</h3>
            <p className="text-xs text-zinc-600 mb-4">Run "Sync to Cloud" in Maya Validation Tab.</p>
            <button onClick={fetchData} className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 rounded text-xs text-zinc-300 flex items-center gap-2 mx-auto">
                <RefreshCw size={12} /> Refresh
            </button>
        </div>
    );

    const getScoreColor = (score: number) => {
        if (score >= 90) return "text-green-500 border-green-500";
        if (score >= 70) return "text-yellow-500 border-yellow-500";
        return "text-red-500 border-red-500";
    };

    return (
        <div className="w-full bg-zinc-950 border border-zinc-800 rounded-xl overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/50">
                <div>
                    <h3 className="text-sm font-bold text-zinc-200 flex items-center gap-2">
                        <CheckCircle size={14} className="text-cyan-400" />
                        VALIDATION HEALTH
                    </h3>
                    <p className="text-xs text-zinc-500 mt-1">
                        Preset: <span className="text-cyan-400">{data.industry_preset}</span> • {new Date(data.timestamp * 1000).toLocaleTimeString()}
                    </p>
                </div>
                <div className={`relative w-12 h-12 rounded-full border-4 flex items-center justify-center font-bold text-sm ${getScoreColor(data.report.score)}`}>
                    {data.report.score}
                </div>
            </div>

            {/* Body */}
            <div className="p-4 max-h-64 overflow-y-auto space-y-2 custom-scrollbar">
                {data.report.checks.map((check, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className={`flex items-start gap-3 p-2 rounded border border-zinc-800/50 ${check.status === "FAIL" ? "bg-red-950/20" : "bg-zinc-900/30"
                            }`}
                    >
                        <div className="mt-1">
                            {check.status === "PASS" && <CheckCircle size={14} className="text-green-500/80" />}
                            {check.status === "FAIL" && <XCircle size={14} className="text-red-500/80" />}
                            {check.status === "WARN" && <AlertTriangle size={14} className="text-yellow-500/80" />}
                        </div>
                        <div className="flex-1">
                            <div className="flex justify-between">
                                <span className={`text-xs font-medium ${check.status === "FAIL" ? "text-red-400" : "text-zinc-400"}`}>
                                    {check.name}
                                </span>
                                {check.count > 0 && (
                                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">
                                        {check.count} found
                                    </span>
                                )}
                            </div>
                            {check.message && (
                                <p className="text-[10px] text-zinc-600 mt-1">{check.message}</p>
                            )}
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
