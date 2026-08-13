"use client";
import React, { useState, useEffect } from 'react';
import { HoloCard } from './ui/HoloCard';
import { NeonButton } from './ui/NeonButton';
import { Globe, Zap, Leaf, Cpu, Wifi, Activity, Server, Wind, Clock, TrendingUp, Dna } from 'lucide-react';

export default function Industry50Dashboard() {
    const [systemHealth, setSystemHealth] = useState(98);
    const [energyUsage, setEnergyUsage] = useState(450); // kWh
    const [carbonSaved, setCarbonSaved] = useState(12.5); // kg
    const [simulationMode, setSimulationMode] = useState(false);
    const [futureTime, setFutureTime] = useState(0); // Months into future
    const [dnaTraits, setDnaTraits] = useState({ durability: 50, eco: 50, cost: 50 });

    // Mock IoT Data Stream
    useEffect(() => {
        const interval = setInterval(() => {
            setEnergyUsage(prev => prev + (Math.random() - 0.4));
            setSystemHealth(prev => Math.min(100, Math.max(90, prev + (Math.random() - 0.5))));
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="h-full grid grid-cols-12 gap-6 animate-in fade-in zoom-in duration-500">
            {/* Left Panel: Generative Product DNA */}
            <div className="col-span-3 flex flex-col gap-6">
                <HoloCard title="Generative DNA" className="flex-1">
                    <div className="flex flex-col gap-6 h-full">
                        <div className="relative h-48 w-full bg-black/50 rounded-lg border border-cyan-500/20 flex items-center justify-center overflow-hidden">
                            {/* Abstract DNA Visualization */}
                            <div className="absolute inset-0 flex items-center justify-center opacity-50">
                                <div className="w-20 h-40 border-l-2 border-r-2 border-cyan-500/50 rounded-[50%] animate-spin-slow" style={{ animationDuration: `${3000 - (dnaTraits.eco * 20)}ms` }}></div>
                                <div className="absolute w-20 h-40 border-t-2 border-b-2 border-purple-500/50 rounded-[50%] animate-spin-reverse-slow" style={{ animationDuration: `${3000 - (dnaTraits.durability * 20)}ms` }}></div>
                            </div>
                            <div className="z-10 text-center">
                                <span className="text-xs font-mono text-cyan-400 block">EVOLUTION: GEN {Math.floor(dnaTraits.durability / 10 + dnaTraits.eco / 10)}</span>
                                <span className="text-[10px] text-gray-500">ADAPTIVE MESH</span>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <DnaSlider label="DURABILITY" value={dnaTraits.durability} onChange={(v: number) => setDnaTraits(prev => ({ ...prev, durability: v }))} color="cyan" />
                            <DnaSlider label="ECO-FRIENDLINESS" value={dnaTraits.eco} onChange={(v: number) => setDnaTraits(prev => ({ ...prev, eco: v }))} color="green" />
                            <DnaSlider label="COST EFFICIENCY" value={dnaTraits.cost} onChange={(v: number) => setDnaTraits(prev => ({ ...prev, cost: v }))} color="purple" />
                        </div>

                        <div className="mt-auto">
                            <NeonButton variant="cyan" className="w-full text-[10px]">
                                EVOLVE GENERATION
                            </NeonButton>
                        </div>
                    </div>
                </HoloCard>

                <HoloCard title="Sustainability Targets" className="h-auto">
                    <div className="space-y-4">
                        <div className="flex items-center gap-4">
                            <Leaf className="w-5 h-5 text-green-400" />
                            <div>
                                <div className="text-[10px] font-mono text-gray-400">CARBON OFFSET</div>
                                <div className="text-xl font-display text-white">{(carbonSaved * (1 + futureTime * 0.1)).toFixed(2)} kg</div>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <Zap className="w-5 h-5 text-yellow-400" />
                            <div>
                                <div className="text-[10px] font-mono text-gray-400">ENERGY EFFICIENCY</div>
                                <div className="text-xl font-display text-white">{((energyUsage / 10) * (1 - futureTime * 0.05)).toFixed(1)} kWh</div>
                            </div>
                        </div>
                    </div>
                </HoloCard>
            </div>

            {/* Center Panel: Digital Twin & Predictive Simulation */}
            <div className="col-span-6 h-full flex flex-col gap-6">
                <HoloCard className="h-[60%] p-0 overflow-hidden relative group border-cyan-500/30 shadow-[0_0_50px_-20px_rgba(0,243,255,0.1)]">
                    <div className="absolute top-4 left-4 z-20 flex gap-2">
                        <div className="bg-black/80 backdrop-blur px-3 py-1 rounded border border-cyan-500/30 text-[10px] font-mono text-cyan-400 flex items-center gap-2">
                            <Globe className="w-3 h-3" /> DIGITAL TWIN: FACTORY_01
                        </div>
                        {simulationMode && (
                            <div className="bg-purple-900/80 backdrop-blur px-3 py-1 rounded border border-purple-500/50 text-[10px] font-mono text-purple-200 flex items-center gap-2 animate-pulse">
                                <Clock className="w-3 h-3" /> SIMULATION: +{futureTime} MONTHS
                            </div>
                        )}
                    </div>

                    {/* 3D View Placeholder */}
                    <div className="w-full h-full bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-gray-900 via-[#050a14] to-black flex items-center justify-center relative">
                        {/* Grid Floor - Changes color in simulation mode */}
                        <div className={`absolute inset-0 bg-[linear-gradient(${simulationMode ? 'rgba(188,19,254,0.1)' : 'rgba(0,243,255,0.05)'}_1px,transparent_1px),linear-gradient(90deg,${simulationMode ? 'rgba(188,19,254,0.1)' : 'rgba(0,243,255,0.05)'}_1px,transparent_1px)] bg-[size:40px_40px] [transform:perspective(1000px)_rotateX(60deg)_translateY(100px)_scale(1.5)] opacity-50 transition-colors duration-1000`}></div>

                        {/* Central Hologram Effect */}
                        <div className="relative z-10 animate-float">
                            <div className={`w-64 h-64 border ${simulationMode ? 'border-purple-500/30' : 'border-cyan-500/30'} rounded-full flex items-center justify-center relative shadow-[0_0_30px_${simulationMode ? 'rgba(188,19,254,0.2)' : 'rgba(0,243,255,0.1)'}] transition-all duration-1000`}>
                                <div className="w-48 h-48 border border-white/10 rounded-full animate-spin-slow"></div>
                                <Cpu className={`w-16 h-16 ${simulationMode ? 'text-purple-400' : 'text-cyan-400'} opacity-80 transition-colors duration-1000`} />
                            </div>
                        </div>

                        {/* Floating Labels */}
                        <FloatingLabel top="20%" left="20%" text="ROBOT_ARM_04 [IDLE]" />
                        <FloatingLabel top="60%" right="20%" text="CONVEYOR_BELT_02 [ACTIVE]" color="text-green-400" />
                    </div>

                    {/* Predictive Time Slider */}
                    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-2/3 bg-black/80 backdrop-blur border border-white/10 rounded-full px-6 py-3 flex items-center gap-4">
                        <span className="text-[10px] font-mono text-gray-400 whitespace-nowrap">NOW</span>
                        <input
                            type="range"
                            min="0"
                            max="12"
                            step="1"
                            value={futureTime}
                            onChange={(e) => {
                                setFutureTime(parseInt(e.target.value));
                                setSimulationMode(parseInt(e.target.value) > 0);
                            }}
                            className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500 hover:accent-cyan-400"
                        />
                        <span className="text-[10px] font-mono text-purple-400 whitespace-nowrap">+1 YEAR</span>
                    </div>
                </HoloCard>

                {/* Platform Ecosystem Evolution Graph */}
                <HoloCard title="Asset Evolution Pipeline" className="flex-1 relative overflow-hidden">
                    <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
                    <div className="flex items-center justify-between px-8 h-full relative z-10">
                        <PlatformNode icon="/icons/maya.png" label="MAYA" status="SOURCE" />
                        <ConnectionLine active />
                        <PlatformNode icon="/icons/qyntara.png" label="QYNTARA CORE" status="PROCESSING" highlight />
                        <ConnectionLine active />

                        <div className="flex flex-col gap-4">
                            <PlatformNode icon="/icons/unreal.png" label="UNREAL 5" status="READY" />
                            <PlatformNode icon="/icons/unity.png" label="UNITY 6" status="READY" />
                        </div>
                    </div>
                </HoloCard>
            </div>

            {/* Right Panel: Connected Agents & Supply Chain */}
            <div className="col-span-3 flex flex-col gap-6">
                <HoloCard title="Neural Collaboration" className="h-[400px] flex flex-col">
                    <div className="flex-1 overflow-y-auto p-2 space-y-3 custom-scrollbar text-[10px] font-mono">
                        <ChatBubble sender="HUMAN" text="Optimize factory layout for 20% energy reduction." />
                        <ChatBubble sender="QYNTARA" text="Analyzing spatial constraints... Proposed layout 'eco_v2' generated. Carbon footprint reduced by 18.5%." highlight />
                        {simulationMode && (
                            <ChatBubble sender="SIMULATION" text={`Projecting efficiency for month +${futureTime}: Energy savings exceed target by 4.5%.`} highlight />
                        )}
                    </div>
                    <div className="border-t border-white/10 p-2">
                        <input type="text" placeholder="Describe intent..." className="w-full bg-black/50 border border-white/10 rounded px-2 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500/50" />
                    </div>
                </HoloCard>

                <HoloCard title="Global Supply Network" className="flex-1">
                    <div className="h-full flex flex-col gap-2">
                        <div className="flex items-center justify-between text-[10px] font-mono text-gray-500 border-b border-white/5 pb-2">
                            <span>NODE</span>
                            <span>STATUS</span>
                        </div>
                        <AgentRow name="TOKYO_HUB_01" role="LOGISTICS" status="ACTIVE" />
                        <AgentRow name="BERLIN_FAB_04" role="PRODUCTION" status="IDLE" />
                        <AgentRow name="NY_RESEARCH" role="R&D" status="ONLINE" />
                    </div>
                </HoloCard>
            </div>
        </div>
    );
}

function DnaSlider({ label, value, onChange, color }: any) {
    const colorClass = color === "green" ? "accent-green-500" : color === "purple" ? "accent-purple-500" : "accent-cyan-500";
    return (
        <div className="space-y-1">
            <div className="flex justify-between text-[9px] font-mono text-gray-400">
                <span>{label}</span>
                <span>{value}%</span>
            </div>
            <input
                type="range"
                min="0"
                max="100"
                value={value}
                onChange={(e) => onChange(parseInt(e.target.value))}
                className={`w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer ${colorClass}`}
            />
        </div>
    );
}

function PlatformNode({ icon, label, status, highlight }: any) {
    return (
        <div className={`flex flex-col items-center gap-2 group ${highlight ? 'scale-110' : ''}`}>
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center border transition-all ${highlight ? 'bg-cyan-500/20 border-cyan-400 shadow-[0_0_20px_rgba(0,243,255,0.4)]' : 'bg-white/5 border-white/10 group-hover:border-cyan-500/30'}`}>
                {/* Placeholder for icon if image missing */}
                <div className="text-[10px] font-bold text-gray-400">{label.substring(0, 1)}</div>
            </div>
            <div className="flex flex-col items-center">
                <span className={`text-[10px] font-mono ${highlight ? 'text-cyan-400' : 'text-gray-400'}`}>{label}</span>
                <span className="text-[8px] font-mono text-gray-600">{status}</span>
            </div>
        </div>
    );
}

function ConnectionLine({ active }: any) {
    return (
        <div className="flex-1 h-[1px] bg-white/10 relative mx-2">
            {active && <div className="absolute inset-y-0 left-0 w-1/2 bg-cyan-500/50 shadow-[0_0_10px_#00f3ff] animate-pulse"></div>}
        </div>
    );
}

function ChatBubble({ sender, text, highlight }: any) {
    return (
        <div className={`flex flex-col gap-1 ${sender === 'HUMAN' ? 'items-end' : 'items-start'}`}>
            <span className="text-[9px] text-gray-600">{sender}</span>
            <div className={`px-3 py-2 rounded max-w-[90%] ${sender === 'HUMAN' ? 'bg-white/10 text-gray-300 rounded-tr-none' : highlight ? 'bg-cyan-950/50 border border-cyan-500/30 text-cyan-100 rounded-tl-none' : 'bg-black/50 border border-white/10 text-gray-400 rounded-tl-none'}`}>
                {text}
            </div>
        </div>
    );
}

function StatusBadge({ icon: Icon, label, status, color }: any) {
    return (
        <div className="bg-black/40 border border-white/5 p-2 rounded flex flex-col items-center justify-center gap-1">
            <Icon className={`w-4 h-4 ${color}`} />
            <div className="text-[9px] text-gray-500 font-mono">{label}</div>
            <div className={`text-[9px] font-bold ${color}`}>{status}</div>
        </div>
    );
}

function FloatingLabel({ top, left, right, bottom, text, color = "text-cyan-400" }: any) {
    return (
        <div className={`absolute pointer-events-none flex items-center gap-2`} style={{ top, left, right, bottom }}>
            <div className="w-2 h-2 rounded-full bg-white animate-pulse"></div>
            <div className={`text-[10px] font-mono ${color} bg-black/60 px-2 py-1 rounded border border-white/10 backdrop-blur-sm`}>
                {text}
            </div>
        </div>
    );
}

function MetricCard({ title, value, unit, trend, color = "cyan" }: any) {
    const colorClass = color === "green" ? "text-green-400" : color === "purple" ? "text-purple-400" : "text-cyan-400";
    return (
        <HoloCard className="flex flex-col justify-between p-4">
            <div className="text-[10px] font-mono text-gray-500 tracking-wider">{title}</div>
            <div>
                <div className={`text-2xl font-display ${colorClass}`}>{value}</div>
                <div className="text-[10px] font-mono text-gray-400 flex justify-between">
                    <span>{unit}</span>
                    <span className={colorClass}>{trend}</span>
                </div>
            </div>
        </HoloCard>
    );
}

function AgentRow({ name, role, status }: any) {
    return (
        <div className="flex items-center justify-between bg-white/5 border border-white/5 p-3 rounded hover:border-cyan-500/30 transition-colors group cursor-pointer">
            <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded bg-gradient-to-br from-gray-800 to-black border border-white/10 flex items-center justify-center">
                    <Cpu className="w-4 h-4 text-cyan-500/50 group-hover:text-cyan-400 transition-colors" />
                </div>
                <div>
                    <div className="text-xs font-bold text-gray-200 group-hover:text-white">{name}</div>
                    <div className="text-[9px] font-mono text-gray-500">{role}</div>
                </div>
            </div>
            <div className="text-[9px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-1 rounded border border-cyan-500/20">
                {status}
            </div>
        </div>
    );
}
