import os
import json
import logging
import time

logger = logging.getLogger(__name__)

class ReinforcementLoop:
    """
    Qyntara RLHF (The Teacher).
    
    Responsible for:
    - Recording user feedback (Accept/Reject/Fix).
    - Calculating 'Reward' signals for the generative models.
    - Closing the loop between User Intent and Model Output.
    
    Current Implementation: v2.0-Alpha (Local JSON Storage)
    """
    
    def __init__(self, log_path=None):
        if not log_path:
            base_dir = os.path.expanduser("~/.qyntara/brain")
            os.makedirs(base_dir, exist_ok=True)
            log_path = os.path.join(base_dir, "rlhf_events.json")
            
        self.log_path = log_path
        self._ensure_log_exists()
        logger.info(f"RLHF Loop initialized. Logging to: {self.log_path}")

    def _ensure_log_exists(self):
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w') as f:
                json.dump([], f)

    def record_feedback(self, asset_id, action, context=None):
        """
        Logs a user interaction event.
        
        Args:
            asset_id (str): ID of the asset.
            action (str): 'ACCEPT', 'REJECT', 'FIX_UV', 'FIX_GEO', etc.
            context (dict): State of the scene/tool at time of action.
        """
        event = {
            "timestamp": time.time(),
            "asset_id": asset_id,
            "action": action,
            "context": context or {}
        }
        
        try:
            with open(self.log_path, 'r+') as f:
                data = json.load(f)
                data.append(event)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
            
            logger.info(f"RLHF Event Recorded: {action} on {asset_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return False

    def calculate_model_score(self, model_version="v1.0"):
        """
        Calculates a simple success rate for a model based on history.
        """
        try:
            with open(self.log_path, 'r') as f:
                data = json.load(f)
                
            relevant = [d for d in data if d.get("context", {}).get("model") == model_version]
            if not relevant:
                return 0.0
                
            accepts = len([d for d in relevant if d["action"] == "ACCEPT"])
            total = len(relevant)
            
            return (accepts / total) * 100.0
        except:
            return 0.0
            
    def get_stats(self):
        return {
            "status": "ONLINE",
            "learning_mode": "ACTIVE",
            "total_events": self._count_events()
        }

    def _count_events(self):
        try:
            with open(self.log_path, 'r') as f:
                return len(json.load(f))
        except:
            return 0
