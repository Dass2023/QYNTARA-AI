/*
 * Qyntara AI Runtime Generator - Unity C# Wrapper
 * Enables real-time 3D generation in Unity using ONNX Runtime
 * 
 * v6.0 Prototype - Runtime SDK
 */

using UnityEngine;
using Unity.Barracuda;
using System.Collections;
using System.IO;

namespace Qyntara.Runtime
{
    /// <summary>
    /// Real-time 3D mesh generator for Unity using LRM (Large Reconstruction Model)
    /// </summary>
    public class QyntaraRuntimeGenerator : MonoBehaviour
    {
        [Header("Model Settings")]
        [Tooltip("Path to ONNX model file")]
        public string modelPath = "Assets/Qyntara/Models/lrm_model.onnx";
        
        [Tooltip("Input image resolution")]
        public int inputResolution = 512;
        
        [Header("Generation Settings")]
        [Tooltip("Marching cubes resolution (higher = more detail, slower)")]
        [Range(64, 512)]
        public int marchingCubesResolution = 256;
        
        [Tooltip("Auto-generate mesh on start")]
        public bool generateOnStart = false;
        
        [Header("Output")]
        [Tooltip("Generated mesh will be assigned here")]
        public MeshFilter outputMeshFilter;
        
        private Model runtimeModel;
        private IWorker worker;
        private bool isGenerating = false;
        
        void Start()
        {
            LoadModel();
            
            if (generateOnStart && outputMeshFilter != null)
            {
                // Generate from default texture
                Texture2D defaultTexture = new Texture2D(inputResolution, inputResolution);
                StartCoroutine(GenerateMeshAsync(defaultTexture));
            }
        }
        
        /// <summary>
        /// Load ONNX model for inference
        /// </summary>
        void LoadModel()
        {
            try
            {
                Debug.Log($"[Qyntara] Loading model from {modelPath}");
                
                // Load ONNX model using Barracuda
                runtimeModel = ModelLoader.Load(modelPath);
                worker = WorkerFactory.CreateWorker(WorkerFactory.Type.ComputePrecompiled, runtimeModel);
                
                Debug.Log("[Qyntara] Model loaded successfully!");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Qyntara] Failed to load model: {e.Message}");
            }
        }
        
        /// <summary>
        /// Generate 3D mesh from texture asynchronously
        /// </summary>
        /// <param name="inputTexture">Input image texture</param>
        /// <returns>Coroutine</returns>
        public IEnumerator GenerateMeshAsync(Texture2D inputTexture)
        {
            if (isGenerating)
            {
                Debug.LogWarning("[Qyntara] Generation already in progress");
                yield break;
            }
            
            if (worker == null)
            {
                Debug.LogError("[Qyntara] Model not loaded");
                yield break;
            }
            
            isGenerating = true;
            float startTime = Time.realtimeSinceStartup;
            
            Debug.Log("[Qyntara] Starting mesh generation...");
            
            // Preprocess image
            Tensor inputTensor = PreprocessImage(inputTexture);
            
            // Run inference
            worker.Execute(inputTensor);
            Tensor outputTensor = worker.PeekOutput();
            
            // Wait for GPU to finish
            yield return new WaitForEndOfFrame();
            
            // Extract mesh from output
            Mesh generatedMesh = ExtractMesh(outputTensor);
            
            // Assign to output
            if (outputMeshFilter != null && generatedMesh != null)
            {
                outputMeshFilter.mesh = generatedMesh;
                Debug.Log($"[Qyntara] Mesh generated in {(Time.realtimeSinceStartup - startTime):F2}s");
                Debug.Log($"[Qyntara] Vertices: {generatedMesh.vertexCount}, Triangles: {generatedMesh.triangles.Length / 3}");
            }
            
            // Cleanup
            inputTensor.Dispose();
            outputTensor.Dispose();
            
            isGenerating = false;
        }
        
        /// <summary>
        /// Preprocess input image for model
        /// </summary>
        Tensor PreprocessImage(Texture2D texture)
        {
            // Resize to input resolution
            Texture2D resized = ResizeTexture(texture, inputResolution, inputResolution);
            
            // Convert to tensor (normalize to [-1, 1])
            float[] pixels = new float[inputResolution * inputResolution * 3];
            Color[] colors = resized.GetPixels();
            
            for (int i = 0; i < colors.Length; i++)
            {
                pixels[i * 3 + 0] = colors[i].r * 2f - 1f;  // R
                pixels[i * 3 + 1] = colors[i].g * 2f - 1f;  // G
                pixels[i * 3 + 2] = colors[i].b * 2f - 1f;  // B
            }
            
            return new Tensor(1, inputResolution, inputResolution, 3, pixels);
        }
        
        /// <summary>
        /// Extract mesh from model output tensor
        /// </summary>
        Mesh ExtractMesh(Tensor outputTensor)
        {
            // NOTE: This is a PROTOTYPE
            // Real implementation would decode the tensor into mesh data
            // For now, create a simple cube as placeholder
            
            Mesh mesh = new Mesh();
            
            // Simple cube vertices
            Vector3[] vertices = new Vector3[]
            {
                new Vector3(-0.5f, -0.5f, -0.5f),
                new Vector3(0.5f, -0.5f, -0.5f),
                new Vector3(0.5f, 0.5f, -0.5f),
                new Vector3(-0.5f, 0.5f, -0.5f),
                new Vector3(-0.5f, -0.5f, 0.5f),
                new Vector3(0.5f, -0.5f, 0.5f),
                new Vector3(0.5f, 0.5f, 0.5f),
                new Vector3(-0.5f, 0.5f, 0.5f)
            };
            
            int[] triangles = new int[]
            {
                0, 2, 1, 0, 3, 2,
                4, 5, 6, 4, 6, 7,
                0, 1, 5, 0, 5, 4,
                1, 2, 6, 1, 6, 5,
                2, 3, 7, 2, 7, 6,
                3, 0, 4, 3, 4, 7
            };
            
            mesh.vertices = vertices;
            mesh.triangles = triangles;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            
            return mesh;
        }
        
        /// <summary>
        /// Resize texture to target resolution
        /// </summary>
        Texture2D ResizeTexture(Texture2D source, int targetWidth, int targetHeight)
        {
            RenderTexture rt = RenderTexture.GetTemporary(targetWidth, targetHeight);
            Graphics.Blit(source, rt);
            
            RenderTexture previous = RenderTexture.active;
            RenderTexture.active = rt;
            
            Texture2D result = new Texture2D(targetWidth, targetHeight);
            result.ReadPixels(new Rect(0, 0, targetWidth, targetHeight), 0, 0);
            result.Apply();
            
            RenderTexture.active = previous;
            RenderTexture.ReleaseTemporary(rt);
            
            return result;
        }
        
        void OnDestroy()
        {
            worker?.Dispose();
        }
    }
}
