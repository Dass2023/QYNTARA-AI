"use client";
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

export default function HolographicDropzone({ onFileSelected }: { onFileSelected: (f: File) => void }) {
    const onDrop = useCallback((files: File[]) => {
        if (files[0]) onFileSelected(files[0]);
    }, [onFileSelected]);
    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, maxFiles: 1 });
    return (
        <div {...getRootProps()} className={`h-48 border-2 border-dashed flex items-center justify-center cursor-pointer ${isDragActive ? 'border-cyan-400 bg-cyan-900/30' : 'border-cyan-800/50'}`}>
            <input {...getInputProps()} />
            <p className="text-cyan-500 font-mono text-xs">{isDragActive ? "INITIALIZING SCAN..." : "DROP VISUAL REFERENCE"}</p>
        </div>
    );
}
