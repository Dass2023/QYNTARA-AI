
"use client";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Cpu, Wifi, Database, Globe, Hexagon, Zap, ShieldCheck } from 'lucide-react';

export default function SystemStartup({ onComplete }: { onComplete: () => void }) {
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState("INITIALIZING BIOS...");
    const [logs, setLogs] = useState<string[]>([]);

    const bootSequence = [
        { progress: 10, text: "LOADING KERNEL MODULES..." },
        { progress: 30, text: "MOUNTING VIRTUAL FILESYSTEM..." },
        { progress: 45, text: "ESTABLISHING NEURAL UPLINK..." },
        { progress: 60, text: "VERIFYING GPU CLUSTER..." },
        { progress: 80, text: "SYNCING WITH QYNTARA CLOUD..." },
        { progress: 90, text: "LOADING USER PROFILE..." },
        { progress: 100, text: "SYSTEM READY." }
    ];

    useEffect(() => {
        let currentStep = 0;

        const interval = setInterval(() => {
            if (currentStep >= bootSequence.length) {
                clearInterval(interval);
                setTimeout(onComplete, 800); // Slight delay after 100%
                return;
            }

            const step = bootSequence[currentStep];
            setProgress(step.progress);
            setStatus(step.text);
            setLogs(prev => [...prev.slice(-4), `[OK] ${step.text}`]);

            currentStep++;
        }, 400); // Duration per step

        return () => clearInterval(interval);
    }, []);

    return (
        <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 1.1, filter: "blur(20px)" }}
            transition={{ duration: 0.8 }}
            className="fixed inset-0 z-[200] bg-black text-cyan-500 font-mono flex flex-col items-center justify-center overflow-hidden"
        >
            {/* Background Grid */}
            <div className="absolute inset-0 bg-grid-pattern opacity-10 pointer-events-none"></div>

            <div className="w-full max-w-lg p-8 relative z-10 flex flex-col gap-8">
                {/* Logo / Header */}
                <div className="flex flex-col items-center gap-4">
                    <div className="relative">
                        <div className="absolute inset-0 bg-cyan-500/20 blur-xl rounded-full animate-pulse"></div>
                        <Hexagon className="w-16 h-16 text-cyan-400 animate-spin-slow" />
                    </div>
                    <h1 className="text-3xl font-black tracking-[0.5em] text-white">QYNTARA NEXUS</h1>
                    <div className="text-xs text-cyan-500/50 tracking-widest">BOOT SEQUENCE INITIATED</div>
                </div>

                {/* Progress Bar */}
                <div className="space-y-2">
                    <div className="flex justify-between text-xs text-cyan-400/80">
                        <span>{status}</span>
                        <span>{progress}%</span>
                    </div>
                    <div className="h-1 w-full bg-cyan-950 rounded-full overflow-hidden border border-cyan-900">
                        <motion.div
                            className="h-full bg-cyan-400 shadow-[0_0_15px_#22d3ee]"
                            initial={{ width: 0 }}
                            animate={{ width: `${progress}%` }}
                            transition={{ ease: "linear" }}
                        />
                    </div>
                </div>

                {/* Terminal Logs */}
                <div className="bg-black/50 border border-white/5 p-4 rounded text-[10px] h-32 flex flex-col justify-end font-mono">
                    {logs.map((log, i) => (
                        <div key={i} className="text-gray-400 border-l-2 border-cyan-500/50 pl-2 mb-1">
                            <span className="text-cyan-600 mr-2">{new Date().toISOString().split('T')[1].split('.')[0]}</span>
                            {log}
                        </div>
                    ))}
                    <div className="animate-pulse text-cyan-400">_</div>
                </div>

                {/* System Icons Check */}
                <div className="flex justify-center gap-8 opacity-50">
                    <StatusIcon icon={Cpu} active={progress > 20} delay={0} />
                    <StatusIcon icon={Database} active={progress > 40} delay={0.1} />
                    <StatusIcon icon={Wifi} active={progress > 60} delay={0.2} />
                    <StatusIcon icon={ShieldCheck} active={progress > 80} delay={0.3} />
                    <StatusIcon icon={Globe} active={progress > 95} delay={0.4} />
                </div>
            </div>
        </motion.div>
    );
}

function StatusIcon({ icon: Icon, active, delay }: any) {
    return (
        <motion.div
            animate={{
                opacity: active ? 1 : 0.3,
                scale: active ? [0.8, 1.2, 1] : 0.8,
                color: active ? "#22d3ee" : "#4b5563"
            }}
            transition={{ delay }}
        >
            <Icon className="w-6 h-6" />
        </motion.div>
    );
}
