"use client";
import React from "react";

interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
}

export default class ErrorBoundary extends React.Component<
    { children: React.ReactNode },
    ErrorBoundaryState
> {
    constructor(props: { children: React.ReactNode }) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error) {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error("ErrorBoundary caught:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{
                    background: "#000",
                    color: "#ff4444",
                    padding: "40px",
                    fontFamily: "monospace",
                    minHeight: "100vh",
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-all"
                }}>
                    <h1 style={{ color: "#ff6666", fontSize: "24px", marginBottom: "20px" }}>
                        ⚠ QYNTARA RUNTIME ERROR
                    </h1>
                    <div style={{ color: "#ffaa00", marginBottom: "10px" }}>
                        {this.state.error?.message}
                    </div>
                    <div style={{ color: "#888", fontSize: "12px" }}>
                        {this.state.error?.stack}
                    </div>
                    <button
                        onClick={() => this.setState({ hasError: false, error: null })}
                        style={{
                            marginTop: "20px",
                            padding: "10px 20px",
                            background: "#333",
                            color: "#0ff",
                            border: "1px solid #0ff",
                            cursor: "pointer",
                            fontFamily: "monospace"
                        }}
                    >
                        RETRY
                    </button>
                </div>
            );
        }
        return this.props.children;
    }
}
