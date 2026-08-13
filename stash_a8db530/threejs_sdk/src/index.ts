/**
 * Qyntara Three.js Runtime SDK
 * ============================
 * 
 * Import and process QMesh data in Three.js with WebGPU support.
 * Optimized for web-based 3D applications and spatial computing.
 * 
 * @author Dass2023
 * @license MIT (Open-Core)
 * @version 5.0.0
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader';

/**
 * QMesh data structure matching Python format.
 */
export interface QMeshData {
    vertices: Float32Array | number[][];
    faces: Int32Array | number[][];
    normals?: Float32Array | number[][];
    uvs?: Float32Array[][] | number[][][];
    vertexColors?: Float32Array | number[][];
    materialIds?: Int32Array | number[];
    name?: string;
}

/**
 * QMaterial PBR properties.
 */
export interface QMaterialData {
    name?: string;
    baseColor?: [number, number, number, number];
    metallic?: number;
    roughness?: number;
    baseColorMap?: string;
    metallicMap?: string;
    roughnessMap?: string;
    normalMap?: string;
    emissiveMap?: string;
    aoMap?: string;
}

/**
 * QScene containing multiple meshes and materials.
 */
export interface QSceneData {
    meshes: QMeshData[];
    materials?: QMaterialData[];
    cameras?: any[];
    lights?: any[];
}

/**
 * Qyntara mesh importer for Three.js.
 * Converts QMesh data to Three.js BufferGeometry and Mesh.
 */
export class QyntaraMeshImporter {
    private textureLoader: THREE.TextureLoader;
    private gltfLoader: GLTFLoader;
    private dracoLoader: DRACOLoader;

    constructor() {
        this.textureLoader = new THREE.TextureLoader();
        this.gltfLoader = new GLTFLoader();

        // Configure Draco decoder for compressed glTF
        this.dracoLoader = new DRACOLoader();
        this.dracoLoader.setDecoderPath('https://www.gstatic.com/draco/v1/decoders/');
        this.gltfLoader.setDRACOLoader(this.dracoLoader);
    }

    /**
     * Create Three.js BufferGeometry from QMesh data.
     */
    createGeometry(meshData: QMeshData): THREE.BufferGeometry {
        const geometry = new THREE.BufferGeometry();

        // Convert vertices to Float32Array if needed
        const vertices = meshData.vertices instanceof Float32Array
            ? meshData.vertices
            : new Float32Array(meshData.vertices.flat());

        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

        // Convert faces to indices (assuming triangulated)
        const faces = meshData.faces instanceof Int32Array
            ? meshData.faces
            : new Int32Array(meshData.faces.flat().filter((v: number) => v !== -1));

        geometry.setIndex(new THREE.BufferAttribute(faces, 1));

        // Add normals if available
        if (meshData.normals) {
            const normals = meshData.normals instanceof Float32Array
                ? meshData.normals
                : new Float32Array(meshData.normals.flat());

            geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
        } else {
            geometry.computeVertexNormals();
        }

        // Add UVs if available (Three.js uses first UV set by default)
        if (meshData.uvs && meshData.uvs.length > 0) {
            const uvSet0 = meshData.uvs[0];
            const uvs = uvSet0 instanceof Float32Array
                ? uvSet0
                : new Float32Array(uvSet0.flat());

            geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));

            // Additional UV sets (uv2, uv3, etc.)
            for (let i = 1; i < Math.min(meshData.uvs.length, 4); i++) {
                const uvSet = meshData.uvs[i];
                const uvsArray = uvSet instanceof Float32Array
                    ? uvSet
                    : new Float32Array(uvSet.flat());

                geometry.setAttribute(`uv${i + 1}`, new THREE.BufferAttribute(uvsArray, 2));
            }
        }

        // Add vertex colors if available
        if (meshData.vertexColors) {
            const colors = meshData.vertexColors instanceof Float32Array
                ? meshData.vertexColors
                : new Float32Array(meshData.vertexColors.flat());

            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        }

        geometry.computeBoundingBox();
        geometry.computeBoundingSphere();

        console.log(`[Qyntara] Created geometry: ${meshData.name || 'QMesh'}`);
        console.log(`  Vertices: ${geometry.attributes.position.count}`);
        console.log(`  Triangles: ${geometry.index ? geometry.index.count / 3 : 0}`);

        return geometry;
    }

    /**
     * Create Three.js Mesh from QMesh data.
     */
    createMesh(
        meshData: QMeshData,
        material?: THREE.Material
    ): THREE.Mesh {
        const geometry = this.createGeometry(meshData);
        const mat = material || new THREE.MeshStandardMaterial({
            color: 0xCCCCCC,
            roughness: 0.5,
            metalness: 0.0
        });

        const mesh = new THREE.Mesh(geometry, mat);
        mesh.name = meshData.name || 'QMesh';

        return mesh;
    }

    /**
     * Import GLB file and return Three.js Group.
     * Supports streaming for large files.
     */
    async importGLB(
        url: string,
        onProgress?: (event: ProgressEvent) => void
    ): Promise<THREE.Group> {
        return new Promise((resolve, reject) => {
            this.gltfLoader.load(
                url,
                (gltf) => {
                    console.log(`[Qyntara] Loaded GLB: ${url}`);
                    console.log(`  Meshes: ${gltf.scene.children.length}`);
                    resolve(gltf.scene);
                },
                onProgress,
                (error) => {
                    console.error(`[Qyntara] Failed to load GLB: ${error}`);
                    reject(error);
                }
            );
        });
    }

    /**
     * Create PBR material from Qyntara material data.
     */
    async createMaterial(materialData: QMaterialData): Promise<THREE.MeshStandardMaterial> {
        const material = new THREE.MeshStandardMaterial({
            name: materialData.name || 'QMaterial'
        });

        // Set base color
        if (materialData.baseColor) {
            const [r, g, b, a] = materialData.baseColor;
            material.color = new THREE.Color(r, g, b);
            material.opacity = a;
            if (a < 1.0) {
                material.transparent = true;
            }
        }

        // Set PBR properties
        if (materialData.metallic !== undefined) {
            material.metalness = materialData.metallic;
        }

        if (materialData.roughness !== undefined) {
            material.roughness = materialData.roughness;
        }

        // Load textures
        const texturePromises: Promise<void>[] = [];

        if (materialData.baseColorMap) {
            texturePromises.push(
                this.loadTexture(materialData.baseColorMap).then(texture => {
                    material.map = texture;
                })
            );
        }

        if (materialData.metallicMap) {
            texturePromises.push(
                this.loadTexture(materialData.metallicMap).then(texture => {
                    material.metalnessMap = texture;
                })
            );
        }

        if (materialData.roughnessMap) {
            texturePromises.push(
                this.loadTexture(materialData.roughnessMap).then(texture => {
                    material.roughnessMap = texture;
                })
            );
        }

        if (materialData.normalMap) {
            texturePromises.push(
                this.loadTexture(materialData.normalMap).then(texture => {
                    material.normalMap = texture;
                })
            );
        }

        if (materialData.aoMap) {
            texturePromises.push(
                this.loadTexture(materialData.aoMap).then(texture => {
                    material.aoMap = texture;
                })
            );
        }

        // Wait for all textures to load
        await Promise.all(texturePromises);

        console.log(`[Qyntara] Created material: ${material.name}`);

        return material;
    }

    /**
     * Load texture with error handling.
     */
    private loadTexture(url: string): Promise<THREE.Texture> {
        return new Promise((resolve, reject) => {
            this.textureLoader.load(
                url,
                (texture) => {
                    texture.encoding = THREE.sRGBEncoding;
                    resolve(texture);
                },
                undefined,
                (error) => {
                    console.warn(`[Qyntara] Failed to load texture: ${url}`, error);
                    // Return placeholder texture instead of rejecting
                    const placeholder = new THREE.Texture();
                    resolve(placeholder);
                }
            );
        });
    }

    /**
     * Clean up resources.
     */
    dispose(): void {
        this.dracoLoader.dispose();
    }
}

/**
 * Mesh processing utilities for Three.js.
 */
export class ThreeMeshProcessor {
    /**
     * Center mesh at origin.
     */
    static centerMesh(mesh: THREE.Mesh): void {
        mesh.geometry.computeBoundingBox();
        const bbox = mesh.geometry.boundingBox!;
        const center = bbox.getCenter(new THREE.Vector3());

        mesh.geometry.translate(-center.x, -center.y, -center.z);
        mesh.geometry.computeBoundingBox();

        console.log(`[Qyntara] Centered mesh, offset: ${center.toArray()}`);
    }

    /**
     * Scale mesh uniformly.
     */
    static scaleMesh(mesh: THREE.Mesh, scale: number): void {
        mesh.geometry.scale(scale, scale, scale);
        mesh.geometry.computeBoundingBox();
        mesh.geometry.computeBoundingSphere();

        console.log(`[Qyntara] Scaled mesh by ${scale}x`);
    }

    /**
     * Validate mesh for common issues.
     */
    static validateMesh(mesh: THREE.Mesh): string[] {
        const issues: string[] = [];
        const geometry = mesh.geometry;

        if (!geometry.attributes.position) {
            issues.push('Mesh has no vertices');
        }

        if (!geometry.index) {
            issues.push('Mesh has no indices');
        }

        if (!geometry.attributes.normal) {
            issues.push('Mesh has no normals');
        }

        if (!geometry.attributes.uv) {
            issues.push('Mesh has no UVs');
        }

        // Check for degenerate triangles
        if (geometry.index) {
            const positions = geometry.attributes.position.array as Float32Array;
            const indices = geometry.index.array;
            let degenerateCount = 0;

            for (let i = 0; i < indices.length; i += 3) {
                const i0 = indices[i] * 3;
                const i1 = indices[i + 1] * 3;
                const i2 = indices[i + 2] * 3;

                const v0 = new THREE.Vector3(positions[i0], positions[i0 + 1], positions[i0 + 2]);
                const v1 = new THREE.Vector3(positions[i1], positions[i1 + 1], positions[i1 + 2]);
                const v2 = new THREE.Vector3(positions[i2], positions[i2 + 1], positions[i2 + 2]);

                const edge1 = new THREE.Vector3().subVectors(v1, v0);
                const edge2 = new THREE.Vector3().subVectors(v2, v0);
                const area = edge1.cross(edge2).length() / 2;

                if (area < 0.000001) {
                    degenerateCount++;
                }
            }

            if (degenerateCount > 0) {
                issues.push(`${degenerateCount} degenerate triangles detected`);
            }
        }

        console.log(`[Qyntara] Mesh validation: ${issues.length} issues found`);

        return issues;
    }

    /**
     * Compute mesh statistics.
     */
    static computeStats(mesh: THREE.Mesh): any {
        const geometry = mesh.geometry;
        geometry.computeBoundingBox();
        geometry.computeBoundingSphere();

        const bbox = geometry.boundingBox!;
        const bsphere = geometry.boundingSphere!;

        const vertexCount = geometry.attributes.position.count;
        const triangleCount = geometry.index ? geometry.index.count / 3 : 0;

        return {
            vertexCount,
            triangleCount,
            boundingBox: {
                min: bbox.min.toArray(),
                max: bbox.max.toArray(),
                size: bbox.getSize(new THREE.Vector3()).toArray()
            },
            boundingSphere: {
                center: bsphere.center.toArray(),
                radius: bsphere.radius
            }
        };
    }
}

/**
 * Example usage:
 * 
 * ```typescript
 * import { QyntaraMeshImporter, ThreeMeshProcessor } from '@qyntara/threejs-sdk';
 * 
 * // Initialize importer
 * const importer = new QyntaraMeshImporter();
 * 
 * // Import GLB file
 * const scene = await importer.importGLB('/models/character.glb');
 * threeScene.add(scene);
 * 
 * // Process mesh
 * const mesh = scene.children[0] as THREE.Mesh;
 * ThreeMeshProcessor.centerMesh(mesh);
 * ThreeMeshProcessor.scaleMesh(mesh, 0.5);
 * 
 * // Validate
 * const issues = ThreeMeshProcessor.validateMesh(mesh);
 * console.log('Issues:', issues);
 * ```
 */
