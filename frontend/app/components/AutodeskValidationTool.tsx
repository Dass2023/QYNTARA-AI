"use client";
import React from 'react';

export default function AutodeskValidationTool({ data }: { data: any }) {
    if (!data) return null;
    return (
        <div className="glass-panel p-6 rounded-xl border border-cyan-500/20">
            <h3 className="text-xl font-bold text-cyan-400">Autodesk Validation</h3>
            <div className="text-xs font-mono text-cyan-200 mt-2">{JSON.stringify(data.checks, null, 2)}</div>
        </div>
    );
}
