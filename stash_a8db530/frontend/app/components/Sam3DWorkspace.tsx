"use client";
import React, { useState } from 'react';
import { HoloCard } from './ui/HoloCard';
import { NeonButton } from './ui/NeonButton';
import MeshViewer from './MeshViewer';
import ImageViewer from './ImageViewer';
import { MousePointer2, Box, Type, Layers, Eye, EyeOff, Trash2, Upload, Loader2 } from 'lucide-react';

interface Sam3DWorkspaceProps {
    meshUrl: string;
    onSegment: (point: [number, number, number], type: 'point' | 'box' | 'text', clickType?: 'left' | 'right') => void;
    segments: Array<{ id: number, color: string, visible: boolean }>;
    onToggleVisibility: (id: number) => void;
    onDeleteSegment: (id: number) => void;
    onMeshGenerated?: (url: string) => void;
}

export default function Sam3DWorkspace({ meshUrl, onSegment, segments, onToggleVisibility, onDeleteSegment, onMeshGenerated }: Sam3DWorkspaceProps) {
    const [activeTool, setActiveTool] = useState<'point' | 'box' | 'text'>('point');
    const [textPrompt, setTextPrompt] = useState('');
    const [showWireframe, setShowWireframe] = useState(false);
    const [explodedAmount, setExplodedAmount] = useState(0);

    // 2D State
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [serverImagePath, setServerImagePath] = useState<string | null>(null);
    const [viewMode, setViewMode] = useState<'3d' | '2d'>('3d');
    const [lastClick, setLastClick] = useState<[number, number] | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);

    const handleMeshClick = (point: [number, number, number], type: 'point' | 'box' | 'text', clickType?: 'left' | 'right') => {
        if (activeTool === 'point') {
            onSegment(point, 'point', clickType);
        }
    };

    const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setImageUrl(URL.createObjectURL(file));
            setViewMode('2d');

            // Upload to server
            const formData = new FormData();
            formData.append('file', file);
            try {
                console.log("Uploading image to server...");
                const res = await fetch('http://localhost:8000/upload', {
                    method: 'POST',
                    body: formData
                });
                if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
                const data = await res.json();
                console.log("Upload success:", data);
                setServerImagePath(data.path);
            } catch (err) {
                console.error("Upload failed", err);
                alert("Failed to upload image to server. Check console for details.");
            }
        }
    };

    const handleGenerate3D = async () => {
        console.log("Attempting to generate 3D...");
        console.log("Server Image Path:", serverImagePath);
        console.log("Last Click:", lastClick);

        if (!serverImagePath) {
            alert("Error: Image not uploaded to server. Please try uploading again.");
            return;
        }
        if (!lastClick) {
            alert("Error: No point selected. Please click on the image first.");
            return;
        }

        setIsGenerating(true);
        try {
            const response = await fetch('http://localhost:8000/segment-to-3d', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image_path: serverImagePath,
                    click_point: lastClick,
                    click_type: 'left'
                })
            });
            const data = await response.json();
            console.log("Generation Response:", data);

            if (data.status === 'success' && data.mesh_path) {
                const newMeshUrl = `http://localhost:8000/static/${data.mesh_path.split('/').pop()}`;
                if (onMeshGenerated) {
                    onMeshGenerated(newMeshUrl);
                }
                setViewMode('3d');
            } else {
                alert(`Generation Failed: ${data.message || "Unknown error"}`);
            }
        } catch (e) {
            console.error("Failed to generate 3D", e);
            alert("Network Error: Failed to connect to backend.");
        } finally {
            setIsGenerating(false);
        }
    };

    // Keyboard shortcuts
    React.useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key.toLowerCase() === 'p') setActiveTool('point');
            if (e.key.toLowerCase() === 'b') setActiveTool('box');
            if (e.key.toLowerCase() === 't') setActiveTool('text');
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    return (
        <div className="h-full grid grid-cols-12 gap-6 animate-in fade-in slide-in-from-right-10 duration-300">
            {/* Tools Panel */}
            <div className="col-span-2 flex flex-col gap-4">
                <HoloCard title="Tools" className="h-full flex flex-col gap-6">
                    <div className="flex flex-col gap-3">
                        <ToolButton
                            icon={MousePointer2}
                            label="Point (P)"
                            active={activeTool === 'point'}
                            onClick={() => setActiveTool('point')}
                        />
                        <ToolButton
                            icon={Box}
                            label="Box (B)"
                            active={activeTool === 'box'}
                            onClick={() => setActiveTool('box')}
                        />
                        <ToolButton
                            icon={Type}
                            label="Text (T)"
                            active={activeTool === 'text'}
                            onClick={() => setActiveTool('text')}
                        />
                    </div>

                    {activeTool === 'text' && (
                        <div className="space-y-2">
                            <label className="text-[10px] font-mono text-cyan-400">TEXT PROMPT</label>
                            <input
                                type="text"
                                value={textPrompt}
                                onChange={(e) => setTextPrompt(e.target.value)}
                                className="w-full bg-black/50 border border-white/10 rounded px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-cyan-500/50"
                                placeholder="e.g. 'car wheel'"
                            />
                            <NeonButton
                                variant="cyan"
                                className="w-full text-[10px]"
                                onClick={() => console.log("Text prompt:", textPrompt)}
                            >
                                SEGMENT
                            </NeonButton>
                        </div>
                    )}

                    <div className="h-px bg-white/10 my-2"></div>

                    {/* Input Source Toggle */}
                    <div className="space-y-2">
                        <div className="text-[10px] font-mono text-gray-500 tracking-wider">INPUT SOURCE</div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setViewMode('3d')}
                                className={`flex-1 py-1.5 text-[10px] font-mono rounded border transition-colors ${viewMode === '3d' ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400' : 'bg-black/40 border-white/10 text-gray-500'}`}
                            >
                                3D MESH
                            </button>
                            <button
                                onClick={() => setViewMode('2d')}
                                className={`flex-1 py-1.5 text-[10px] font-mono rounded border transition-colors ${viewMode === '2d' ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400' : 'bg-black/40 border-white/10 text-gray-500'}`}
                            >
                                2D IMAGE
                            </button>
                        </div>

                        {viewMode === '2d' && (
                            <div className="relative space-y-2">
                                <div className="relative">
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={handleImageUpload}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                                    />
                                    <NeonButton variant="cyan" className="w-full text-[10px]">
                                        <Upload className="w-3 h-3 mr-2" /> UPLOAD IMAGE
                                    </NeonButton>
                                </div>

                                {segments.length > 0 && lastClick && (
                                    <NeonButton
                                        variant="purple"
                                        className="w-full text-[10px] animate-pulse"
                                        onClick={handleGenerate3D}
                                        disabled={isGenerating}
                                    >
                                        {isGenerating ? (
                                            <><Loader2 className="w-3 h-3 mr-2 animate-spin" /> GENERATING...</>
                                        ) : (
                                            <><Box className="w-3 h-3 mr-2" /> GENERATE 3D FROM SELECTION</>
                                        )}
                                    </NeonButton>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="h-px bg-white/10 my-2"></div>

                    {/* Visualization Controls */}
                    {viewMode === '3d' && (
                        <div className="space-y-4">
                            <div className="text-[10px] font-mono text-gray-500 tracking-wider">VISUALIZATION</div>
                            <button
                                onClick={() => setShowWireframe(!showWireframe)}
                                className={`w-full flex items-center justify-between px-3 py-2 rounded border transition-all ${showWireframe ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400' : 'bg-black/40 border-white/5 text-gray-400'}`}
                            >
                                <span className="text-xs font-mono">WIREFRAME</span>
                                <div className={`w-8 h-4 rounded-full relative transition-colors ${showWireframe ? 'bg-cyan-500' : 'bg-gray-700'}`}>
                                    <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform ${showWireframe ? 'left-4.5' : 'left-0.5'}`} style={{ left: showWireframe ? '18px' : '2px' }}></div>
                                </div>
                            </button>

                            <div className="space-y-2">
                                <div className="flex justify-between text-[10px] font-mono text-gray-400">
                                    <span>EXPLODED VIEW</span>
                                    <span>{(explodedAmount * 100).toFixed(0)}%</span>
                                </div>
                                <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.01"
                                    value={explodedAmount}
                                    onChange={(e) => setExplodedAmount(parseFloat(e.target.value))}
                                    className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                                />
                            </div>
                        </div>
                    )}
                </HoloCard>
            </div>

            {/* Viewport */}
            <div className="col-span-7 flex flex-col gap-6 h-full">
                <HoloCard className="flex-1 p-0 overflow-hidden border-cyan-500/30 shadow-[0_0_100px_-30px_rgba(0,243,255,0.15)] relative group">
                    <div className="absolute top-6 left-6 z-10 flex gap-4">
                        <div className="font-mono text-[10px] text-cyan-400 bg-black/80 backdrop-blur px-3 py-1.5 rounded border border-cyan-500/30 flex items-center gap-2 shadow-lg">
                            <MousePointer2 className="w-3 h-3" /> {activeTool.toUpperCase()} MODE
                        </div>
                    </div>

                    {viewMode === '3d' ? (
                        <MeshViewer
                            meshUrl={meshUrl}
                            onSegment={handleMeshClick}
                            markers={segments.filter(s => s.visible).map(s => ({ position: [0, 0, 0], color: s.color }))}
                            showWireframe={showWireframe}
                            explodedAmount={explodedAmount}
                        />
                    ) : (
                        imageUrl ? (
                            <ImageViewer
                                imageUrl={imageUrl}
                                onSegment={(point, clickType) => {
                                    setLastClick(point);
                                    // Adapt 2D point to 3D point signature for now, or update prop
                                    // We'll pass z=0
                                    onSegment([point[0], point[1], 0], 'point', clickType);
                                }}
                                markers={segments.filter(s => s.visible).map(s => ({ position: [0, 0], color: s.color }))}
                            />
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-white/20 font-mono text-xs gap-4">
                                <Upload className="w-12 h-12 opacity-20" />
                                <span>UPLOAD AN IMAGE TO START 2D SEGMENTATION</span>
                            </div>
                        )
                    )}
                </HoloCard>
            </div>

            {/* Segments Panel */}
            <div className="col-span-3 h-full flex flex-col gap-4">
                <HoloCard title="Segments" className="flex-1">
                    <div className="space-y-2 overflow-y-auto h-full pr-2 custom-scrollbar">
                        {segments.length === 0 && (
                            <div className="text-center text-white/20 font-mono text-xs py-10">
                                NO SEGMENTS
                            </div>
                        )}
                        {segments.map((seg) => (
                            <div key={seg.id} className="flex items-center justify-between bg-white/5 border border-white/5 rounded p-2 group hover:border-cyan-500/30 transition-colors">
                                <div className="flex items-center gap-3">
                                    <div className="w-3 h-3 rounded-full shadow-[0_0_10px_rgba(0,0,0,0.5)]" style={{ backgroundColor: seg.color }}></div>
                                    <span className="font-mono text-xs text-gray-300">Segment #{seg.id}</span>
                                </div>
                                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button onClick={() => onToggleVisibility(seg.id)} className="p-1 hover:text-cyan-400 text-gray-500 transition-colors">
                                        {seg.visible ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                                    </button>
                                    <button onClick={() => onDeleteSegment(seg.id)} className="p-1 hover:text-red-400 text-gray-500 transition-colors">
                                        <Trash2 className="w-3 h-3" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </HoloCard>

                {/* Pipeline Actions */}
                <HoloCard className="h-auto p-4">
                    <div className="flex flex-col gap-3">
                        <div className="text-[10px] font-mono text-gray-500 tracking-wider mb-1">PIPELINE ACTIONS</div>
                        <NeonButton variant="purple" className="w-full text-[10px]" onClick={() => console.log("Exporting segments...")}>
                            EXPORT SELECTED (.OBJ)
                        </NeonButton>
                        <NeonButton variant="cyan" className="w-full text-[10px]" onClick={() => console.log("Sending to Maya...")}>
                            SEND TO MAYA BRIDGE
                        </NeonButton>
                    </div>
                </HoloCard>
            </div>
        </div>
    );
}

function ToolButton({ icon: Icon, label, active, onClick }: { icon: any, label: string, active: boolean, onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg border transition-all ${active ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400 shadow-[0_0_15px_-5px_rgba(0,243,255,0.3)]' : 'bg-black/40 border-white/5 text-gray-400 hover:bg-white/5 hover:border-white/10'}`}
        >
            <Icon className="w-4 h-4" />
            <span className="font-mono text-xs tracking-wider">{label}</span>
        </button>
    );
}
