"use client";
import React, { useState } from 'react';
import HolographicDropzone from './HolographicDropzone';
import { NeonButton } from './ui/NeonButton';
import { motion, AnimatePresence } from 'framer-motion';
import { Type, Image as ImageIcon, Sparkles } from 'lucide-react';

export default function JobSubmitter({ onSubmit, loading }: { onSubmit: (s: any, f?: File) => void, loading: boolean }) {
    const [mode, setMode] = useState<'text' | 'visual'>('text');
    const [prompt, setPrompt] = useState("cyberpunk helmet");
    const [file, setFile] = useState<File | null>(null);
    const [highFidelity, setHighFidelity] = useState(false);

    return (
        <div className="flex flex-col gap-6 h-full">
            {/* Child Tabs (Mode Selection) */}
            <div className="flex border-b border-white/10">
                <button
                    onClick={() => setMode('text')}
                    className={`flex-1 pb-3 text-xs font-mono font-bold tracking-wider transition-all relative ${mode === 'text' ? 'text-cyan-400' : 'text-gray-500 hover:text-gray-300'}`}
                >
                    TEXT TO 3D
                    {mode === 'text' && (
                        <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-[2px] bg-cyan-400 shadow-[0_0_10px_rgba(0,243,255,0.5)]" />
                    )}
                </button>
                <button
                    onClick={() => setMode('visual')}
                    className={`flex-1 pb-3 text-xs font-mono font-bold tracking-wider transition-all relative ${mode === 'visual' ? 'text-purple-400' : 'text-gray-500 hover:text-gray-300'}`}
                >
                    IMAGE TO 3D
                    {mode === 'visual' && (
                        <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-[2px] bg-purple-400 shadow-[0_0_10px_rgba(188,19,254,0.5)]" />
                    )}
                </button>
            </div>

            {/* Input Area */}
            <div className="flex-1 relative flex flex-col gap-4">
                <div className="flex-1 relative">
                    <AnimatePresence mode="wait">
                        {mode === 'text' ? (
                            <motion.div
                                key="text"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                className="h-full flex flex-col gap-4"
                            >
                                <textarea
                                    className="flex-1 w-full bg-black/20 border border-white/10 p-4 text-sm font-mono text-cyan-100 focus:outline-none focus:border-cyan-500/50 transition-colors resize-none rounded-md placeholder:text-white/20"
                                    placeholder="// ENTER ASSET DESCRIPTION..."
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                />

                                {/* Generation Settings */}
                                <div className="bg-black/40 border border-white/10 p-3 rounded-md flex items-center justify-between">
                                    <div className="flex flex-col">
                                        <span className="text-xs font-bold text-cyan-400">HIGH FIDELITY MODE</span>
                                        <span className="text-[10px] text-gray-500">Uses Stable Diffusion + Trellis (Slower)</span>
                                    </div>
                                    <button
                                        onClick={() => setHighFidelity(!highFidelity)}
                                        className={`w-10 h-5 rounded-full relative transition-colors ${highFidelity ? 'bg-cyan-500' : 'bg-white/10'}`}
                                    >
                                        <div className={`absolute top-1 w-3 h-3 rounded-full bg-white transition-all ${highFidelity ? 'left-6' : 'left-1'}`} />
                                    </button>
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="visual"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="h-full"
                            >
                                <div className="h-full border border-dashed border-white/10 rounded-md hover:border-purple-500/50 transition-colors bg-black/20">
                                    <HolographicDropzone onFileSelected={setFile} />
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            {/* Action Button */}
            <NeonButton
                onClick={() => onSubmit({ prompt, mode, quality: highFidelity ? 'high' : 'draft' }, file || undefined)}
                loading={loading}
                variant={mode === 'text' ? 'cyan' : 'purple'}
                className="w-full h-10 text-xs tracking-wider"
            >
                {loading ? 'GENERATING...' : <><Sparkles className="w-4 h-4" /> GENERATE 3D MODEL</>}
            </NeonButton>
        </div>
    );
}
