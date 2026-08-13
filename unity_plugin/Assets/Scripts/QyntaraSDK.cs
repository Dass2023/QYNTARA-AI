using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;

public class QyntaraSDK : MonoBehaviour
{
    private const string API_URL = "http://localhost:8008/validate/core";

    public delegate void ValidationCallback(string jsonResponse);

    public static IEnumerator ValidateAsset(string industry, string metadataJson, ValidationCallback callback)
    {
        // Construct Payload
        string payload = string.Format("{{\"industry\": \"{0}\", \"metadata\": {1}}}", industry, metadataJson);
        byte[] bodyRaw = Encoding.UTF8.GetBytes(payload);

        UnityWebRequest request = new UnityWebRequest(API_URL, "POST");
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        Debug.Log($"[Qyntara] Sending Request to {API_URL}...");
        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError($"[Qyntara] Error: {request.error}");
        }
        else
        {
            Debug.Log($"[Qyntara] Response: {request.downloadHandler.text}");
            callback?.Invoke(request.downloadHandler.text);
        }
    }
}
