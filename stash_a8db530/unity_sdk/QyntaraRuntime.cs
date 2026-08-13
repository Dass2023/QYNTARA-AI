// Qyntara Unity SDK - QMesh Importer
// ===================================
// 
// Import QMesh data into Unity's native mesh format.
// Supports vertex colors, multiple UV sets, and normals.
//
// Author: Dass2023
// License: MIT (Open-Core)
// Version: 5.0.0

using UnityEngine;
using UnityEditor;
using System;
using System.IO;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace Qyntara.Runtime
{
    /// <summary>
    /// Unity mesh representation of Qyntara QMesh.
    /// </summary>
    [Serializable]
    public class QMeshData
    {
        public Vector3[] vertices;
        public int[] faces;          // Flattened triangle indices
        public Vector3[] normals;
        public Vector2[][] uvSets;   // Multiple UV sets
        public Color[] vertexColors;
        public int[] materialIds;
        public string meshName;
    }

    /// <summary>
    /// Import QMesh from glTF/GLB files into Unity.
    /// </summary>
    public static class QMeshImporter
    {
        /// <summary>
        /// Import GLB file as Unity GameObject with mesh and materials.
        /// </summary>
        /// <param name="glbPath">Path to .glb file</param>
        /// <returns>GameObject with imported mesh</returns>
        public static GameObject ImportGLB(string glbPath)
        {
            if (!File.Exists(glbPath))
            {
                Debug.LogError($"[QMeshImporter] File not found: {glbPath}");
                return null;
            }

            Debug.Log($"[QMeshImporter] Importing: {glbPath}");

            // Use Unity's built-in glTF importer (Unity 2020.2+)
            // For older versions, would need GLTFUtility or similar
            #if UNITY_2020_2_OR_NEWER
            var importer = AssetImporter.GetAtPath(glbPath) as ModelImporter;
            if (importer != null)
            {
                // Configure import settings
                importer.importNormals = ModelImporterNormals.Import;
                importer.importTangents = ModelImporterTangents.CalculateMikk;
                importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
                
                importer.SaveAndReimport();
                
                // Load the imported asset
                GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(glbPath);
                if (prefab != null)
                {
                    GameObject instance = GameObject.Instantiate(prefab);
                    instance.name = Path.GetFileNameWithoutExtension(glbPath);
                    
                    Debug.Log($"[QMeshImporter] Successfully imported: {instance.name}");
                    return instance;
                }
            }
            #endif

            Debug.LogWarning("[QMeshImporter] Using fallback importer");
            return ImportGLBFallback(glbPath);
        }

        /// <summary>
        /// Fallback GLB importer for older Unity versions or missing native support.
        /// </summary>
        private static GameObject ImportGLBFallback(string glbPath)
        {
            GameObject container = new GameObject($"[MISSING_IMPORTER] {Path.GetFileNameWithoutExtension(glbPath)}");
            
            Debug.LogError($"[QMeshImporter] CRITICAL: No native glTF importer found in this Unity version for: {glbPath}");
            Debug.LogWarning("[QMeshImporter] PRODUCTION RECOMMENDATION:");
            Debug.LogWarning("1. Install 'GLTFUtility' (Github) or 'UnityGLTF' via OpenUPM.");
            Debug.LogWarning("2. Or upgrade to Unity 2020.2+ for native ModelImporter support.");
            
            // Create a small visual placeholder in-scene
            GameObject placeholder = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            placeholder.name = "DEBUG_PLACEHOLDER_ERROR";
            placeholder.transform.SetParent(container.transform);
            placeholder.transform.localScale = Vector3.one * 0.15f;
            
            var renderer = placeholder.GetComponent<Renderer>();
            if (renderer != null) {
                // Use a neon-magenta error shader if available, else red-emissive
                renderer.sharedMaterial = new Material(Shader.Find("Standard"));
                renderer.sharedMaterial.color = new Color(1f, 0f, 1f, 1f); 
                renderer.sharedMaterial.EnableKeyword("_EMISSION");
                renderer.sharedMaterial.SetColor("_EmissionColor", new Color(0.5f, 0f, 0.5f));
            }
            
            return container;
        }

        /// <summary>
        /// Create Unity Mesh from QMeshData.
        /// </summary>
        /// <param name="qmeshData">QMesh data</param>
        /// <returns>Unity Mesh</returns>
        public static Mesh CreateMeshFromQMesh(QMeshData qmeshData)
        {
            // Production Guardrail: Unity's mesh limit
            const int MAX_SAFE_VERTS = 200000; 
            if (qmeshData.vertices.Length > MAX_SAFE_VERTS)
            {
                Debug.LogWarning($"[QMeshImporter] High Poly Warning: Asset has {qmeshData.vertices.Length} vertices. This may impact mobile performance.");
            }

            Mesh mesh = new Mesh();
            mesh.indexFormat = qmeshData.vertices.Length > 65535 ? 
                UnityEngine.Rendering.IndexFormat.UInt32 : 
                UnityEngine.Rendering.IndexFormat.UInt16;

            mesh.name = qmeshData.meshName ?? "QMesh";
            mesh.vertices = qmeshData.vertices;
            mesh.triangles = qmeshData.faces;

            if (qmeshData.normals != null && qmeshData.normals.Length > 0)
                mesh.normals = qmeshData.normals;
            else
                mesh.RecalculateNormals();

            if (qmeshData.uvSets != null && qmeshData.uvSets.Length > 0)
            {
                for (int i = 0; i < Mathf.Min(qmeshData.uvSets.Length, 8); i++)
                {
                    if (qmeshData.uvSets[i] != null)
                        mesh.SetUVs(i, new List<Vector2>(qmeshData.uvSets[i]));
                }
            }

            if (qmeshData.vertexColors != null && qmeshData.vertexColors.Length > 0)
                mesh.colors = qmeshData.vertexColors;

            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>
        /// Create GameObject with mesh from QMeshData.
        /// </summary>
        public static GameObject CreateGameObjectFromQMesh(QMeshData qmeshData)
        {
            GameObject go = new GameObject(qmeshData.meshName ?? "QMesh");
            
            MeshFilter meshFilter = go.AddComponent<MeshFilter>();
            meshFilter.mesh = CreateMeshFromQMesh(qmeshData);
            
            MeshRenderer renderer = go.AddComponent<MeshRenderer>();
            renderer.material = new Material(Shader.Find("Standard"));
            
            return go;
        }
    }

    /// <summary>
    /// Convert Qyntara materials to Unity materials.
    /// </summary>
    public static class QMaterialConverter
    {
        /// <summary>
        /// Create Unity Standard material from Qyntara material properties.
        /// </summary>
        public static Material CreateStandardMaterial(
            Color baseColor,
            float metallic,
            float roughness,
            Texture2D albedoMap = null,
            Texture2D metallicMap = null,
            Texture2D normalMap = null,
            Texture2D emissionMap = null,
            Texture2D occlusionMap = null,
            Texture2D heightMap = null
        )
        {
            Material mat = new Material(Shader.Find("Standard"));
            if (mat.shader == null) {
                Debug.LogError("[QMaterialConverter] 'Standard' shader not found. Ensure it's in 'Always Included Shaders'.");
                return null;
            }
            
            mat.SetColor("_Color", baseColor);
            mat.SetFloat("_Metallic", metallic);
            mat.SetFloat("_Glossiness", Mathf.Clamp01(1.0f - roughness)); 
            
            if (albedoMap != null) mat.SetTexture("_MainTex", albedoMap);
            
            if (metallicMap != null) {
                mat.SetTexture("_MetallicGlossMap", metallicMap);
                mat.EnableKeyword("_METALLICGLOSSMAP");
            }
            
            if (normalMap != null) {
                mat.SetTexture("_BumpMap", normalMap);
                mat.EnableKeyword("_NORMALMAP");
                mat.SetFloat("_BumpScale", 1.0f);
            }

            if (emissionMap != null) {
                mat.SetTexture("_EmissionMap", emissionMap);
                mat.SetColor("_EmissionColor", Color.white);
                mat.EnableKeyword("_EMISSION");
            }

            if (occlusionMap != null) {
                mat.SetTexture("_OcclusionMap", occlusionMap);
            }

            if (heightMap != null) {
                mat.SetTexture("_ParallaxMap", heightMap);
                mat.EnableKeyword("_PARALLAXMAP");
            }
            
            return mat;
        }

        public static Material CreateURPMaterial(
            Color baseColor,
            float metallic,
            float smoothness,
            Texture2D baseMap = null,
            Texture2D bumpMap = null,
            Texture2D emissionMap = null,
            Texture2D occlusionMap = null
        )
        {
            Material mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            
            if (mat.shader == null)
            {
                Debug.LogWarning("[QMaterialConverter] URP/Lit shader not found, falling back to Standard.");
                return CreateStandardMaterial(baseColor, metallic, 1.0f - smoothness, baseMap, null, bumpMap, emissionMap, occlusionMap);
            }
            
            mat.SetColor("_BaseColor", baseColor);
            mat.SetFloat("_Metallic", metallic);
            mat.SetFloat("_Smoothness", smoothness);

            if (baseMap != null) mat.SetTexture("_BaseMap", baseMap);
            
            if (bumpMap != null) {
                mat.SetTexture("_BumpMap", bumpMap);
                mat.EnableKeyword("_NORMALMAP");
            }

            if (emissionMap != null) {
                mat.SetTexture("_EmissionMap", emissionMap);
                mat.SetColor("_EmissionColor", Color.white);
                mat.EnableKeyword("_EMISSION");
            }

            if (occlusionMap != null) {
                mat.SetTexture("_OcclusionMap", occlusionMap);
            }
            
            return mat;
        }
    }

    /// <summary>
    /// Runtime mesh processor - Unity port of MeshProcessor.
    /// </summary>
    public static class UnityMeshProcessor
    {
        /// <summary>
        /// Center mesh at origin.
        /// </summary>
        public static void CenterMesh(Mesh mesh)
        {
            Bounds bounds = mesh.bounds;
            Vector3 center = bounds.center;
            
            Vector3[] vertices = mesh.vertices;
            for (int i = 0; i < vertices.Length; i++)
            {
                vertices[i] -= center;
            }
            
            mesh.vertices = vertices;
            mesh.RecalculateBounds();
            
            Debug.Log($"[UnityMeshProcessor] Centered mesh, offset: {center}");
        }

        /// <summary>
        /// Scale mesh uniformly.
        /// </summary>
        public static void ScaleMesh(Mesh mesh, float scale)
        {
            Vector3[] vertices = mesh.vertices;
            for (int i = 0; i < vertices.Length; i++)
            {
                vertices[i] *= scale;
            }
            
            mesh.vertices = vertices;
            mesh.RecalculateBounds();
            
            Debug.Log($"[UnityMeshProcessor] Scaled mesh by {scale}x");
        }

        /// <summary>
        /// Validate mesh for common issues.
        /// </summary>
        public static List<string> ValidateMesh(Mesh mesh)
        {
            List<string> issues = new List<string>();
            
            // Polycount Soft-Limits for Mobile/XR Production
            const int MAX_VERTS_16BIT = 65535;
            if (mesh.vertexCount > MAX_VERTS_16BIT && mesh.indexFormat == UnityEngine.Rendering.IndexFormat.UInt16)
            {
                issues.Add($"Critical: Mesh exceeds 16-bit index limit ({mesh.vertexCount} verts). Hardware compatibility risk.");
            }

            if (mesh.vertexCount == 0)
            {
                issues.Add("Mesh has no vertices");
            }
            
            if (mesh.triangles.Length == 0)
            {
                issues.Add("Mesh has no triangles");
            }
            
            if (mesh.triangles.Length % 3 != 0)
            {
                issues.Add("Triangle count not divisible by 3");
            }
            
            if (!mesh.HasVertexAttribute(UnityEngine.Rendering.VertexAttribute.Normal))
            {
                issues.Add("Mesh has no normals");
            }
            
            if (!mesh.HasVertexAttribute(UnityEngine.Rendering.VertexAttribute.TexCoord0))
            {
                issues.Add("Mesh has no UVs");
            }
            
            // Check for degenerate triangles
            Vector3[] verts = mesh.vertices;
            int[] tris = mesh.triangles;
            
            int degenerateCount = 0;
            for (int i = 0; i < tris.Length; i += 3)
            {
                Vector3 v0 = verts[tris[i]];
                Vector3 v1 = verts[tris[i + 1]];
                Vector3 v2 = verts[tris[i + 2]];
                
                float area = Vector3.Cross(v1 - v0, v2 - v0).magnitude / 2f;
                if (area < 0.000001f)
                {
                    degenerateCount++;
                }
            }
            
            if (degenerateCount > 0)
            {
                issues.Add($"{degenerateCount} degenerate triangles detected");
            }
            
            return issues;
        }
    }
}
