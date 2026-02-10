"use client";
import React, { useState } from 'react';
import { Activity, Layers, Command, Hexagon, Database, Sparkles, LayoutTemplate, BrainCircuit, RefreshCw, Cpu, Globe } from 'lucide-react';
import { NeonButton } from './components/ui/NeonButton';
import HoloCard from './components/HoloCard';
import JobSubmitter from './components/JobSubmitter';
import MeshViewer from './components/MeshViewer';
import ArtifactViewer from './components/ArtifactViewer';
import GeometryDNA from './components/GeometryDNA';
import PipelineProgress from './components/PipelineProgress';
import SystemTerminal from './components/SystemTerminal';
import VoiceCommandModule from './components/VoiceCommandModule';
import AnalyticsPanel from './components/AnalyticsPanel';
import LoginPage from './components/LoginPage';
import NeuralCommandInterface from './components/NeuralCommandInterface';
import AutodeskValidationTool from './components/AutodeskValidationTool';
import Sam3DWorkspace from './components/Sam3DWorkspace';
import FloorPlanWorkspace from './components/FloorPlanWorkspace';
import Industry50Dashboard from './components/Industry50Dashboard';
import { useNeuralLink } from './hooks/useNeuralLink';

export default function Home() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [showAnalytics, setShowAnalytics] = useState(false);
    const [artifacts, setArtifacts] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const { messages } = useNeuralLink();

    const [activeTab, setActiveTab] = useState<'create' | 'inspect' | 'sam3d' | 'floorplan' | 'library' | 'system' | 'neural' | 'validate' | 'uv' | 'remesh' | 'material' | 'industry5'>('create');
    const [segmentationMode, setSegmentationMode] = useState(false);
    const [segmentationMarkers, setSegmentationMarkers] = useState<Array<{ position: [number, number, number], color: string }>>([]);
    const [sam3dSegments, setSam3dSegments] = useState<Array<{ id: number, color: string, visible: boolean }>>([]);

    const handleVoiceCommand = (command: string) => {
        console.log("VOICE:", command);
        if (command.includes("OPEN ANALYTICS") || command.includes("SHOW STATS")) {
            setShowAnalytics(true);
        } else if (command.includes("CLOSE ANALYTICS") || command.includes("HIDE STATS")) {
            setShowAnalytics(false);
        } else if (command.includes("RUN DIAGNOSTICS") || command.includes("VALIDATE")) {
            executePipeline({ prompt: "diagnostic_run" });
        } else if (command.includes("SYSTEM STATUS")) {
            console.log("SYSTEM STATUS: OPERATIONAL");
        } else if (command.includes("CREATE MODE")) {
            setActiveTab('create');
        } else if (command.includes("INSPECT MODE")) {
            setActiveTab('inspect');
        } else if (command.includes("NEURAL MODE")) {
            setActiveTab('neural');
        }
    };

    const executePipeline = async (settings: any, file?: File) => {
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append("settings", JSON.stringify(settings));
            if (file) formData.append("file", file);

            const endpoint = file ? 'http://localhost:8000/execute-visual' : 'http://localhost:8000/execute';

            // Modular Execution Logic
            let tasks = ["generative"]; // Default for Create tab

            // If we are in other tabs, we might want different tasks, but executePipeline is primarily for the Create tab.
            // For other tabs, we will likely call specific endpoints or execute with different task lists.
            if (settings.prompt === "validate_only") tasks = ["validate"];
            if (settings.prompt === "uv_only") tasks = ["uv"];
            if (settings.prompt === "remesh_only") tasks = ["remesh"];
            if (settings.prompt === "material_only") tasks = ["material"];

            // Chained Workflow: Use generated mesh if available
            const cleanMeshPath = artifacts?.generative3DOutput?.generated_mesh_path
                ? (artifacts.generative3DOutput.generated_mesh_path.startsWith("backend/data")
                    ? artifacts.generative3DOutput.generated_mesh_path
                    : artifacts.generative3DOutput.generated_mesh_path /* assume full path if not relative */)
                : "backend/data/sample_cube.obj"; // Fallback

            const body = file ? formData : JSON.stringify({
                meshes: [cleanMeshPath],
                materials: [],
                tasks: tasks,
                generative_settings: {
                    prompt: settings.prompt,
                    quality: settings.quality || 'draft'
                },
                remesh_settings: { target_faces: settings.targetFaces || 5000 },
                uv_settings: settings.uv || { mode: "auto" },
                material_settings: settings.material || { profile: "unreal" },
                export_settings: settings.export || { format: "glb" },
                validation_profile: "GENERIC"
            });
            const headers = file ? { "x-qyntara-key": "QYNTARA-X-777" } : { "Content-Type": "application/json", "x-qyntara-key": "QYNTARA-X-777" };

            const res = await fetch(endpoint, {
                method: 'POST',
                headers: headers as any,
                body: body as any
            });
            const result = await res.json();
            setArtifacts(result);
            // Auto-switch to inspect mode on success only for generative tasks
            if (result.status === 'success' && tasks.includes("generative")) {
                setActiveTab('inspect');
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleSegmentation = async (point: [number, number, number]) => {
        if (!segmentationMode || !artifacts?.generative3DOutput?.generated_mesh_path) return;

        console.log("Segmenting at:", point);

        try {
            const res = await fetch('http://localhost:8000/segment-3d', {
                method: 'POST',
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    mesh_path: artifacts.generative3DOutput.generated_mesh_path,
                    click_point: point,
                    camera_view: [0, 0, 4] // Mock camera view
                })
            });
            const result = await res.json();
            console.log("Segmentation Result:", result);

            if (result.status === 'success') {
                setSegmentationMarkers(prev => [...prev, { position: point, color: result.color || '#00ff00' }]);
            }
        } catch (e) {
            console.error("Segmentation failed:", e);
        }
    };

    if (!isAuthenticated) return <LoginPage onLogin={(k) => k === "QYNTARA-X-777" && setIsAuthenticated(true)} />;

    return (
        <main className="flex min-h-screen bg-void text-foreground overflow-hidden relative selection:bg-cyan-500/30 font-sans">
            {/* Dynamic Background */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-surface-highlight via-void to-void opacity-80 pointer-events-none"></div>
            <div className="absolute inset-0 bg-grid-pattern bg-[length:60px_60px] opacity-[0.05] pointer-events-none perspective-grid origin-top animate-[pulse-slow_8s_infinite]"></div>
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent animate-pulse pointer-events-none"></div>
            <div className="scanline-overlay pointer-events-none"></div>

            {/* Sidebar (Parent Tabs) */}
            <aside className="w-20 border-r border-white/5 bg-surface/30 backdrop-blur-xl flex flex-col items-center py-6 z-20 gap-6 relative">
                <div className="absolute inset-y-0 right-0 w-[1px] bg-gradient-to-b from-transparent via-cyan-500/20 to-transparent"></div>
                <div className="w-10 h-10 bg-gradient-to-br from-cyan-500/20 to-purple-600/20 rounded-lg border border-white/10 flex items-center justify-center shadow-[0_0_20px_-5px_rgba(0,243,255,0.2)] group cursor-pointer hover:scale-105 transition-transform" onClick={() => setActiveTab('create')}>
                    <Hexagon className="w-5 h-5 text-cyan-400 group-hover:rotate-180 transition-transform duration-700" />
                </div>

                <div className="flex flex-col gap-4 w-full px-3 mt-auto mb-auto overflow-y-auto custom-scrollbar">
                    <SidebarTab icon={Activity} label="CREATE" active={activeTab === 'create'} onClick={() => setActiveTab('create')} />

                    <div className="h-[1px] bg-white/10 w-full my-2"></div>

                    <SidebarTab icon={Layers} label="INSPECT" active={activeTab === 'inspect'} onClick={() => setActiveTab('inspect')} />
                    <SidebarTab icon={Globe} label="INDUSTRY 5.0" active={activeTab === 'industry5'} onClick={() => setActiveTab('industry5')} />
                    <SidebarTab icon={Sparkles} label="SAM 3D" active={activeTab === 'sam3d'} onClick={() => setActiveTab('sam3d')} />
                    <SidebarTab icon={LayoutTemplate} label="FLOOR PLAN" active={activeTab === 'floorplan'} onClick={() => setActiveTab('floorplan')} />

                    <div className="h-[1px] bg-white/10 w-full my-2"></div>

                    <SidebarTab icon={Cpu} label="VALIDATE" active={activeTab === 'validate'} onClick={() => setActiveTab('validate')} />
                    <SidebarTab icon={LayoutTemplate} label="UV" active={activeTab === 'uv'} onClick={() => setActiveTab('uv')} />
                    <SidebarTab icon={Hexagon} label="REMESH" active={activeTab === 'remesh'} onClick={() => setActiveTab('remesh')} />
                    <SidebarTab icon={Layers} label="MATERIAL" active={activeTab === 'material'} onClick={() => setActiveTab('material')} />

                    <div className="h-[1px] bg-white/10 w-full my-2"></div>

                    <SidebarTab icon={BrainCircuit} label="NEURAL" active={activeTab === 'neural'} onClick={() => setActiveTab('neural')} />
                    <SidebarTab icon={Database} label="LIBRARY" active={activeTab === 'library'} onClick={() => setActiveTab('library')} />
                    <SidebarTab icon={Command} label="SYSTEM" active={activeTab === 'system'} onClick={() => setActiveTab('system')} />
                </div>
                <div className="text-[9px] font-mono text-white/20 vertical-text tracking-widest opacity-50">V.2.0.45</div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col relative z-10 h-screen overflow-hidden">
                {/* Header */}
                <header className="h-20 flex-shrink-0 flex items-center justify-between px-8 z-50 relative border-b border-white/5 bg-black/20 backdrop-blur-sm">
                    <div className="flex items-center gap-4 group">
                        <div className="relative">
                            <div className="absolute inset-0 bg-cyan-500/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                            <img src="/logo_new.png" alt="Qyntara Logo" className="h-12 w-auto object-contain relative z-10" />
                        </div>
                        <div className="h-8 w-[1px] bg-white/10 mx-2"></div>
                        <div className="font-mono text-sm tracking-widest text-cyan-400">
                            {activeTab === 'create' && "GENERATIVE STUDIO"}
                            {activeTab === 'neural' && "NEURAL COMMAND CENTER"}
                            {activeTab === 'inspect' && "INSPECTOR MODULE"}
                            {activeTab === 'library' && "ARTIFACT LIBRARY"}
                            {activeTab === 'system' && "SYSTEM TERMINAL"}
                            {activeTab === 'validate' && "GEOMETRY VALIDATOR"}
                            {activeTab === 'uv' && "UV UNWRAPPER"}
                            {activeTab === 'remesh' && "TOPOLOGY OPTIMIZER"}
                            {activeTab === 'remesh' && "TOPOLOGY OPTIMIZER"}
                            {activeTab === 'material' && "MATERIAL SYNTHESIZER"}
                            {activeTab === 'industry5' && "INDUSTRY 5.0 COMMAND CENTER"}
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="flex flex-col items-end">
                            <div className="font-mono text-[9px] text-gray-500 mb-1 tracking-wider">SYSTEM STATUS</div>
                            <div className="flex items-center gap-2 font-mono text-[10px] text-cyan-400 bg-cyan-950/30 px-3 py-1.5 rounded border border-cyan-500/20 shadow-[0_0_10px_-5px_rgba(0,243,255,0.3)]">
                                <Activity className="w-3 h-3 animate-pulse" />
                                OPERATIONAL
                            </div>
                        </div>
                        <NeonButton variant="cyan" onClick={() => setShowAnalytics(true)} className="h-9 px-4 text-[10px] tracking-wider">
                            LAUNCH ANALYTICS
                        </NeonButton>
                    </div>
                </header>

                {/* Tab Content Views */}
                <div className="flex-1 overflow-hidden relative p-8">

                    {/* CREATE VIEW */}
                    {activeTab === 'create' && (
                        <div className="h-full flex items-center justify-center max-w-4xl mx-auto animate-in fade-in zoom-in duration-300">
                            <HoloCard title="Generative Studio" className="w-full h-[600px]">
                                <JobSubmitter onSubmit={executePipeline} loading={loading} />
                            </HoloCard>
                        </div>
                    )}

                    {/* NEURAL VIEW */}
                    {activeTab === 'neural' && (
                        <div className="h-full max-w-5xl mx-auto animate-in fade-in zoom-in duration-300">
                            <NeuralCommandInterface />
                        </div>
                    )}

                    {/* INSPECT VIEW */}
                    {activeTab === 'inspect' && (
                        <div className="h-full grid grid-cols-12 gap-6 animate-in fade-in slide-in-from-right-10 duration-300">
                            <div className="col-span-8 flex flex-col gap-6 h-full">
                                <HoloCard className="flex-1 p-0 overflow-hidden border-cyan-500/30 shadow-[0_0_100px_-30px_rgba(0,243,255,0.15)] relative group">
                                    <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
                                    <div className="absolute top-6 left-6 z-10 flex gap-4">
                                        <div className="font-mono text-[10px] text-cyan-400 bg-black/80 backdrop-blur px-3 py-1.5 rounded border border-cyan-500/30 flex items-center gap-2 shadow-lg">
                                            <Activity className="w-3 h-3" /> LIVE VIEWPORT
                                        </div>
                                        <button
                                            onClick={() => setSegmentationMode(!segmentationMode)}
                                            className={`font-mono text-[10px] px-3 py-1.5 rounded border transition-all flex items-center gap-2 ${segmentationMode ? 'bg-purple-500/20 text-purple-400 border-purple-500/50 shadow-[0_0_10px_rgba(188,19,254,0.3)]' : 'bg-black/80 text-gray-400 border-white/10 hover:border-white/30'}`}
                                        >
                                            <Sparkles className="w-3 h-3" /> {segmentationMode ? 'SEGMENTATION ACTIVE' : 'ENABLE SEGMENTATION'}
                                        </button>
                                    </div>
                                    <MeshViewer
                                        meshUrl={artifacts?.generative3DOutput?.generated_mesh_path ? `http://localhost:8000/static/${artifacts.generative3DOutput.generated_mesh_path.split('/').pop()}` : "http://localhost:8000/static/sample_cube.obj"}
                                        onSegment={segmentationMode ? handleSegmentation : undefined}
                                        markers={segmentationMarkers}
                                    />
                                </HoloCard>
                                <HoloCard title="Neural Logs" className="h-48 flex-shrink-0">
                                    <PipelineProgress messages={messages} />
                                </HoloCard>
                            </div>
                            <div className="col-span-4 h-full">
                                <HoloCard title="Artifacts" className="h-full">
                                    {artifacts ? (
                                        <div className="space-y-4 h-full overflow-y-auto pr-2 custom-scrollbar">
                                            {artifacts.segmentation && artifacts.segmentation.detected_objects && (
                                                <ArtifactViewer title="Visual Analysis" data={artifacts.segmentation} />
                                            )}
                                            <GeometryDNA data={artifacts.generative3DOutput} />
                                            <ArtifactViewer title="Validation Report" data={artifacts.validationReport} />
                                            <AutodeskValidationTool data={artifacts.autodeskValidation} />
                                        </div>
                                    ) : (
                                        <div className="h-full flex flex-col items-center justify-center text-white/20 font-mono text-xs gap-4">
                                            <Database className="w-12 h-12 opacity-20 animate-pulse" />
                                            <span>AWAITING INPUT DATA...</span>
                                        </div>
                                    )}
                                </HoloCard>
                            </div>
                        </div>
                    )}

                    {/* SAM 3D VIEW */}
                    {activeTab === 'sam3d' && (
                        <Sam3DWorkspace
                            meshUrl={artifacts?.generative3DOutput?.generated_mesh_path ? `http://localhost:8000/static/${artifacts.generative3DOutput.generated_mesh_path.split('/').pop()}` : "http://localhost:8000/static/sample_cube.obj"}
                            onSegment={async (point, type, clickType) => {
                                console.log("SAM 3D Segment:", point, type, clickType);
                                // Reuse the existing segmentation handler for now, but adapt it
                                await handleSegmentation(point);
                                // Determine color based on click type (Left=Green/Positive, Right=Red/Negative)
                                const color = clickType === 'right' ? '#ff0000' : '#00ff00';
                                setSam3dSegments(prev => [...prev, { id: prev.length + 1, color: color, visible: true }]);
                            }}
                            segments={sam3dSegments}
                            onToggleVisibility={(id) => setSam3dSegments(prev => prev.map(s => s.id === id ? { ...s, visible: !s.visible } : s))}
                            onDeleteSegment={(id) => setSam3dSegments(prev => prev.filter(s => s.id !== id))}
                            onMeshGenerated={(url) => {
                                console.log("New Mesh Generated:", url);
                                // Update artifacts to reflect the new mesh
                                setArtifacts(prev => ({
                                    ...prev,
                                    generative3DOutput: {
                                        ...prev?.generative3DOutput,
                                        generated_mesh_path: url.split('/').pop() || "gen_model.obj",
                                        neural_enhancement_applied: true
                                    }
                                }));
                            }}
                        />
                    )}

                    {/* FLOOR PLAN VIEW */}
                    {activeTab === 'floorplan' && (
                        <FloorPlanWorkspace />
                    )}

                    {/* LIBRARY VIEW */}
                    {activeTab === 'library' && (
                        <div className="h-full max-w-6xl mx-auto animate-in fade-in zoom-in duration-300 flex flex-col gap-6">
                            <div className="flex justify-between items-center">
                                <h2 className="text-xl font-display text-cyan-400">ARTIFACT LIBRARY</h2>
                                <NeonButton variant="cyan" onClick={() => setActiveTab('library')} className="text-xs">
                                    <RefreshCw className="w-3 h-3 mr-2" /> REFRESH
                                </NeonButton>
                            </div>

                            <LibraryGrid />
                        </div>
                    )}

                    {/* SYSTEM VIEW */}
                    {activeTab === 'system' && (
                        <div className="h-full max-w-5xl mx-auto animate-in fade-in zoom-in duration-300">
                            <HoloCard title="System Terminal" className="h-full">
                                <SystemTerminal logs={messages} />
                            </HoloCard>
                        </div>
                    )}

                    {/* Modular Tabs Placeholders */}
                    {activeTab === 'validate' && (
                        <div className="h-full flex items-center justify-center flex-col gap-4">
                            <Cpu className="w-16 h-16 text-cyan-500 opacity-50" />
                            <h2 className="text-xl font-bold tracking-widest text-cyan-400">GEOMETRY VALIDATION</h2>
                            <p className="text-gray-500 max-w-md text-center">Run advanced geometry checks to ensure manifold, watertight meshes.</p>
                            <NeonButton variant="cyan" onClick={() => executePipeline({ prompt: "validate_only" })}>RUN VALIDATION</NeonButton>
                        </div>
                    )}
                    {activeTab === 'uv' && (
                        <div className="h-full flex items-center justify-center flex-col gap-4">
                            <LayoutTemplate className="w-16 h-16 text-purple-500 opacity-50" />
                            <h2 className="text-xl font-bold tracking-widest text-purple-400">UV UNWRAPPING</h2>
                            <p className="text-gray-500 max-w-md text-center">Generate optimized UV maps with minimal distortion and high packing efficiency.</p>
                            <NeonButton variant="purple" onClick={() => executePipeline({ prompt: "uv_only" })}>GENERATE UVs</NeonButton>
                        </div>
                    )}
                    {activeTab === 'remesh' && (
                        <div className="h-full flex items-center justify-center flex-col gap-4">
                            <Hexagon className="w-16 h-16 text-cyan-500 opacity-50" />
                            <h2 className="text-xl font-bold tracking-widest text-cyan-400">QUAD REMESHING</h2>
                            <p className="text-gray-500 max-w-md text-center">Convert complex topology into clean, animation-ready quads.</p>
                            <NeonButton variant="cyan" onClick={() => executePipeline({ prompt: "remesh_only", targetFaces: 5000 })}>START REMESHING</NeonButton>
                        </div>
                    )}
                    {activeTab === 'material' && (
                        <div className="h-full flex items-center justify-center flex-col gap-4">
                            <Layers className="w-16 h-16 text-purple-500 opacity-50" />
                            <h2 className="text-xl font-bold tracking-widest text-purple-400">MATERIAL SYNTHESIS</h2>
                            <p className="text-gray-500 max-w-md text-center">AI-driven material assignment and texture generation.</p>
                            <NeonButton variant="purple" onClick={() => executePipeline({ prompt: "material_only" })}>ASSIGN MATERIALS</NeonButton>
                        </div>
                    )}

                    {/* INDUSTRY 5.0 VIEW */}
                    {activeTab === 'industry5' && (
                        <Industry50Dashboard />
                    )}

                </div>
            </div>
            <VoiceCommandModule onCommand={handleVoiceCommand} />
            {showAnalytics && <AnalyticsPanel onClose={() => setShowAnalytics(false)} />}
        </main>
    );
}

function SidebarTab({ icon: Icon, label, active, onClick }: { icon: any, label: string, active: boolean, onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={`w-full aspect-square rounded-lg border transition-all flex items-center justify-center group relative overflow-hidden ${active ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-400 shadow-[0_0_15px_-5px_rgba(0,243,255,0.3)]' : 'border-white/5 hover:border-cyan-500/30 hover:bg-cyan-500/5 text-gray-500 hover:text-cyan-300'}`}
        >
            <div className={`absolute inset-0 bg-cyan-400/5 transition-transform duration-300 ${active ? 'translate-y-0' : 'translate-y-full group-hover:translate-y-0'}`}></div>
            <Icon className={`w-5 h-5 relative z-10 transition-transform ${active ? 'scale-110' : 'group-hover:scale-110'}`} />

            {/* Tooltip */}
            <div className="absolute left-full ml-4 px-2 py-1 bg-black/90 border border-white/10 rounded text-[10px] font-mono text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                {label}
            </div>
        </button>
    );
}

function LibraryGrid() {
    const [files, setFiles] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    React.useEffect(() => {
        fetch('http://localhost:8000/library')
            .then(res => res.json())
            .then(data => {
                setFiles(data.files);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="text-center text-cyan-500 animate-pulse font-mono">LOADING ARCHIVES...</div>;

    if (files.length === 0) return (
        <div className="h-64 flex flex-col items-center justify-center text-white/20 font-mono text-xs gap-4 border border-white/5 rounded-lg bg-white/5">
            <Database className="w-12 h-12 opacity-20" />
            <span>NO ARTIFACTS FOUND</span>
        </div>
    );

    return (
        <div className="grid grid-cols-4 gap-4 overflow-y-auto pr-2 custom-scrollbar h-[600px]">
            {files.map((file, i) => (
                <HoloCard key={i} className="h-auto p-4 flex flex-col gap-3 group hover:border-cyan-500/50 transition-colors">
                    <div className="aspect-square bg-black/50 rounded flex items-center justify-center relative overflow-hidden">
                        {file.type === 'png' || file.type === 'jpg' ? (
                            <img src={file.url} alt={file.name} className="w-full h-full object-cover" />
                        ) : (
                            <Hexagon className="w-12 h-12 text-cyan-500/30 group-hover:text-cyan-400 transition-colors" />
                        )}
                        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 backdrop-blur-sm">
                            <a href={file.url} download>
                                <NeonButton variant="cyan" className="text-[10px] h-8 px-3">DOWNLOAD</NeonButton>
                            </a>
                        </div>
                    </div>
                    <div className="flex flex-col gap-1">
                        <div className="text-xs font-mono text-cyan-400 truncate" title={file.name}>{file.name}</div>
                        <div className="flex justify-between text-[10px] text-gray-500 font-mono">
                            <span>{file.type.toUpperCase()}</span>
                            <span>{(file.size / 1024).toFixed(1)} KB</span>
                        </div>
                    </div>
                </HoloCard>
            ))}
        </div>
    );
}
