
"use client";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Hexagon, ArrowRight, CheckCircle, Activity, Layers, Sparkles } from 'lucide-react';
import { NeonButton } from './ui/NeonButton';
import HoloCard from './HoloCard';

export default function SystemOnboarding({ onComplete }: { onComplete: () => void }) {
    const [step, setStep] = useState(0);

    const steps = [
        {
            title: "WELCOME TO QYNTARA",
            subtitle: "THE DIGITAL 3D FACTORY",
            icon: Hexagon,
            color: "text-cyan-400",
            content: (
                <div className="space-y-4 text-center">
                    <p className="text-gray-300 text-sm">
                        You have entered an advanced <strong>Spatial Intelligence System</strong>.
                    </p>
                    <p className="text-gray-400 text-xs">
                        Unlike simple AI generators, Qyntara is a complete pipeline designed to build <strong>Production-Ready Game Assets</strong> from scratch.
                    </p>
                </div>
            )
        },
        {
            title: "THE WORKFLOW",
            subtitle: "FROM DREAM TO ENGINE",
            icon: Activity,
            color: "text-purple-400",
            content: (
                <div className="flex flex-col gap-4">
                    <div className="flex items-center gap-3 bg-white/5 p-3 rounded border border-white/10">
                        <div className="w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold text-xs">1</div>
                        <div className="text-left">
                            <div className="text-cyan-400 text-xs font-bold">CREATE</div>
                            <div className="text-gray-500 text-[10px]">Materialize assets via Quantum Intent Engine.</div>
                        </div>
                    </div>
                    <div className="flex items-center justify-center">
                        <ArrowRight className="w-4 h-4 text-gray-600 rotate-90" />
                    </div>
                    <div className="flex items-center gap-3 bg-white/5 p-3 rounded border border-white/10">
                        <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 font-bold text-xs">2</div>
                        <div className="text-left">
                            <div className="text-purple-400 text-xs font-bold">OPTIMIZE</div>
                            <div className="text-gray-500 text-[10px]">Auto-Remesh, UV Unwrap, and Validate for game engines.</div>
                        </div>
                    </div>
                </div>
            )
        },
        {
            title: "READY TO BEGIN",
            subtitle: "SYSTEM INITIALIZED",
            icon: Sparkles,
            color: "text-green-400",
            content: (
                <div className="space-y-4 text-center">
                    <p className="text-gray-300 text-sm">
                        Your workspace is ready.
                    </p>
                    <div className="bg-green-500/10 border border-green-500/20 p-4 rounded-lg">
                        <p className="text-green-400 text-xs font-mono">
                            // SYSTEM_STATUS: OPERATIONAL<br />
                            // NEURAL_LINK: ACTIVE<br />
                            // GPU_CLUSTER: ONLINE
                        </p>
                    </div>
                </div>
            )
        }
    ];

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md">
            <div className="max-w-md w-full">
                <HoloCard className="border-cyan-500/50 shadow-[0_0_50px_rgba(0,243,255,0.2)]">
                    <div className="p-6 flex flex-col items-center gap-6">
                        {/* Header Icon */}
                        <div className={`w-20 h-20 rounded-full bg-black/50 border border-white/10 flex items-center justify-center ${steps[step].color}`}>
                            {React.createElement(steps[step].icon, { className: "w-10 h-10 animate-pulse" })}
                        </div>

                        {/* Text Content */}
                        <div className="text-center space-y-2">
                            <h2 className={`text-2xl font-black tracking-widest ${steps[step].color}`}>{steps[step].title}</h2>
                            <p className="text-xs font-mono text-gray-500 tracking-[0.2em]">{steps[step].subtitle}</p>
                        </div>

                        {/* Dynamic Body */}
                        <div className="w-full">
                            {steps[step].content}
                        </div>

                        {/* Navigation */}
                        <div className="w-full flex gap-3 mt-4">
                            {step < steps.length - 1 ? (
                                <NeonButton variant="cyan" className="w-full" onClick={() => setStep(step + 1)}>
                                    NEXT STEP <ArrowRight className="w-4 h-4 ml-2" />
                                </NeonButton>
                            ) : (
                                <NeonButton variant="green" className="w-full" onClick={onComplete}>
                                    ENTER STUDIO <CheckCircle className="w-4 h-4 ml-2" />
                                </NeonButton>
                            )}
                        </div>

                        {/* Dots */}
                        <div className="flex gap-2">
                            {steps.map((_, i) => (
                                <div key={i} className={`w-2 h-2 rounded-full transition-colors ${i === step ? 'bg-cyan-400' : 'bg-gray-700'}`} />
                            ))}
                        </div>
                    </div>
                </HoloCard>
            </div>
        </div>
    );
}
