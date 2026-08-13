#pragma once

#include "CoreMinimal.h"
#include "EditorSubsystem.h"
#include "Http.h"
#include "QyntaraSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnValidationComplete, const FString&, JsonResponse);

/**
 * Validates active assets against Qyntara Core API.
 */
UCLASS()
class QYNTARAUNREAL_API UQyntaraSubsystem : public UEditorSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	/** Sends asset metadata to http://localhost:8008/validate/core */
	UFUNCTION(BlueprintCallable, Category = "Qyntara AI")
	void ValidateAsset(FString AssetName, FString Industry, FString MetadataJson);

	UPROPERTY(BlueprintAssignable, Category = "Qyntara AI")
	FOnValidationComplete OnValidationComplete;

private:
	void OnResponseReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
};
