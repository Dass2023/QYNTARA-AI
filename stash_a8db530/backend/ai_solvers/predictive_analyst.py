
import random

class PredictiveAnalyst:
    """
    AI-Powered Pipeline Failure Prediction.
    
    Concept:
    Predicts if a mesh will fail later in the Game Engine pipeline (e.g. Nanite tessellation issues, 
    Lightmap overlapping) BEFORE exporting.
    """
    
    @staticmethod
    def predict_risk(context_data):
        """
        Input: Dict containing mesh stats.
        Output: Risk Assessment Report based on Game Engine constraints.
        """
        # Data from client
        polycount = context_data.get("polycount", 0)
        has_ngons = context_data.get("has_ngons", False)
        
        risk_score = 0.0
        reasons = []
        
        # 1. Polycount Thresholds (Standard UE5/Unity Logic)
        if polycount > 2000000:
             risk_score += 0.4
             reasons.append("Extreme Polycount (>2M) - Nanite Required")
        elif polycount > 100000:
             # Warning only
             risk_score += 0.1
             reasons.append("High Polycount - Check LODs")
            
        # 2. Topology Logic
        if has_ngons:
            risk_score += 0.5
            reasons.append("N-Gons Detected (Critical: Shading Artifacts)")
            
        # 3. Deterministic Heuristic (No longer random)
        # Check ratio
        if polycount < 100:
             risk_score += 0.1
             reasons.append("Low Polycount - Maybe Placeholder?")
             
        final_score = min(risk_score, 1.0)
            
        return {
            "risk_score": final_score,
            "safety_rating": "A" if final_score < 0.2 else "C" if final_score < 0.5 else "F",
            "prediction": "Safe to Export" if final_score < 0.4 else "Risk of Pipeline Failure",
            "reasons": reasons
        }
