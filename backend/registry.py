from typing import Dict, List, Optional
import os
import json

class AssetRegistry:
    def __init__(self):
        self.assets: Dict[str, dict] = {}
        self.db_path = "backend/data/registry.json"
        self._load()

    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    self.assets = json.load(f)
            except:
                self.assets = {}

    def _save(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w") as f:
            json.dump(self.assets, f, indent=2)

    def register_asset(self, asset_id: str, metadata: dict):
        self.assets[asset_id] = metadata
        self._save()

    def get_asset(self, asset_id: str) -> Optional[dict]:
        return self.assets.get(asset_id)

    def list_assets(self) -> List[dict]:
        return [{"id": k, **v} for k, v in self.assets.items()]

    def search_assets(self, query: str) -> List[dict]:
        return [
            {"id": k, **v} 
            for k, v in self.assets.items() 
            if query.lower() in k.lower() or query.lower() in str(v).lower()
        ]

registry = AssetRegistry()
