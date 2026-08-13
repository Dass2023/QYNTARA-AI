"use client";
import React, { useState, useEffect, useRef } from 'react';

export default function VoiceCommandModule({ onCommand }: { onCommand: (c: string) => void }) {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState("");
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
            const SpeechRecognition = (window as any).webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.onstart = () => setIsListening(true);
            recognition.onend = () => setIsListening(false);
            recognition.onresult = (e: any) => {
                const text = e.results[0][0].transcript.toUpperCase();
                setTranscript(text);
                if (e.results[0].isFinal) onCommand(text);
            };
            recognitionRef.current = recognition;
        }
    }, [onCommand]);

    return (
        <div className="flex items-center gap-4">
            <div className="font-mono text-xs text-cyan-400">{transcript || "VOICE STANDBY"}</div>
            <button onClick={() => isListening ? recognitionRef.current?.stop() : recognitionRef.current?.start()} className={`w-10 h-10 rounded-full border ${isListening ? 'bg-red-500/20 border-red-500' : 'bg-cyan-900/30 border-cyan-500'}`}>MIC</button>
        </div>
    );
}
