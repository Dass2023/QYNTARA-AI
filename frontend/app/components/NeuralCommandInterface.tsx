import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { NeonButton } from './ui/NeonButton';

interface Message {
    role: 'user' | 'agent';
    content: string;
    timestamp: number;
}

export default function NeuralCommandInterface() {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([
        { role: 'agent', content: 'Neural Link Established. I am your Technical Director. How can I assist you with the pipeline today?', timestamp: Date.now() }
    ]);
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSubmit = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || loading) return;

        const userMsg: Message = { role: 'user', content: input, timestamp: Date.now() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch('http://localhost:8000/agent/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: userMsg.content })
            });
            const data = await res.json();

            const agentMsg: Message = {
                role: 'agent',
                content: data.response || "I encountered an error processing your request.",
                timestamp: Date.now()
            };
            setMessages(prev => [...prev, agentMsg]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'agent', content: "Connection Error: Could not reach the Neural Core.", timestamp: Date.now() }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-black/40 backdrop-blur-md rounded-xl border border-cyan-500/20 overflow-hidden shadow-[0_0_30px_-10px_rgba(0,243,255,0.1)]">
            {/* Header */}
            <div className="h-12 border-b border-white/10 flex items-center px-6 bg-cyan-950/20">
                <Sparkles className="w-4 h-4 text-cyan-400 mr-3 animate-pulse" />
                <span className="font-mono text-xs tracking-widest text-cyan-300">NEURAL COMMAND INTERFACE // TD-LEVEL</span>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar" ref={scrollRef}>
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 border ${msg.role === 'agent' ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400' : 'bg-purple-500/10 border-purple-500/30 text-purple-400'}`}>
                            {msg.role === 'agent' ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
                        </div>
                        <div className={`max-w-[80%] p-4 rounded-lg border backdrop-blur-sm text-sm leading-relaxed ${msg.role === 'agent' ? 'bg-cyan-950/30 border-cyan-500/20 text-cyan-100 rounded-tl-none' : 'bg-purple-950/30 border-purple-500/20 text-purple-100 rounded-tr-none'}`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-4">
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                            <Bot className="w-5 h-5" />
                        </div>
                        <div className="bg-cyan-950/30 border border-cyan-500/20 p-4 rounded-lg rounded-tl-none flex items-center gap-2">
                            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-white/10 bg-black/40">
                <form onSubmit={handleSubmit} className="flex gap-4">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Enter command (e.g., 'Generate a sci-fi crate and validate it')..."
                        className="flex-1 bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-mono placeholder:text-gray-600"
                        disabled={loading}
                    />
                    <NeonButton variant="cyan" type="submit" disabled={loading} className="px-6">
                        <Send className="w-4 h-4" />
                    </NeonButton>
                </form>
            </div>
        </div>
    );
}
