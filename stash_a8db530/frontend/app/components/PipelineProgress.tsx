"use client";
import React, { useMemo } from 'react';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

interface PipelineProgressProps {
    messages: string[];
}

const STAGES = [
    { id: 'segment', label: 'SEGMENTATION', keywords: ['Segmentation'] },
    { id: 'validate', label: 'VALIDATION', keywords: ['Validating', 'Compliance'] },
    { id: 'uv', label: 'UV UNWRAP', keywords: ['UVs', 'Lightmap'] },
    { id: 'remesh', label: 'REMESHING', keywords: ['Remeshing', 'Quad'] },
    { id: 'gen', label: 'GENERATIVE', keywords: ['Generating 3D', 'Vision-to-3D'] },
    { id: 'export', label: 'EXPORT', keywords: ['Export'] },
];

export default function PipelineProgress({ messages }: PipelineProgressProps) {
    const currentStageIndex = useMemo(() => {
        if (messages.length === 0) return -1;
        const lastMsg = messages[messages.length - 1];
        if (lastMsg.includes("Pipeline Complete")) return STAGES.length;

        // Find the latest stage mentioned in the logs
        let maxIndex = -1;
        messages.forEach(msg => {
            STAGES.forEach((stage, idx) => {
                if (stage.keywords.some(k => msg.includes(k))) {
                    maxIndex = Math.max(maxIndex, idx);
                }
            });
        });
        return maxIndex;
    }, [messages]);

    return (
        <div className="w-full bg-black/40 border border-white/5 rounded-lg p-6 mb-6 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent"></div>

            <div className="flex justify-between items-center relative z-10">
                {STAGES.map((stage, i) => {
                    const isCompleted = currentStageIndex > i;
                    const isActive = currentStageIndex === i;
                    const isPending = currentStageIndex < i;

                    return (
                        <div key={stage.id} className="flex flex-col items-center gap-3 relative group">
                            {/* Connector Line */}
                            {i < STAGES.length - 1 && (
                                <div className={cn(
                                    "absolute top-[10px] left-[50%] w-[calc(100%+2rem)] h-[2px] -z-10 transition-colors duration-500",
                                    isCompleted ? "bg-cyan-500" : "bg-white/10"
                                )} />
                            )}

                            <div className={cn(
                                "w-6 h-6 rounded-full flex items-center justify-center border transition-all duration-300 bg-void",
                                isCompleted ? "border-cyan-500 text-cyan-500 shadow-[0_0_10px_rgba(0,243,255,0.5)]" :
                                    isActive ? "border-cyan-400 text-cyan-400 animate-pulse shadow-[0_0_15px_rgba(0,243,255,0.3)]" :
                                        "border-white/10 text-white/10"
                            )}>
                                {isCompleted ? <CheckCircle2 className="w-4 h-4" /> :
                                    isActive ? <Loader2 className="w-4 h-4 animate-spin" /> :
                                        <Circle className="w-3 h-3" />}
                            </div>

                            <span className={cn(
                                "font-mono text-[10px] tracking-widest transition-colors duration-300",
                                isActive || isCompleted ? "text-cyan-400" : "text-white/20"
                            )}>
                                {stage.label}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
