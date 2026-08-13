"use client";
import React from 'react';

export default function CyberGrid() {
    return (
        <div className="fixed inset-0 z-[-1] overflow-hidden pointer-events-none">
            <div className="absolute inset-0 bg-[#020205]"></div>
            <div className="absolute inset-0 perspective-grid"><div className="grid-lines"></div></div>
        </div>
    );
}
