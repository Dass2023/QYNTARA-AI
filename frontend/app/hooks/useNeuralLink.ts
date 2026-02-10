import { useEffect, useState, useRef } from 'react';

export function useNeuralLink() {
    const [messages, setMessages] = useState<string[]>([]);
    const [isConnected, setIsConnected] = useState(false);

    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        // Prevent multiple connections
        if (wsRef.current) return;

        setMessages(["[SYSTEM] Initializing Neural Link...", "[SYSTEM] Connecting to QYNTARA Core..."]);

        const ws = new WebSocket('ws://localhost:8000/ws/neural-link');
        wsRef.current = ws;

        ws.onopen = () => {
            setIsConnected(true);
            setMessages(p => [...p, "[SYSTEM] Neural Link ESTABLISHED."]);
        };

        ws.onmessage = (e) => setMessages(p => [...p, e.data]);

        ws.onclose = () => {
            setIsConnected(false);
            setMessages(p => [...p, "[SYSTEM] Neural Link DISCONNECTED."]);
            wsRef.current = null;
        };

        ws.onerror = (e) => {
            setMessages(p => [...p, "[ERROR] Neural Link Connection Failed."]);
        };

        return () => {
            // Only close if the connection is OPEN.
            if (ws.readyState === WebSocket.OPEN) {
                ws.close();
            }
            wsRef.current = null;
        };
    }, []);

    return { messages, isConnected };
}
