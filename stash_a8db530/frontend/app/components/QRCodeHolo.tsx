"use client";
import React from 'react';
import { QRCodeSVG } from 'qrcode.react';

export default function QRCodeHolo({ url, onClose }: { url: string, onClose: () => void }) {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80" onClick={onClose}>
            <div className="bg-white p-4 rounded-lg"><QRCodeSVG value={url} size={200} /></div>
        </div>
    );
}
