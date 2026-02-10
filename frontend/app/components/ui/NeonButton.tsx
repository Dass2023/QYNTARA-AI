"use client";
import React from "react";
import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "../../../lib/utils";
import { Loader2 } from "lucide-react";

interface NeonButtonProps extends HTMLMotionProps<"button"> {
    variant?: "cyan" | "purple" | "danger" | "green";
    loading?: boolean;
    children: React.ReactNode;
}

export const NeonButton = ({ children, className, variant = "cyan", loading, ...props }: NeonButtonProps) => {
    return (
        <motion.button
            whileHover={{ scale: 1.02, textShadow: "0 0 8px rgb(255,255,255)" }}
            whileTap={{ scale: 0.98 }}
            className={cn(
                "relative px-6 py-3 rounded-lg font-mono text-sm tracking-widest uppercase transition-all duration-300 overflow-hidden group",
                variant === "cyan" && "bg-cyan-950/30 border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-400 hover:shadow-[0_0_30px_-5px_rgba(0,243,255,0.4)]",
                variant === "purple" && "bg-purple-950/30 border border-purple-500/50 text-purple-400 hover:bg-purple-500/20 hover:border-purple-400 hover:shadow-[0_0_30px_-5px_rgba(188,19,254,0.4)]",
                variant === "green" && "bg-green-950/30 border border-green-500/50 text-green-400 hover:bg-green-500/20 hover:border-green-400 hover:shadow-[0_0_30px_-5px_rgba(0,255,128,0.4)]",
                variant === "danger" && "bg-red-950/30 border border-red-500/50 text-red-400 hover:bg-red-500/20 hover:border-red-400 hover:shadow-[0_0_30px_-5px_rgba(255,0,60,0.4)]",
                loading && "opacity-70 cursor-wait",
                className
            )}
            disabled={loading || props.disabled}
            {...props}
        >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:animate-[shimmer_1s_infinite] pointer-events-none"></div>
            <span className="relative z-10 flex items-center gap-2">
                {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                {children}
            </span>
        </motion.button>
    );
};
