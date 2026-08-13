// Qyntara Unreal Engine Plugin - Runtime SDK
// ==========================================
// 
// Import QMesh data into Unreal Engine's native types.
// Supports procedural mesh generation, materials, and Blueprint integration.
//
// Author: Dass2023
// License: MIT (Open-Core)
// Version: 5.0.0
// Unreal Engine: 5.0+

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ProceduralMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "QyntaraMeshComponent.generated.h"

/**
 * Qyntara mesh data structure matching Python QMesh format.
 */
USTRUCT(BlueprintType)
struct FQMeshData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    TArray<FVector> Vertices;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    TArray<int32> Triangles;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    TArray<FVector> Normals;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    TArray<FVector2D> UV0;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    TArray<FVector2D> UV1;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    TArray<FVector2D> UV2;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    TArray<FVector2D> UV3;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    TArray<FLinearColor> VertexColors;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    FString MeshName;
};

/**
 * Qyntara material properties for PBR conversion.
 */
USTRUCT(BlueprintType)
struct FQMaterialData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    FString MaterialName;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    FLinearColor BaseColor;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    float Metallic;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    float Roughness;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    UTexture2D* BaseColorTexture;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    UTexture2D* NormalTexture;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    UTexture2D* MetallicTexture;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    UTexture2D* RoughnessTexture;

    UPROPERTY(BlueprintReadWrite, Category = "Qyntara")
    UTexture2D* EmissiveTexture;
};

/**
 * Component for creating runtime procedural meshes from Qyntara data.
 * Blueprint-compatible and supports full PBR materials.
 */
UCLASS(ClassGroup = (Qyntara), meta = (BlueprintSpawnableComponent))
class QYNTARARUNTIME_API UQyntaraMeshComponent : public UProceduralMeshComponent
{
    GENERATED_BODY()

public:
    UQyntaraMeshComponent();

    /**
     * Create procedural mesh from QMesh data.
     * @param MeshData - Qyntara mesh structure
     * @param bCreateCollision - Generate collision mesh
     * @return Success status
     */
    UFUNCTION(BlueprintCallable, Category = "Qyntara")
    bool CreateMeshFromQData(const FQMeshData& MeshData, bool bCreateCollision = true);

    /**
     * Import GLB file and create mesh at runtime.
     * Uses Unreal's built-in glTF importer or GLTFRuntime plugin.
     * @param GLBPath - Path to .glb file
     * @return Created actor with mesh
     */
    UFUNCTION(BlueprintCallable, Category = "Qyntara")
    static AActor* ImportGLB(UWorld* World, const FString& GLBPath);

    /**
     * Create Unreal material from Qyntara material data.
     * @param MaterialData - PBR material properties
     * @param BaseMaterial - Optional master material (defaults to M_QyntaraPBR)
     * @return Dynamic material instance
     */
    UFUNCTION(BlueprintCallable, Category = "Qyntara")
    static UMaterialInstanceDynamic* CreateMaterialFromQData(
        const FQMaterialData& MaterialData,
        UMaterialInterface* BaseMaterial = nullptr
    );

    /**
     * Center mesh at origin.
     */
    UFUNCTION(BlueprintCallable, Category = "Qyntara|Mesh Processing")
    void CenterMesh();

    /**
     * Scale mesh uniformly.
     */
    UFUNCTION(BlueprintCallable, Category = "Qyntara|Mesh Processing")
    void ScaleMesh(float Scale);

    /**
     * Validate mesh for common issues.
     * @param OutIssues - Array of issue descriptions
     * @return True if mesh is valid (no issues)
     */
    UFUNCTION(BlueprintCallable, Category = "Qyntara|Mesh Processing")
    bool ValidateMesh(TArray<FString>& OutIssues);

protected:
    virtual void BeginPlay() override;

private:
    /** Helper: Get procedural mesh section */
    FProcMeshSection* GetMeshSection(int32 SectionIndex)
    {
        if (ProcMeshSections.IsValidIndex(SectionIndex))
        {
            return &ProcMeshSections[SectionIndex];
        }
        return nullptr;
    }
};


// ============================================================================
// Implementation (.cpp would be separate file, shown here for completeness)
// ============================================================================

UQyntaraMeshComponent::UQyntaraMeshComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UQyntaraMeshComponent::BeginPlay()
{
    Super::BeginPlay();
}

bool UQyntaraMeshComponent::CreateMeshFromQData(const FQMeshData& MeshData, bool bCreateCollision)
{
    if (MeshData.Vertices.Num() == 0 || MeshData.Triangles.Num() == 0)
    {
        UE_LOG(LogTemp, Error, TEXT("[Qyntara] Invalid mesh data: no vertices or triangles"));
        return false;
    }

    // Unreal uses left-handed Z-up, Qyntara uses right-handed Y-up
    // No conversion needed if already in Unreal space

    // Create procedural mesh section
    CreateMeshSection_LinearColor(
        0,                          // Section index
        MeshData.Vertices,
        MeshData.Triangles,
        MeshData.Normals,
        MeshData.UV0,
        MeshData.UV1,
        MeshData.UV2,
        MeshData.UV3,
        MeshData.VertexColors,
        TArray<FProcMeshTangent>(), // Tangents (auto-computed)
        bCreateCollision
    );

    UE_LOG(LogTemp, Log, TEXT("[Qyntara] Created mesh: %s"), *MeshData.MeshName);
    UE_LOG(LogTemp, Log, TEXT("  Vertices: %d"), MeshData.Vertices.Num());
    UE_LOG(LogTemp, Log, TEXT("  Triangles: %d"), MeshData.Triangles.Num() / 3);

    return true;
}

AActor* UQyntaraMeshComponent::ImportGLB(UWorld* World, const FString& GLBPath)
{
    if (!World)
    {
        UE_LOG(LogTemp, Error, TEXT("[Qyntara] Invalid world context"));
        return nullptr;
    }

    // Use Datasmith or glTFRuntime plugin for GLB import
    // This is a simplified example - production would use proper import pipeline

    UE_LOG(LogTemp, Warning, TEXT("[Qyntara] GLB import requires glTFRuntime plugin or Datasmith"));
    UE_LOG(LogTemp, Warning, TEXT("[Qyntara] Install: https://github.com/rdeioris/glTFRuntime"));

    // Placeholder - actual implementation would use:
    // UglTFRuntimeAsset* Asset = UglTFRuntimeFunctionLibrary::glTFLoadAssetFromFilename(GLBPath, ...);
    // AActor* Actor = Asset->CreateActorFromAsset(World);

    return nullptr;
}

UMaterialInstanceDynamic* UQyntaraMeshComponent::CreateMaterialFromQData(
    const FQMaterialData& MaterialData,
    UMaterialInterface* BaseMaterial)
{
    // Load default PBR master material if none provided
    if (!BaseMaterial)
    {
        // In production, this would load from:
        // /Qyntara/Materials/M_QyntaraPBR.M_QyntaraPBR
        BaseMaterial = LoadObject<UMaterial>(
            nullptr,
            TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial")
        );
    }

    if (!BaseMaterial)
    {
        UE_LOG(LogTemp, Error, TEXT("[Qyntara] Failed to load base material"));
        return nullptr;
    }

    // Create dynamic material instance
    UMaterialInstanceDynamic* DynMaterial = UMaterialInstanceDynamic::Create(
        BaseMaterial,
        nullptr,
        *MaterialData.MaterialName
    );

    if (!DynMaterial)
    {
        UE_LOG(LogTemp, Error, TEXT("[Qyntara] Failed to create dynamic material"));
        return nullptr;
    }

    // Set PBR parameters
    DynMaterial->SetVectorParameterValue(TEXT("BaseColor"), MaterialData.BaseColor);
    DynMaterial->SetScalarParameterValue(TEXT("Metallic"), MaterialData.Metallic);
    DynMaterial->SetScalarParameterValue(TEXT("Roughness"), MaterialData.Roughness);

    // Set textures if available
    if (MaterialData.BaseColorTexture)
    {
        DynMaterial->SetTextureParameterValue(TEXT("BaseColorTexture"), MaterialData.BaseColorTexture);
    }

    if (MaterialData.NormalTexture)
    {
        DynMaterial->SetTextureParameterValue(TEXT("NormalTexture"), MaterialData.NormalTexture);
    }

    if (MaterialData.MetallicTexture)
    {
        DynMaterial->SetTextureParameterValue(TEXT("MetallicTexture"), MaterialData.MetallicTexture);
    }

    if (MaterialData.RoughnessTexture)
    {
        DynMaterial->SetTextureParameterValue(TEXT("RoughnessTexture"), MaterialData.RoughnessTexture);
    }

    UE_LOG(LogTemp, Log, TEXT("[Qyntara] Created material: %s"), *MaterialData.MaterialName);

    return DynMaterial;
}

void UQyntaraMeshComponent::CenterMesh()
{
    FProcMeshSection* Section = GetMeshSection(0);
    if (!Section)
    {
        UE_LOG(LogTemp, Warning, TEXT("[Qyntara] No mesh section to center"));
        return;
    }

    // Compute bounding box
    FBox BoundingBox(ForceInit);
    for (const FProcMeshVertex& Vertex : Section->ProcVertexBuffer)
    {
        BoundingBox += Vertex.Position;
    }

    // Calculate offset
    FVector Center = BoundingBox.GetCenter();

    // Apply offset
    for (FProcMeshVertex& Vertex : Section->ProcVertexBuffer)
    {
        Vertex.Position -= Center;
    }

    // Update mesh
    UpdateMeshSection_LinearColor(
        0,
        Section->ProcVertexBuffer,
        Section->ProcIndexBuffer,
        TArray<FLinearColor>(),
        TArray<FProcMeshTangent>()
    );

    UE_LOG(LogTemp, Log, TEXT("[Qyntara] Centered mesh, offset: %s"), *Center.ToString());
}

void UQyntaraMeshComponent::ScaleMesh(float Scale)
{
    FProcMeshSection* Section = GetMeshSection(0);
    if (!Section)
    {
        UE_LOG(LogTemp, Warning, TEXT("[Qyntara] No mesh section to scale"));
        return;
    }

    // Scale vertices
    for (FProcMeshVertex& Vertex : Section->ProcVertexBuffer)
    {
        Vertex.Position *= Scale;
    }

    // Update mesh
    UpdateMeshSection_LinearColor(
        0,
        Section->ProcVertexBuffer,
        Section->ProcIndexBuffer,
        TArray<FLinearColor>(),
        TArray<FProcMeshTangent>()
    );

    UE_LOG(LogTemp, Log, TEXT("[Qyntara] Scaled mesh by %f"), Scale);
}

bool UQyntaraMeshComponent::ValidateMesh(TArray<FString>& OutIssues)
{
    OutIssues.Empty();

    FProcMeshSection* Section = GetMeshSection(0);
    if (!Section)
    {
        OutIssues.Add(TEXT("No mesh section found"));
        return false;
    }

    // Check vertex count
    if (Section->ProcVertexBuffer.Num() == 0)
    {
        OutIssues.Add(TEXT("Mesh has no vertices"));
    }

    // Check triangle count
    if (Section->ProcIndexBuffer.Num() == 0)
    {
        OutIssues.Add(TEXT("Mesh has no triangles"));
    }

    if (Section->ProcIndexBuffer.Num() % 3 != 0)
    {
        OutIssues.Add(TEXT("Triangle count not divisible by 3"));
    }

    // Check for degenerate triangles
    int32 DegenerateCount = 0;
    for (int32 i = 0; i < Section->ProcIndexBuffer.Num(); i += 3)
    {
        FVector V0 = Section->ProcVertexBuffer[Section->ProcIndexBuffer[i]].Position;
        FVector V1 = Section->ProcVertexBuffer[Section->ProcIndexBuffer[i + 1]].Position;
        FVector V2 = Section->ProcVertexBuffer[Section->ProcIndexBuffer[i + 2]].Position;

        float Area = FVector::CrossProduct(V1 - V0, V2 - V0).Size() / 2.0f;
        if (Area < 0.000001f)
        {
            DegenerateCount++;
        }
    }

    if (DegenerateCount > 0)
    {
        OutIssues.Add(FString::Printf(TEXT("%d degenerate triangles detected"), DegenerateCount));
    }

    UE_LOG(LogTemp, Log, TEXT("[Qyntara] Mesh validation: %d issues found"), OutIssues.Num());

    return OutIssues.Num() == 0;
}

// Helper removed from here, moved to class definition for accessibility
