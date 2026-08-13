# Qyntara Three.js SDK - Quick Start

## Installation

```bash
npm install @qyntara/threejs-sdk three
```

## Basic Usage

### Import GLB File

```typescript
import * as THREE from 'three';
import { QyntaraMeshImporter } from '@qyntara/threejs-sdk';

// Set up Three.js scene
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Import GLB
const importer = new QyntaraMeshImporter();
const model = await importer.importGLB('/path/to/model.glb', (event) => {
    console.log(`Loading: ${(event.loaded / event.total * 100).toFixed(2)}%`);
});

scene.add(model);

// Render
camera.position.z = 5;
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();
```

### Create Mesh from QMesh Data

```typescript
import { QyntaraMeshImporter, QMeshData } from '@qyntara/threejs-sdk';

const meshData: QMeshData = {
    vertices: new Float32Array([...]),
    faces: new Int32Array([...]),
    normals: new Float32Array([...]),
    uvs: [new Float32Array([...])],
    name: 'MyMesh'
};

const importer = new QyntaraMeshImporter();
const mesh = importer.createMesh(meshData);
scene.add(mesh);
```

### Process Meshes

```typescript
import { ThreeMeshProcessor } from '@qyntara/threejs-sdk';

// Center mesh at origin
ThreeMeshProcessor.centerMesh(mesh);

// Scale uniformly
ThreeMeshProcessor.scaleMesh(mesh, 0.5);

// Validate
const issues = ThreeMesh Processor.validateMesh(mesh);
if (issues.length > 0) {
    console.warn('Mesh issues:', issues);
}

// Get statistics
const stats = ThreeMeshProcessor.computeStats(mesh);
console.log('Stats:', stats);
```

### PBR Materials

```typescript
import { QyntaraMeshImporter, QMaterialData } from '@qyntara/threejs-sdk';

const materialData: QMaterialData = {
    name: 'GoldMetal',
    baseColor: [1.0, 0.85, 0.45, 1.0],
    metallic: 1.0,
    roughness: 0.2,
    baseColorMap: '/textures/gold_albedo.png',
    normalMap: '/textures/gold_normal.png',
    metallicMap: '/textures/gold_metallic.png',
    roughnessMap: '/textures/gold_roughness.png'
};

const importer = new QyntaraMeshImporter();
const material = await importer.createMaterial(materialData);
mesh.material = material;
```

## WebGPU Support

For better performance, use WebGPU renderer:

```typescript
import WebGPU from 'three/examples/jsm/capabilities/WebGPU.js';
import WebGPURenderer from 'three/examples/jsm/renderers/webgpu/WebGPURenderer.js';

if (WebGPU.isAvailable()) {
    const renderer = new WebGPURenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
} else {
    // Fallback to WebGL
    const renderer = new THREE.WebGLRenderer();
}
```

## Progressive Loading

For large models, use progressive loading:

```typescript
const importer = new QyntaraMeshImporter();

let loadedPercentage = 0;
const model = await importer.importGLB('/large-model.glb', (event) => {
    loadedPercentage = (event.loaded / event.total * 100);
    updateProgressBar(loadedPercentage);
});

console.log('Model loaded!');
scene.add(model);
```

## Integration with React

```tsx
import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { QyntaraMeshImporter } from '@qyntara/threejs-sdk';

function ModelViewer({ glbPath }: { glbPath: string }) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        // Setup scene
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        containerRef.current.appendChild(renderer.domElement);

        // Load model
        const importer = new QyntaraMeshImporter();
        importer.importGLB(glbPath).then(model => {
            scene.add(model);
        });

        // Animation loop
        camera.position.z = 5;
        const animate = () => {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        };
        animate();

        // Cleanup
        return () => {
            renderer.dispose();
            importer.dispose();
        };
    }, [glbPath]);

    return <div ref={containerRef} />;
}
```

## TypeScript Support

Full TypeScript support with type definitions:

```typescript
import type { QMeshData, QMaterialData, QSceneData } from '@qyntara/threejs-sdk';
```

## License

MIT (Open-Core)
