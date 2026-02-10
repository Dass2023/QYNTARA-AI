"use client";
import React, { useState, useRef } from 'react';

interface ImageViewerProps {
    imageUrl: string;
    onSegment: (point: [number, number], clickType: 'left' | 'right') => void;
    markers: Array<{ position: [number, number], color: string }>;
}

export default function ImageViewer({ imageUrl, onSegment, markers }: ImageViewerProps) {
    const imgRef = useRef<HTMLImageElement>(null);

    const handleClick = (e: React.MouseEvent, type: 'left' | 'right') => {
        if (!imgRef.current) return;

        const rect = imgRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Normalize coordinates (0-1) or use pixels? 
        // Let's use pixels relative to the displayed image size for now, 
        // but ideally we map to natural size.
        // For simplicity in this demo, let's pass the raw pixel coordinates relative to the image element.
        // The parent/backend can handle scaling if needed, or we scale here.

        const scaleX = imgRef.current.naturalWidth / rect.width;
        const scaleY = imgRef.current.naturalHeight / rect.height;

        const naturalX = x * scaleX;
        const naturalY = y * scaleY;

        onSegment([naturalX, naturalY], type);
    };

    return (
        <div className="w-full h-full bg-black/40 relative flex items-center justify-center overflow-hidden">
            <div className="relative">
                <img
                    ref={imgRef}
                    src={imageUrl}
                    alt="Segmentation Target"
                    className="max-w-full max-h-full object-contain cursor-crosshair"
                    onClick={(e) => handleClick(e, 'left')}
                    onContextMenu={(e) => {
                        e.preventDefault();
                        handleClick(e, 'right');
                    }}
                />

                {/* Markers Overlay */}
                {markers.map((marker, i) => {
                    // We need to map natural coordinates back to display coordinates
                    // This requires a re-render or state update when image resizes.
                    // For a robust solution, we should store markers in normalized (0-1) space.
                    // But since we are passing natural coords, let's try to position them using % if possible?
                    // No, we need to know the aspect ratio.

                    // Simplified approach: Render markers as absolute children of the image container?
                    // If the image is centered, we can use percentage positioning if we convert natural coords to %.

                    const left = marker.position[0]; // This is natural X
                    const top = marker.position[1]; // This is natural Y

                    // We can't easily convert to % without knowing natural dimensions here cleanly without state.
                    // Let's assume the parent passes normalized coords or we change the contract.
                    // Actually, let's just use a helper to get % style if we can access natural dimensions.

                    // Better: Just use the click event to set state in parent, and parent passes back normalized coords?
                    // Or just use the ref.

                    let style = {};
                    if (imgRef.current) {
                        const naturalW = imgRef.current.naturalWidth;
                        const naturalH = imgRef.current.naturalHeight;
                        if (naturalW && naturalH) {
                            style = {
                                left: `${(left / naturalW) * 100}%`,
                                top: `${(top / naturalH) * 100}%`
                            };
                        }
                    }

                    return (
                        <div
                            key={i}
                            className="absolute w-3 h-3 rounded-full border border-white/50 transform -translate-x-1/2 -translate-y-1/2 shadow-sm"
                            style={{
                                ...style,
                                backgroundColor: marker.color
                            }}
                        ></div>
                    );
                })}
            </div>
        </div>
    );
}
