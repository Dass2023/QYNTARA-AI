"use client";
import React, { useEffect, useState } from 'react';
import { HoloCard } from './ui/HoloCard';
import { NeonButton } from './ui/NeonButton';
import { Activity, Cpu, Database, Server, Zap, Globe } from 'lucide-react';

export default function AnalyticsPanel({ onClose }: { onClose: () => void }) {
    const [stats, setStats] = useState<any>(null);

    useEffect(() => {
        const fetchStats = async () => { try { setStats(await (await fetch('http://localhost:8000/stats')).json()); } catch { } };
        fetchStats();
        const interval = setInterval(fetchStats, 2000);
        return () => clearInterval(interval);
    }, []);

    if (!stats) return null;

    const metrics = [
        { label: "TOTAL POLYGONS", value: stats.total_polygons.toLocaleString(), icon: Database, color: "text-cyan-400" },
        { label: "AI TOKENS", value: stats.ai_tokens.toLocaleString(), icon: Zap, color: "text-purple-400" },
        { label: "ACTIVE JOBS", value: stats.total_jobs, icon: Activity, color: "text-green-400" },
        { label: "NODES ONLINE", value: stats.active_nodes, icon: Server, color: "text-amber-400" },
    ];

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-void/90 backdrop-blur-xl p-8 animate-in fade-in duration-300">
            <HoloCard className="max-w-5xl w-full border-cyan-500/30 shadow-[0_0_100px_-20px_rgba(0,243,255,0.2)]">
                <div className="flex items-center justify-between mb-8 border-b border-white/10 pb-6">
                    <div className="flex items-center gap-4">
                        <Globe className="w-8 h-8 text-cyan-500 animate-pulse-slow" />
                        <div>
                            <h2 className="text-3xl font-display font-bold text-white tracking-widest">NEURAL ANALYTICS</h2>
                            <p className="font-mono text-xs text-cyan-500/50 tracking-[0.3em]">REAL-TIME SYSTEM TELEMETRY</p>
                        </div>
                    </div>
                    <NeonButton variant="danger" onClick={onClose} className="text-xs">CLOSE PANEL</NeonButton>
                </div>

                <div className="grid grid-cols-4 gap-6 mb-8">
                    {metrics.map((m, i) => (
                        <div key={i} className="bg-black/40 border border-white/5 p-6 rounded-lg relative overflow-hidden group hover:border-cyan-500/30 transition-colors">
                            <div className={`absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-50 transition-opacity ${m.color}`}>
                                <m.icon className="w-12 h-12" />
                            </div>
                            <div className="font-mono text-xs text-gray-500 mb-2">{m.label}</div>
                            <div className={`font-display text-3xl font-bold ${m.color}`}>{m.value}</div>
                        </div>
                    ))}
                </div>

                <div className="h-64 bg-black/40 border border-white/5 rounded-lg p-6 flex items-center justify-center relative overflow-hidden">
                    <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(68,68,68,.2)_50%,transparent_75%,transparent_100%)] bg-[length:250%_250%,100%_100%] animate-[shimmer_3s_infinite]" />
                    <div className="text-center">
                        <Cpu className="w-16 h-16 text-white/10 mx-auto mb-4" />
                        <div className="font-mono text-sm text-white/30">VISUALIZATION MODULE LOADING...</div>
                    </div>
                </div>
            </HoloCard>
        </div>
    );
}
