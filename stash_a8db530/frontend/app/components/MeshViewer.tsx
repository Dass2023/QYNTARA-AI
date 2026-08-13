"use client";
import React, { Suspense, useState, useMemo } from 'react';
import { Canvas, useLoader } from '@react-three/fiber';
import { OrbitControls, Stage, Html, TransformControls, Grid, Environment, Center } from '@react-three/drei';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import * as THREE from 'three';

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean }> {
    constructor(props: any) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: any) {
        return { hasError: true };
    }

    componentDidCatch(error: any, errorInfo: any) {
        console.error("MeshViewer Error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="flex items-center justify-center w-full h-full text-red-500 bg-black/80">
                    <div className="text-center">
                        <h3 className="text-xl font-bold">3D View Error</h3>
                        <p className="text-sm">WebGL Context Lost or Mesh Load Failed.</p>
                        <button onClick={() => window.location.reload()} className="px-4 py-2 mt-4 text-black bg-white rounded hover:bg-gray-200">
                            Reload Viewer
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

// Extracted Mesh component to avoid nesting and syntax issues
const MeshScene = ({ url, transformMode, onSegment, markers, showWireframe, explodedAmount, setStats }: any) => {
    // Determine loader based on extension
    const isGLB = url.toLowerCase().endsWith('.glb') || url.toLowerCase().endsWith('.gltf');

    // Load Mesh
    let obj: THREE.Group | null = null;
    if (isGLB) {
        const gltf = useLoader(GLTFLoader, url) as any;
        obj = gltf.scene;
    } else {
        obj = useLoader(OBJLoader, url) as THREE.Group;
    }

    const { mesh, wireframe } = useMemo(() => {
        if (!obj) return { mesh: null, wireframe: null };

        let geometry: THREE.BufferGeometry | null = null;

        // Find first valid geometry
        obj.traverse((child: any) => {
            if (geometry) return;
            if (child.isMesh && child.geometry) {
                geometry = child.geometry.clone();
            }
        });

        if (!geometry) {
            return { mesh: null, wireframe: null };
        }

        // 1. Center Geometry
        (geometry as THREE.BufferGeometry).computeBoundingBox();
        const box = (geometry as THREE.BufferGeometry).boundingBox!;
        const center = box.getCenter(new THREE.Vector3());
        (geometry as THREE.BufferGeometry).translate(-center.x, -center.y, -center.z);

        // 2. Scale Geometry
        (geometry as THREE.BufferGeometry).computeBoundingBox(); // Recompute
        const size = (geometry as THREE.BufferGeometry).boundingBox!.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = maxDim > 0 ? 4 / maxDim : 1;
        (geometry as THREE.BufferGeometry).scale(scale, scale, scale);

        // Stats
        if (setStats) {
            setStats({
                tris: Math.round((geometry as THREE.BufferGeometry).index ? (geometry as THREE.BufferGeometry).index!.count / 3 : (geometry as THREE.BufferGeometry).attributes.position.count / 3),
                verts: (geometry as THREE.BufferGeometry).attributes.position.count
            });
        }

        // Create Mesh
        const material = new THREE.MeshStandardMaterial({
            color: 0xff00ff, // Hot Pink
            roughness: 0.3,
            metalness: 0.8,
            side: THREE.DoubleSide
        });

        const m = new THREE.Mesh(geometry, material);
        m.castShadow = true;
        m.receiveShadow = true;
        m.frustumCulled = false; // IMPORTANT: Disable culling to prevent visibility issues

        // Wireframe
        let w = null;
        if (showWireframe) {
            const wMat = new THREE.MeshBasicMaterial({ color: 0x00ffff, wireframe: true, transparent: true, opacity: 0.2 });
            w = new THREE.Mesh(geometry, wMat);
            w.frustumCulled = false;
        }

        return { mesh: m, wireframe: w };
    }, [obj, showWireframe, setStats]);

    if (!mesh) return null;

    return (
        <group>
            <TransformControls mode={transformMode}>
                <primitive
                    object={mesh}
                    onClick={(e: any) => {
                        e.stopPropagation();
                        if (onSegment) onSegment([e.point.x, e.point.y, e.point.z], 'point', 'left');
                    }}
                />
            </TransformControls>
            {wireframe && <primitive object={wireframe} />}

            {markers.map((marker: any, i: number) => {
                const pos = new THREE.Vector3(...marker.position);
                const dir = pos.clone().normalize();
                const explodedPos = pos.add(dir.multiplyScalar(explodedAmount * 2));

                return (
                    <mesh key={i} position={[explodedPos.x, explodedPos.y, explodedPos.z]}>
                        <sphereGeometry args={[0.05, 16, 16]} />
                        <meshStandardMaterial color={marker.color} emissive={marker.color} emissiveIntensity={0.5} />
                    </mesh>
                );
            })}
        </group>
    );
};

export default function MeshViewer({ meshUrl, onSegment, markers = [], showWireframe = false, explodedAmount = 0 }: { meshUrl: string, onSegment?: (point: [number, number, number], type: 'point' | 'box' | 'text', clickType?: 'left' | 'right') => void, markers?: Array<{ position: [number, number, number], color: string }>, showWireframe?: boolean, explodedAmount?: number }) {
    const [currentMeshUrl, setCurrentMeshUrl] = useState(meshUrl);
    const [transformMode, setTransformMode] = useState<'translate' | 'rotate' | 'scale'>('translate');
    const [stats, setStats] = useState({ tris: 0, verts: 0 });
    const [exportFormat, setExportFormat] = useState<'OBJ' | 'GLB' | 'USD'>('OBJ');
    const [exportEngine, setExportEngine] = useState<'Unreal' | 'Unity'>('Unreal');
    const [exportPath, setExportPath] = useState('C:/Qyntara/Exports/');
    const [isExporting, setIsExporting] = useState(false);
    const [manualScale, setManualScale] = useState(1);

    // Update currentMeshUrl when prop changes
    React.useEffect(() => {
        setCurrentMeshUrl(meshUrl);
    }, [meshUrl]);

    const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            const url = URL.createObjectURL(file);
            setCurrentMeshUrl(url);
            console.log("Imported mesh:", file.name, url);
        }
    };

    const handleExport = async () => {
        setIsExporting(true);
        try {
            const res = await fetch('http://localhost:8000/export-mesh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_path: currentMeshUrl.split('/').pop() || "model.obj",
                    target_path: exportPath,
                    format: exportFormat,
                    engine: exportEngine
                })
            });
            const result = await res.json();
            if (result.status === 'success') {
                alert(`Export Successful!\nSaved to: ${result.path}`);
            } else {
                alert(`Export Failed: ${result.message || result.detail}`);
            }
        } catch (e) {
            console.error("Export error:", e);
            alert("Export failed. Check console for details.");
        } finally {
            setIsExporting(false);
        }
    };

    return (
        <div className="w-full h-full bg-black/90 relative overflow-hidden group">
            {/* HUD Overlay */}
            <div className="absolute top-4 left-4 z-10 pointer-events-none">
                <div className="bg-black/60 backdrop-blur-md border border-cyan-500/30 p-3 rounded-lg text-cyan-400 font-mono text-xs mb-2">
                    <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        <span className="font-bold tracking-wider">VIEWPORT.ACTIVE</span>
                    </div>
                    <div className="space-y-1 opacity-80">
                        <div>TRIS:  {stats.tris.toLocaleString()}</div>
                        <div>VERTS: {stats.verts.toLocaleString()}</div>
                        <div>FPS:   60.0</div>
                    </div>
                </div>

                {/* Import Button */}
                <div className="pointer-events-auto mb-2">
                    <label className="cursor-pointer bg-cyan-900/50 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 px-3 py-2 rounded flex items-center gap-2 transition-all">
                        <span className="font-bold">IMPORT MESH</span>
                        <input type="file" accept=".obj" className="hidden" onChange={handleImport} />
                    </label>
                </div>

                {/* Scale Control */}
                <div className="pointer-events-auto bg-black/60 backdrop-blur-md border border-cyan-500/30 p-3 rounded-lg text-cyan-400 font-mono text-xs">
                    <div className="mb-1 font-bold">SCALE: {manualScale.toFixed(2)}x</div>
                    <input
                        type="range"
                        min="0.1"
                        max="5"
                        step="0.1"
                        value={manualScale}
                        onChange={(e) => setManualScale(parseFloat(e.target.value))}
                        className="w-full accent-cyan-500 cursor-pointer"
                    />
                </div>
            </div>

            {/* Export Panel */}
            <div className="absolute top-4 right-4 z-10 pointer-events-auto">
                <div className="bg-black/80 backdrop-blur-md border border-cyan-500/30 p-4 rounded-lg text-cyan-400 font-mono text-xs w-64 shadow-[0_0_20px_rgba(6,182,212,0.1)]">
                    <h3 className="text-sm font-bold mb-3 border-b border-cyan-500/30 pb-2 flex justify-between items-center">
                        <span>EXPORT MODULE</span>
                        <div className="w-2 h-2 bg-cyan-500 rounded-full" />
                    </h3>

                    <div className="space-y-4">
                        <div className="space-y-1">
                            <label className="text-[10px] uppercase tracking-wider opacity-70">Target Path</label>
                            <input
                                type="text"
                                value={exportPath}
                                onChange={(e) => setExportPath(e.target.value)}
                                className="w-full bg-black/50 border border-cyan-500/20 rounded px-2 py-1 text-cyan-400 focus:outline-none focus:border-cyan-500/50"
                            />
                        </div>

                        <div className="space-y-1">
                            <label className="text-[10px] uppercase tracking-wider opacity-70">Format</label>
                            <div className="flex gap-1 bg-black/50 p-1 rounded border border-cyan-500/20">
                                {['OBJ', 'GLB', 'USD'].map(fmt => (
                                    <button
                                        key={fmt}
                                        onClick={() => setExportFormat(fmt as any)}
                                        className={`flex-1 py-1 rounded text-[10px] font-bold transition-all ${exportFormat === fmt ? 'bg-cyan-500 text-black' : 'hover:bg-cyan-500/20'
                                            }`}
                                    >
                                        {fmt}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-[10px] uppercase tracking-wider opacity-70">Target Engine</label>
                            <div className="flex gap-1 bg-black/50 p-1 rounded border border-cyan-500/20">
                                {['Unreal', 'Unity'].map(eng => (
                                    <button
                                        key={eng}
                                        onClick={() => setExportEngine(eng as any)}
                                        className={`flex-1 py-1 rounded text-[10px] font-bold transition-all ${exportEngine === eng ? 'bg-cyan-500 text-black' : 'hover:bg-cyan-500/20'
                                            }`}
                                    >
                                        {eng}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <button
                            onClick={handleExport}
                            disabled={isExporting}
                            className={`w-full py-2 rounded font-bold text-black transition-all flex items-center justify-center gap-2 ${isExporting ? 'bg-cyan-900 cursor-not-allowed' : 'bg-cyan-500 hover:bg-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.5)]'
                                }`}
                        >
                            {isExporting ? (
                                <>
                                    <div className="w-3 h-3 border-2 border-black border-t-transparent rounded-full animate-spin" />
                                    PROCESSING...
                                </>
                            ) : (
                                'INITIATE EXPORT'
                            )}
                        </button>
                    </div>
                </div>
            </div>

            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 flex gap-2 pointer-events-auto">
                {['translate', 'rotate', 'scale'].map((mode) => (
                    <button
                        key={mode}
                        onClick={() => setTransformMode(mode as any)}
                        className={`px-4 py-2 rounded-md font-bold text-xs uppercase tracking-widest transition-all ${transformMode === mode
                            ? 'bg-cyan-500 text-black shadow-[0_0_15px_rgba(6,182,212,0.5)]'
                            : 'bg-black/60 text-cyan-500 border border-cyan-500/30 hover:bg-cyan-500/20'
                            }`}
                    >
                        {mode}
                    </button>
                ))}
            </div>

            <ErrorBoundary>
                <Canvas shadows camera={{ position: [5, 5, 5], fov: 45 }} gl={{ antialias: false }}>
                    <color attach="background" args={['#222']} />

                    <Suspense fallback={<Html center><div className="text-cyan-500 font-mono text-xl animate-pulse tracking-[0.2em]">INITIALIZING NEURAL LINK...</div></Html>}>
                        <ambientLight intensity={1} />
                        <directionalLight position={[10, 10, 5]} intensity={2} castShadow />



                        <group scale={[manualScale, manualScale, manualScale]}>
                            <MeshScene
                                url={currentMeshUrl}
                                transformMode={transformMode}
                                onSegment={onSegment}
                                markers={markers}
                                showWireframe={showWireframe}
                                explodedAmount={explodedAmount}
                                setStats={setStats}
                            />
                        </group>

                        <Grid
                            infiniteGrid
                            fadeDistance={30}
                            sectionColor="#00ffff"
                            cellColor="#1a1a1a"
                            sectionThickness={1}
                            cellThickness={0.5}
                        />

                        <Environment preset="city" />
                    </Suspense>

                    <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 1.75} />
                </Canvas>
            </ErrorBoundary>
        </div>
    );
}
