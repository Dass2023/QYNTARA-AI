import React from 'react';
import { motion } from 'framer-motion';

export const QyntaraLogo = ({ className = "w-12 h-12" }: { className?: string }) => {
    return (
        <div className={`relative flex items-center justify-center ${className}`}>
            {/* Outer Orbital Ring */}
            <motion.svg
                viewBox="0 0 100 100"
                className="w-full h-full absolute inset-0"
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
                <defs>
                    <linearGradient id="orbGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.8" />
                        <stop offset="100%" stopColor="#818cf8" stopOpacity="0.8" />
                    </linearGradient>
                </defs>
                <circle cx="50" cy="50" r="45" stroke="url(#orbGradient)" strokeWidth="1" fill="none" strokeDasharray="10 5" opacity="0.5" />
                <circle cx="50" cy="50" r="45" stroke="cyan" strokeWidth="0.5" fill="none" strokeDasharray="80 100" opacity="0.8" />
            </motion.svg>

            {/* Inner Core Construction */}
            <svg viewBox="0 0 100 100" className="w-full h-full p-2">
                <defs>
                    <linearGradient id="coreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#06b6d4" />
                        <stop offset="50%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#a855f7" />
                    </linearGradient>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* Central Hex with Connections */}
                <path
                    d="M50 20 L76 35 V65 L50 80 L24 65 V35 Z"
                    fill="none"
                    stroke="url(#coreGradient)"
                    strokeWidth="2"
                    filter="url(#glow)"
                />

                {/* Neural Nodes */}
                <circle cx="50" cy="20" r="3" fill="#22d3ee" filter="url(#glow)" />
                <circle cx="76" cy="35" r="3" fill="#818cf8" filter="url(#glow)" />
                <circle cx="76" cy="65" r="3" fill="#a855f7" filter="url(#glow)" />
                <circle cx="50" cy="80" r="3" fill="#22d3ee" filter="url(#glow)" />
                <circle cx="24" cy="65" r="3" fill="#818cf8" filter="url(#glow)" />
                <circle cx="24" cy="35" r="3" fill="#a855f7" filter="url(#glow)" />

                {/* Core Pulse */}
                <circle cx="50" cy="50" r="10" fill="url(#coreGradient)" opacity="0.8">
                    <animate attributeName="opacity" values="0.8;0.4;0.8" dur="3s" repeatCount="indefinite" />
                </circle>
            </svg>
        </div>
    );
};
