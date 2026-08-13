"use client";
import React, { useState, useEffect } from 'react';

// Force client-side only render
const ClientOnly = ({ children }: { children: React.ReactNode }) => {
    const [hasMounted, setHasMounted] = useState(false);
    useEffect(() => { setHasMounted(true); }, []);
    if (!hasMounted) return <div style={{ color: 'yellow' }}>Initializing Client...</div>;
    return <>{children}</>;
};

export default function VerifyPage() {
    const [count, setCount] = useState(0);

    return (
        <ClientOnly>
            <div style={{ padding: 50, background: '#000', color: '#0f0', border: '2px solid #0f0' }}>
                <h1>CRITICAL SYSTEM VERIFICATION</h1>
                <p>React Version: {React.version}</p>
                <p>Status: OPERATIONAL</p>
                <p>Count: {count}</p>
                <button onClick={() => setCount(c => c + 1)} style={{ padding: 20, fontSize: 20, cursor: 'pointer' }}>
                    TEST INTERACTION
                </button>
            </div>
        </ClientOnly>
    );
}
