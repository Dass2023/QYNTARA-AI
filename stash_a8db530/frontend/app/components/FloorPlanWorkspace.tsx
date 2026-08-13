"use client";
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { HoloCard } from './ui/HoloCard';
import { NeonButton } from './ui/NeonButton';
import MeshViewer from './MeshViewer';
import { Upload, LayoutTemplate, Settings2, RefreshCw } from 'lucide-react';

export default function FloorPlanWorkspace() {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [height, setHeight] = useState(2.5);
    const [threshold, setThreshold] = useState(127);
    const [loading, setLoading] = useState(false);
    const [meshUrl, setMeshUrl] = useState<string | null>(null);
    const [dxfUrl, setDxfUrl] = useState<string | null>(null);

    // Calibration State
    const [isCalibrating, setIsCalibrating] = useState(false);
    const [calibrationPoints, setCalibrationPoints] = useState<Array<{ x: number, y: number }>>([]);
    const [pixelsPerMeter, setPixelsPerMeter] = useState(50); // Default
    const [calibrationLength, setCalibrationLength] = useState(1.0); // Meters

    const onDrop = useCallback((acceptedFiles: File[]) => {
        const f = acceptedFiles[0];
        setFile(f);
        setPreview(URL.createObjectURL(f));
        setCalibrationPoints([]); // Reset calibration
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: { 'image/*': [] } });

    const handleImageClick = (e: React.MouseEvent<HTMLImageElement>) => {
        if (!isCalibrating) return;
        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Scale coordinates to natural image size if needed, but for now let's use displayed pixels 
        // and assume the user calibrates on the displayed image. 
        // Ideally we map this back to the original image resolution.
        // For simplicity in this "TD Level" demo, we'll calculate ratio based on displayed width vs natural width.
        const scaleX = e.currentTarget.naturalWidth / rect.width;
        const scaleY = e.currentTarget.naturalHeight / rect.height;

        const point = { x: x * scaleX, y: y * scaleY };

        if (calibrationPoints.length < 2) {
            setCalibrationPoints(prev => [...prev, point]);
        }
    };

    const finishCalibration = () => {
        if (calibrationPoints.length === 2) {
            const p1 = calibrationPoints[0];
            const p2 = calibrationPoints[1];
            const dist = Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
            const ppm = dist / calibrationLength;
            setPixelsPerMeter(ppm);
            setIsCalibrating(false);
            setCalibrationPoints([]);
            alert(`Calibration Complete: ${ppm.toFixed(2)} pixels/meter`);
        }
    };

    const handleGenerate = async () => {
        if (!file) return;
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('height', height.toString());
            formData.append('threshold', threshold.toString());
            formData.append('pixels_per_meter', pixelsPerMeter.toString());

            const res = await fetch('http://localhost:8000/extrude-floorplan', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (data.status === 'success') {
                setMeshUrl(`http://localhost:8000/static/${data.mesh_path}`);
                setDxfUrl(`http://localhost:8000/static/${data.dxf_path}`);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="h-full grid grid-cols-12 gap-6 animate-in fade-in slide-in-from-right-10 duration-300">
            {/* Left Panel: Upload & Settings */}
            <div className="col-span-4 flex flex-col gap-6">
                <HoloCard title="Input Floor Plan" className="flex-1 flex flex-col relative">
                    <div
                        {...getRootProps()}
                        className={`flex-1 border-2 border-dashed rounded-lg flex flex-col items-center justify-center p-6 transition-colors cursor-pointer relative overflow-hidden ${isDragActive ? 'border-cyan-500 bg-cyan-500/10' : 'border-white/10 hover:border-white/20 hover:bg-white/5'}`}
                        onClick={(e) => isCalibrating ? e.stopPropagation() : getRootProps().onClick(e)}
                    >
                        <input {...getInputProps()} disabled={isCalibrating} />
                        {preview ? (
                            <div className="relative w-full h-full flex items-center justify-center">
                                <img
                                    src={preview}
                                    alt="Preview"
                                    className={`max-h-64 object-contain ${isCalibrating ? 'cursor-crosshair' : ''}`}
                                    onClick={handleImageClick}
                                />
                                {/* Draw Calibration Line */}
                                {calibrationPoints.map((p, i) => (
                                    // Note: These points are in natural image coordinates, mapping back to display is hard without ref.
                                    // For this demo, we won't visualize the dots on the scaled image perfectly to avoid complex React ref logic.
                                    // Instead, we rely on the user clicking.
                                    null
                                ))}
                            </div>
                        ) : (
                            <div className="text-center text-gray-500">
                                <Upload className="w-10 h-10 mx-auto mb-2 opacity-50" />
                                <p className="font-mono text-xs">DRAG & DROP OR CLICK TO UPLOAD</p>
                            </div>
                        )}
                    </div>

                    {/* Calibration Controls Overlay */}
                    {preview && (
                        <div className="absolute bottom-4 right-4 flex gap-2">
                            {!isCalibrating ? (
                                <button
                                    onClick={(e) => { e.stopPropagation(); setIsCalibrating(true); setCalibrationPoints([]); }}
                                    className="bg-black/80 backdrop-blur border border-white/20 text-xs font-mono px-3 py-1.5 rounded hover:bg-cyan-500/20 hover:text-cyan-400 transition-colors"
                                >
                                    CALIBRATE SCALE
                                </button>
                            ) : (
                                <div className="flex flex-col gap-2 bg-black/90 p-3 rounded border border-cyan-500/50 shadow-lg">
                                    <div className="text-[10px] text-cyan-400 font-mono">CLICK 2 POINTS ON IMAGE</div>
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="number"
                                            value={calibrationLength}
                                            onChange={(e) => setCalibrationLength(parseFloat(e.target.value))}
                                            className="w-16 bg-white/10 border border-white/20 rounded px-2 py-1 text-xs text-white"
                                        />
                                        <span className="text-xs text-gray-400">meters</span>
                                    </div>
                                    <div className="flex gap-2">
                                        <button onClick={finishCalibration} disabled={calibrationPoints.length !== 2} className="flex-1 bg-cyan-500/20 text-cyan-400 text-xs py-1 rounded border border-cyan-500/50 disabled:opacity-50">SET</button>
                                        <button onClick={() => setIsCalibrating(false)} className="flex-1 bg-red-500/20 text-red-400 text-xs py-1 rounded border border-red-500/50">CANCEL</button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </HoloCard>

                <HoloCard title="Extrusion Settings" className="h-auto">
                    <div className="space-y-6">
                        <div className="space-y-2">
                            <div className="flex justify-between text-[10px] font-mono text-gray-400">
                                <span>WALL HEIGHT</span>
                                <span>{height}m</span>
                            </div>
                            <input
                                type="range"
                                min="1"
                                max="5"
                                step="0.1"
                                value={height}
                                onChange={(e) => setHeight(parseFloat(e.target.value))}
                                className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                            />
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between text-[10px] font-mono text-gray-400">
                                <span>DETECTION THRESHOLD</span>
                                <span>{threshold}</span>
                            </div>
                            <input
                                type="range"
                                min="0"
                                max="255"
                                step="1"
                                value={threshold}
                                onChange={(e) => setThreshold(parseInt(e.target.value))}
                                className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                            />
                        </div>

                        <div className="text-[10px] font-mono text-gray-500">
                            SCALE: {pixelsPerMeter.toFixed(1)} PX/M
                        </div>

                        <NeonButton
                            variant="cyan"
                            className="w-full"
                            onClick={handleGenerate}
                            disabled={!file || loading}
                        >
                            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <LayoutTemplate className="w-4 h-4 mr-2" />}
                            {loading ? "PROCESSING..." : "GENERATE 3D MODEL"}
                        </NeonButton>

                        {meshUrl && (
                            <div className="flex gap-2">
                                <a href={meshUrl} download className="flex-1 block">
                                    <NeonButton variant="cyan" className="w-full text-[10px]">
                                        DOWNLOAD OBJ
                                    </NeonButton>
                                </a>
                                {dxfUrl && (
                                    <a href={dxfUrl} download className="flex-1 block">
                                        <NeonButton variant="purple" className="w-full text-[10px]">
                                            DOWNLOAD DXF
                                        </NeonButton>
                                    </a>
                                )}
                            </div>
                        )}

                        <div className="text-[10px] font-mono text-gray-500 text-center">
                            {meshUrl ? "MODEL GENERATED" : "READY TO PROCESS"}
                        </div>
                    </div>
                </HoloCard>
            </div>

            {/* Right Panel: 3D Preview */}
            <div className="col-span-8 h-full">
                <HoloCard className="h-full p-0 overflow-hidden border-cyan-500/30 shadow-[0_0_100px_-30px_rgba(0,243,255,0.15)] relative group">
                    <div className="absolute top-6 left-6 z-10 flex gap-4">
                        <div className="font-mono text-[10px] text-cyan-400 bg-black/80 backdrop-blur px-3 py-1.5 rounded border border-cyan-500/30 flex items-center gap-2 shadow-lg">
                            <LayoutTemplate className="w-3 h-3" /> 3D PREVIEW
                        </div>
                    </div>
                    {meshUrl ? (
                        <MeshViewer meshUrl={meshUrl} showWireframe={false} />
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-white/20 font-mono text-xs gap-4">
                            <LayoutTemplate className="w-16 h-16 opacity-20" />
                            <span>NO MODEL GENERATED</span>
                        </div>
                    )}
                </HoloCard>
            </div>
        </div>
    );
}
