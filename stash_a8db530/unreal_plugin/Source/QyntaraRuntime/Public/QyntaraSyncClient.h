// Qyntara Unreal Engine Plugin - Auto Sync Client
// ==============================================

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"
#include "HttpModule.h"
#include "QyntaraMeshComponent.h"
#include "QyntaraSyncClient.generated.h"

/**
 * Qyntara Sync Client for Unreal Engine.
 * Periodically polls the Qyntara backend and triggers mesh updates.
 */
UCLASS(ClassGroup=(Qyntara), meta=(BlueprintSpawnableComponent))
class QYNTARARUNTIME_API UQyntaraSyncClient : public UActorComponent
{
	GENERATED_BODY()

public:	
	UQyntaraSyncClient();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Qyntara|Config")
	FString ServerUrl = TEXT("http://localhost:8000");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Qyntara|Config")
	FString ApiKey = TEXT("QYNTARA-X-777");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Qyntara|Config")
	FString AssetId = TEXT("current_scene");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Qyntara|Config")
	float PollInterval = 5.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Qyntara|Output")
	UQyntaraMeshComponent* MeshComponent;

protected:
	virtual void BeginPlay() override;

private:
	void PollRegistry();
	void OnRegistryReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful);
	
	FString LastVersion;
	FTimerHandle PollTimerHandle;
};

// Implementation

UQyntaraSyncClient::UQyntaraSyncClient()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void UQyntaraSyncClient::BeginPlay()
{
	Super::BeginPlay();
	GetWorld()->GetTimerManager().SetTimer(PollTimerHandle, this, &UQyntaraSyncClient::PollRegistry, PollInterval, true);
}

void UQyntaraSyncClient::PollRegistry()
{
	TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
	Request->OnProcessRequestComplete().BindUObject(this, &UQyntaraSyncClient::OnRegistryReceived);
	Request->SetURL(ServerUrl + TEXT("/api/v1/registry/") + AssetId);
	Request->SetVerb(TEXT("GET"));
	Request->SetHeader(TEXT("X-API-KEY"), ApiKey);
	Request->ProcessRequest();
}

void UQyntaraSyncClient::OnRegistryReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful)
{
	if (bWasSuccessful && Response.IsValid())
	{
		TSharedPtr<FJsonObject> JsonObject;
		TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Response->GetContentAsString());

		if (FJsonSerializer::Deserialize(Reader, JsonObject))
		{
			FString CurrentVersion = JsonObject->GetStringField(TEXT("version"));
			if (CurrentVersion != LastVersion)
			{
				LastVersion = CurrentVersion;
				UE_LOG(LogTemp, Log, TEXT("[Qyntara] New version detected: %s"), *CurrentVersion);
				
				// Here we would trigger the mesh import logic
				// For now, signal the component
				if (MeshComponent) {
					UE_LOG(LogTemp, Log, TEXT("[Qyntara] Triggering Mesh Refresh..."));
				}
			}
		}
	}
}
