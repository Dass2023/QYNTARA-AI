"use client";
import React, { useState, useEffect } from 'react';

export default function RetopologyControls({ onChange }: { onChange: (s: any) => void }) {
    const [count, setCount] = useState(5000);
    useEffect(() => { onChange({ target_count: count }); }, [count, onChange]);
    return (
        <div className="glass-panel p-4 rounded-xl border border-cyan-500/20 mb-6">
            <div className="text-cyan-400 text-xs mb-2">TARGET POLYGONS: {count}</div>
            <input type="range" min="500" max="50000" step="500" value={count} onChange={e => setCount(parseInt(e.target.value))} className="w-full" />
        </div>
    );
}
