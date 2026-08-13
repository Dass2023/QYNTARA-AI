#include "QyntaraSubsystem.h"
#include "HttpModule.h"
#include "Interfaces/IHttpResponse.h"

void UQyntaraSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	UE_LOG(LogTemp, Log, TEXT("Qyntara AI Subsystem Initialized."));
}

void UQyntaraSubsystem::ValidateAsset(FString AssetName, FString Industry, FString MetadataJson)
{
	FHttpModule* Http = &FHttpModule::Get();
	TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = Http->CreateRequest();

	Request->OnProcessRequestComplete().BindUObject(this, &UQyntaraSubsystem::OnResponseReceived);
	
	// Construct JSON Payload
	FString Payload = FString::Printf(TEXT("{\"industry\": \"%s\", \"metadata\": %s}"), *Industry.ToLower(), *MetadataJson);

	Request->SetURL("http://localhost:8008/validate/core");
	Request->SetVerb("POST");
	Request->SetHeader("Content-Type", "application/json");
	Request->SetContentAsString(Payload);

	UE_LOG(LogTemp, Warning, TEXT("Sending Qyntara Request for: %s"), *AssetName);
	Request->ProcessRequest();
}

void UQyntaraSubsystem::OnResponseReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful)
{
	if (bWasSuccessful && Response.IsValid())
	{
		FString content = Response->GetContentAsString();
		UE_LOG(LogTemp, Log, TEXT("Qyntara Response: %s"), *content);
		OnValidationComplete.Broadcast(content);
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("Qyntara API connection failed."));
	}
}
