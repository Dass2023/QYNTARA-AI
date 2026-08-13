"use client";
import React, { useEffect, useRef } from 'react';

export default function SystemTerminal({ logs }: { logs: string[] }) {
    const bottomRef = useRef<HTMLDivElement>(null);
    useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);
    return (
        <div className="glass-panel p-4 rounded-xl border border-cyan-500/20 h-64 overflow-y-auto font-mono text-xs">
            {logs.map((log, i) => (
                <div key={i} className="mb-1">
                    <span className="text-cyan-500 mr-2">[{new Date().toLocaleTimeString()}]</span>
                    <span className="text-cyan-100">{log}</span>
                </div>
            ))}
            <div ref={bottomRef} />
        </div>
    );
}
