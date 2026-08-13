"use client";
import React from "react";
import { motion } from "framer-motion";
import { cn } from "../../../lib/utils";

interface HoloCardProps {
    title?: string;
    children: React.ReactNode;
    className?: string;
}

export function HoloCard({ title, children, className }: HoloCardProps) {
    return (
        <div className={cn(
            "glass-panel rounded-xl p-6 flex flex-col relative group transition-all duration-500",
            className
        )}>
            {/* Holographic Corner Accents */}
            <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-cyan-500/30 rounded-tl-xl group-hover:border-cyan-400/80 transition-colors duration-500"></div>
            <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-cyan-500/30 rounded-br-xl group-hover:border-cyan-400/80 transition-colors duration-500"></div>

            {title && (
                <div className="mb-4 flex items-center justify-between relative z-10">
                    <h3 className="font-display text-lg tracking-wider text-white/90 group-hover:text-cyan-400 transition-colors duration-300 flex items-center gap-2">
                        {title}
                    </h3>
                    <div className="h-[1px] flex-1 ml-4 bg-gradient-to-r from-cyan-500/30 to-transparent"></div>
                </div>
            )}
            <div className="relative z-10 flex-1 flex flex-col min-h-0">
                {children}
            </div>
        </div>
    );
}
