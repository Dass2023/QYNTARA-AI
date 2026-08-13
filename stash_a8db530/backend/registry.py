import json
import os
import time
from typing import List, Dict, Any, Optional
class AssetRegistry:
    def __init__(self, storage_path: str = "backend/data/registry.json"):
        self.storage_path = storage_path
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                return json.load(f)
        return {"assets": {}, "last_updated": 0}

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.data["last_updated"] = time.time()
        with open(self.storage_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def register_asset(self, asset_id: str, metadata: Dict[str, Any]):
        """Registers or updates an asset in the registry."""
        self.data["assets"][asset_id] = {
            "id": asset_id,
            "version": self.data["assets"].get(asset_id, {}).get("version", 0) + 1,
            "timestamp": time.time(),
            **metadata
        }
        self._save()
        return self.data["assets"][asset_id]

    def search_assets(self, query: str) -> List[Dict[str, Any]]:
        """Simple string search (Vector Store Removed)."""
        results = []
        for asset in self.data["assets"].values():
            if query.lower() in str(asset).lower():
                results.append(asset)
        return results

    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return self.data["assets"].get(asset_id)

    def list_assets(self) -> List[Dict[str, Any]]:
        return list(self.data["assets"].values())

    def delete_asset(self, asset_id: str):
        if asset_id in self.data["assets"]:
            del self.data["assets"][asset_id]
            self._save()
            return True
        return False

# Singleton instance
registry = AssetRegistry()
