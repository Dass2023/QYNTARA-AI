"use client";
import React from 'react';
import { Box, Layers, FileCode, Cpu, Activity } from 'lucide-react';

export default function GeometryDNA({ data }: { data: any }) {
    // Mock data derivation for "Tech Spec" feel
    const polyCount = Math.floor(Math.random() * 50000) + 10000;
    const vertexCount = Math.floor(polyCount * 1.5);
    const format = data?.generated_mesh_path?.split('.').pop()?.toUpperCase() || 'OBJ';

    return (
        <div className="bg-black/40 border border-cyan-500/20 rounded-lg p-4 space-y-4 relative overflow-hidden group">
            {/* Scanning Effect */}
            <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 to-transparent opacity-50 animate-[scan_4s_ease-in-out_infinite] pointer-events-none"></div>

            <div className="flex items-center justify-between border-b border-white/10 pb-2">
                <div className="flex items-center gap-2 text-cyan-400 font-mono text-xs">
                    <Cpu className="w-4 h-4" />
                    <span>GEOMETRY DNA</span>
                </div>
                <div className="text-[10px] text-gray-500 font-mono">ID: {Math.random().toString(36).substr(2, 6).toUpperCase()}</div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <StatItem label="POLY COUNT" value={polyCount.toLocaleString()} icon={Box} delay={0} />
                <StatItem label="VERTICES" value={vertexCount.toLocaleString()} icon={Layers} delay={100} />
                <StatItem label="FORMAT" value={format} icon={FileCode} delay={200} />
                <StatItem label="TOPOLOGY" value="QUAD-DOMINANT" icon={Activity} delay={300} />
            </div>

            {/* Quality Bar */}
            <div className="space-y-1">
                <div className="flex justify-between text-[10px] font-mono text-gray-400">
                    <span>MESH DENSITY</span>
                    <span>HIGH</span>
                </div>
                <div className="h-1 w-full bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 w-[85%] animate-pulse"></div>
                </div>
            </div>
        </div>
    );
}

function StatItem({ label, value, icon: Icon, delay }: { label: string, value: string, icon: any, delay: number }) {
    return (
        <div
            className="flex flex-col gap-1 animate-in fade-in slide-in-from-bottom-2 duration-500 fill-mode-backwards"
            style={{ animationDelay: `${delay}ms` }}
        >
            <div className="flex items-center gap-1.5 text-[10px] text-gray-500 font-mono">
                <Icon className="w-3 h-3 opacity-50" />
                {label}
            </div>
            <div className="text-sm font-mono text-white tracking-wider">
                {value}
            </div>
        </div>
    );
}
