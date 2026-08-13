using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using Qyntara.Runtime;
using Newtonsoft.Json;

namespace Qyntara.SDK
{
    public enum SyncState { Idle, Patching, Synchronized, Error, Disconnected }

    /// <summary>
    /// Qyntara Runtime Client - Handles polling and synchronization with the backend.
    /// </summary>
    public class QyntaraClient : MonoBehaviour
    {
        [Header("Configuration")]
        public string serverUrl = "http://localhost:8000";
        public string apiKey = "QYNTARA-X-777";
        public string targetAssetId = "current_scene";
        public float pollInterval = 5.0f;

        [Header("Runtime Status")]
        public SyncState state = SyncState.Disconnected;
        public string lastVersion = "";
        public float lastValidationScore = 0f;

        private void Start()
        {
            StartCoroutine(PollRegistry());
        }

        private IEnumerator PollRegistry()
        {
            while (true)
            {
                yield return CheckForUpdates();
                yield return new WaitForSeconds(pollInterval);
            }
        }

        private IEnumerator CheckForUpdates()
        {
            state = SyncState.Idle;
            string url = $"{serverUrl}/api/v1/registry/{targetAssetId}";
            
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.SetRequestHeader("X-API-KEY", apiKey);
                request.timeout = 5;
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    ProcessUpdate(request.downloadHandler.text);
                }
                else
                {
                    state = SyncState.Disconnected;
                    Debug.LogWarning($"[QyntaraClient] Registry polling failed (Code {request.responseCode}): {request.error}");
                }
            }
        }

        private void ProcessUpdate(string json)
        {
            try
            {
                var metadata = JsonConvert.DeserializeObject<Dictionary<string, object>>(json);
                string currentVersion = metadata.ContainsKey("version") ? metadata["version"].ToString() : "0.1.0";

                if (currentVersion != lastVersion)
                {
                    state = SyncState.Patching;
                    Debug.Log($"[QyntaraClient] New asset version: {currentVersion}");
                    lastVersion = currentVersion;
                    
                    if (metadata.ContainsKey("score"))
                        lastValidationScore = float.Parse(metadata["score"].ToString());

                    RefreshAsset(metadata["path"].ToString());
                }
                else
                {
                    state = SyncState.Synchronized;
                }
            }
            catch (System.Exception e)
            {
                state = SyncState.Error;
                Debug.LogError($"[QyntaraClient] Error processing JSON: {e.Message}");
            }
        }

        private void RefreshAsset(string path)
        {
            Debug.Log($"[QyntaraClient] Initializing Sync for: {path}");
            StartCoroutine(DownloadAsset(path));
        }

        private IEnumerator DownloadAsset(string relativePath)
        {
            // Normalize path for web
            string cleanPath = relativePath.Replace("\\", "/");
            
            // Remove known path prefixes
            string[] systemPrefixes = { "backend/data/", "i:/qyntara ai/backend/data/", "/app/backend/data/" };
            foreach (var prefix in systemPrefixes)
            {
                if (cleanPath.ToLower().StartsWith(prefix.ToLower()))
                {
                    cleanPath = cleanPath.Substring(prefix.Length);
                    break;
                }
            }

            string url = $"{serverUrl}/static/{cleanPath}"; 
            string tempPath = Path.Combine(Application.temporaryCachePath, Path.GetFileName(cleanPath));

            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.SetRequestHeader("X-API-KEY", apiKey);
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    try {
                        byte[] data = request.downloadHandler.data;
                        if (data == null || data.Length == 0) {
                             state = SyncState.Error;
                             Debug.LogError($"[QyntaraClient] Downloaded asset is empty.");
                             yield break;
                        }

                        File.WriteAllBytes(tempPath, data);
                        Debug.Log($"[QyntaraClient] Patch downloaded successfully: {tempPath}");
                        
                        // Execute Import
                        GameObject instance = QMeshImporter.ImportGLB(tempPath);
                        if (instance != null)
                        {
                            instance.transform.position = Vector3.zero;
                            instance.tag = "EditorOnly"; 
                            state = SyncState.Synchronized;
                        }
                        else {
                            state = SyncState.Error;
                        }
                    } catch (System.Exception e) {
                        state = SyncState.Error;
                        Debug.LogError($"[QyntaraClient] Asset ingestion failed: {e.Message}");
                    }
                }
                else
                {
                    state = SyncState.Error;
                    Debug.LogError($"[QyntaraClient] Binary download failed (Code {request.responseCode}): {request.error}");
                }
            }
        }
    }
}
