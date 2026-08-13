
"use client";
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AssetData {
    meshUrl?: string; // Local or remote URL
    meshPath?: string; // Backend path
    thumbnail?: string;
    metadata?: any;
    validationStatus?: 'pending' | 'valid' | 'invalid';
}

interface ActiveAssetContextType {
    activeAsset: AssetData | null;
    setActiveAsset: (asset: AssetData | null) => void;
    // Helper to quick-load from generation result
    loadFromArtifacts: (artifacts: any) => void;
}

const ActiveAssetContext = createContext<ActiveAssetContextType | undefined>(undefined);

export function ActiveAssetProvider({ children }: { children: ReactNode }) {
    const [activeAsset, setActiveAsset] = useState<AssetData | null>(null);

    const loadFromArtifacts = (artifacts: any) => {
        let newPath = null;

        // Auto-Promote Logic: Determine the best 'successor' asset
        // 1. Remeshing (Topological Transformation)
        if (artifacts?.remeshOutput?.mesh_path) {
            newPath = artifacts.remeshOutput.mesh_path;
        }
        // 2. Dual UV / Texturing (Material Application)
        else if (artifacts?.dualUVOutput?.texture_mesh_path) {
            newPath = artifacts.dualUVOutput.texture_mesh_path;
        }
        // 3. Generative Creation (New Asset)
        else if (artifacts?.generative3DOutput?.generated_mesh_path) {
            newPath = artifacts.generative3DOutput.generated_mesh_path;
        }

        if (newPath) {
            const filename = newPath.split('/').pop();
            // Cache-busting to ensure viewer reload even if filename persists
            const cacheBuster = `?t=${Date.now()}`;
            setActiveAsset({
                meshPath: newPath,
                meshUrl: `http://localhost:8000/static/${filename}${cacheBuster}`,
                metadata: artifacts
            });
            console.log("[ActiveAsset] Auto-promoted asset:", newPath);
        }
    };

    return (
        <ActiveAssetContext.Provider value={{ activeAsset, setActiveAsset, loadFromArtifacts }}>
            {children}
        </ActiveAssetContext.Provider>
    );
}

export function useActiveAsset() {
    const context = useContext(ActiveAssetContext);
    if (context === undefined) {
        throw new Error('useActiveAsset must be used within an ActiveAssetProvider');
    }
    return context;
}
