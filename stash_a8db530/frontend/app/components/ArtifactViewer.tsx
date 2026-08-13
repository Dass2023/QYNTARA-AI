"use client";
import React from 'react';
import MeshViewer from './MeshViewer';
import { HoloCard } from './ui/HoloCard';
import { CheckCircle, AlertTriangle, Box, Layers } from 'lucide-react';

export default function ArtifactViewer({ data, title }: { data: any, title: string }) {
    if (!data) return null;

    // Special handling for Visual Analysis (Segmentation)
    if (title === "Visual Analysis" || (data.detected_objects && data.style_analysis)) {
        return (
            <HoloCard title="VISUAL ANALYSIS" className="border-purple-500/30">
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-mono text-gray-400">CONFIDENCE</span>
                        <span className="text-sm font-bold text-purple-400">{(data.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div className="space-y-2">
                        <span className="text-xs font-mono text-gray-400">DETECTED OBJECTS</span>
                        <div className="flex flex-wrap gap-2">
                            {data.detected_objects.map((obj: string, i: number) => (
                                <span key={i} className="px-2 py-1 bg-purple-500/10 border border-purple-500/30 rounded text-xs text-purple-300 uppercase">{obj}</span>
                            ))}
                        </div>
                    </div>
                    <div>
                        <span className="text-xs font-mono text-gray-400">STYLE</span>
                        <div className="text-sm text-white">{data.style_analysis}</div>
                    </div>
                </div>
            </HoloCard>
        );
    }

    // Default Mesh Viewer
    const meshUrl = title === "Generative 3D" && data.generated_mesh_path ? `http://localhost:8000/static/${data.generated_mesh_path.split('/').pop()}` : null;
    if (meshUrl) {
        return (
            <HoloCard title={title} className="border-cyan-500/30">
                <div className="h-40 relative rounded overflow-hidden border border-white/5">
                    <MeshViewer meshUrl={meshUrl} />
                </div>
                {data.source_image && <div className="mt-2 text-[10px] font-mono text-gray-500">SOURCE: {data.source_image}</div>}
            </HoloCard>
        );
    }

    // Default JSON View
    return (
        <HoloCard title={title} className="border-cyan-500/20">
            <pre className="text-[10px] font-mono text-cyan-200/70 overflow-auto max-h-60 custom-scrollbar p-2 bg-black/20 rounded">
                {JSON.stringify(data, null, 2)}
            </pre>
        </HoloCard>
    );
}
