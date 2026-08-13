using UnityEngine;
using UnityEditor;
using System.Collections.Generic;

public class QyntaraEditorWindow : EditorWindow
{
    private string selectedIndustry = "gaming";
    private string lastResult = "";
    private Vector2 scrollPos;

    [MenuItem("Qyntara/Spatial Intelligence Check")]
    public static void ShowWindow()
    {
        GetWindow<QyntaraEditorWindow>("Qyntara AI");
    }

    private void OnGUI()
    {
        GUILayout.Label("Qyntara Spatial Intelligence", EditorStyles.boldLabel);

        selectedIndustry = EditorGUILayout.TextField("Industry Context", selectedIndustry);

        if (GUILayout.Button("Validate Selected Asset"))
        {
            RunValidation();
        }

        GUILayout.Label("Analysis Results:", EditorStyles.boldLabel);
        scrollPos = EditorGUILayout.BeginScrollView(scrollPos, GUILayout.Height(300));
        GUILayout.TextArea(lastResult);
        EditorGUILayout.EndScrollView();
    }

    private void RunValidation()
    {
        GameObject obj = Selection.activeGameObject;
        if (obj == null)
        {
            Debug.LogWarning("No GameObject selected.");
            return;
        }

        // Mock Metadata Extraction
        string metaJson = ExtractMetadata(obj);
        
        // Start Coroutine via EditorCoroutine utility (mocked here)
        // In real Unity Editor, we'd use EditorCoroutineUtility
        Debug.Log($"[Qyntara] validating {obj.name}...");
        
        // Simulating the call for the script generation purpose
        // QyntaraSDK.ValidateAsset(selectedIndustry, metaJson, OnResponse);
    }

    private string ExtractMetadata(GameObject obj)
    {
        int polycount = 0;
        MeshFilter mf = obj.GetComponent<MeshFilter>();
        if (mf != null && mf.sharedMesh != null)
        {
            polycount = mf.sharedMesh.triangles.Length / 3;
        }

        return string.Format("{{\"polycount\": {0}, \"name\": \"{1}\"}}", polycount, obj.name);
    }
}
