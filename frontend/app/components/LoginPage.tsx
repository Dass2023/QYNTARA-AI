"use client";
import React, { useState } from 'react';

export default function LoginPage({ onLogin }: { onLogin: (k: string) => void }) {
    const [key, setKey] = useState("");
    return (
        <div className="min-h-screen bg-black flex items-center justify-center">
            <div className="p-8 border border-cyan-500/30 bg-black/80 rounded-xl text-center">
                <h1 className="text-4xl font-black text-cyan-400 mb-8">QYNTARA AI</h1>
                <input type="password" value={key} onChange={e => setKey(e.target.value)} className="w-full bg-black/50 border border-cyan-900 text-cyan-400 p-4 rounded mb-4 text-center" placeholder="ENTER ACCESS CODE" />
                <button onClick={() => onLogin(key)} className="w-full py-4 bg-cyan-600 font-bold">AUTHENTICATE</button>
            </div>
        </div>
    );
}
