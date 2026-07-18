import subprocess
import time
import requests

def run():
    print("============================================================")
    print("PHASE 2 QDRANT PERSISTENCE VERIFICATION")
    print("============================================================")
    
    print("Starting Qdrant via Docker Compose...")
    subprocess.run(["docker-compose", "up", "-d", "qdrant"], cwd="I:\\QYNTARA AI", check=True)
    
    print("Waiting 3 seconds for Qdrant to boot...")
    time.sleep(3)
    
    print("Testing connection...")
    resp = requests.get("http://localhost:6333/")
    print(f"Qdrant Info: {resp.json()}")
    
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams
    from qdrant_client.http.models import PointStruct
    
    client = QdrantClient(url="http://localhost:6333")
    
    collection_name = "test_persistence"
    
    if not client.collection_exists(collection_name):
        print(f"Creating collection '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=4, distance=Distance.COSINE),
        )
    
    print("Inserting test vector...")
    client.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=1,
                vector=[0.05, 0.61, 0.76, 0.74],
                payload={"city": "Berlin"}
            )
        ]
    )
    
    print("Stopping Qdrant container (simulating backend/docker restart)...")
    subprocess.run(["docker-compose", "stop", "qdrant"], cwd="I:\\QYNTARA AI", check=True)
    time.sleep(2)
    
    print("Starting Qdrant container again...")
    subprocess.run(["docker-compose", "start", "qdrant"], cwd="I:\\QYNTARA AI", check=True)
    time.sleep(3)
    
    client2 = QdrantClient(url="http://localhost:6333")
    print("Retrieving vector after restart...")
    points = client2.retrieve(
        collection_name=collection_name,
        ids=[1]
    )
    
    if points:
        print(f"SUCCESS: Vector 1 retrieved: {points[0].payload}")
    else:
        print("FAILED: Vector not found after restart!")
        
    print("Cleaning up collection...")
    client2.delete_collection(collection_name)
    
    print("Stopping Qdrant container...")
    subprocess.run(["docker-compose", "stop", "qdrant"], cwd="I:\\QYNTARA AI", check=True)

if __name__ == "__main__":
    run()
