import React from 'react';

interface HoloCardProps {
    children: React.ReactNode;
    title?: string;
    className?: string;
}

export default function HoloCard({ children, title, className = "" }: HoloCardProps) {
    return (
        <div className={`relative bg-black/40 backdrop-blur-md border border-white/10 rounded-xl overflow-hidden flex flex-col ${className}`}>
            {/* Holographic Border Effect */}
            <div className="absolute inset-0 pointer-events-none rounded-xl border border-white/5 shadow-[inset_0_0_20px_rgba(0,243,255,0.05)]"></div>

            {/* Corner Accents */}
            <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-cyan-500/50 rounded-tl"></div>
            <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-cyan-500/50 rounded-tr"></div>
            <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-cyan-500/50 rounded-bl"></div>
            <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-cyan-500/50 rounded-br"></div>

            {/* Header */}
            {title && (
                <div className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-white/5 relative z-10">
                    <h3 className="font-mono text-xs tracking-widest text-cyan-400 uppercase flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-pulse"></span>
                        {title}
                    </h3>
                    <div className="flex gap-1">
                        <div className="w-1 h-1 bg-white/20 rounded-full"></div>
                        <div className="w-1 h-1 bg-white/20 rounded-full"></div>
                        <div className="w-1 h-1 bg-white/20 rounded-full"></div>
                    </div>
                </div>
            )}

            {/* Content */}
            <div className="flex-1 relative z-10 p-4">
                {children}
            </div>
        </div>
    );
}
