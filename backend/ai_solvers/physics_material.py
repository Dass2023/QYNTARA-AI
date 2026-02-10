
class PhysicsMaterialSolver:
    """
    AI-Powered Physical Property Estimation.
    
    Concept:
    Given a visual material name (e.g. "Rusty Iron"), infers:
    - Index of Refraction (IoR)
    - Friction Coefficient
    - Density
    - Restitution (Bounciness)
    """
    
    KNOWLEDGE_BASE = {
        "iron": {"ior": 2.9, "friction": 0.8, "density": 7870},
        "steel": {"ior": 2.5, "friction": 0.74, "density": 8050},
        "glass": {"ior": 1.5, "friction": 0.4, "density": 2500},
        "ice": {"ior": 1.31, "friction": 0.02, "density": 917},
        "rubber": {"ior": 1.5, "friction": 0.9, "density": 1100},
        "wood": {"ior": 1.5, "friction": 0.6, "density": 700},
        "concrete": {"ior": 1.5, "friction": 1.0, "density": 2400},
        "plastic": {"ior": 1.46, "friction": 0.35, "density": 1200}
    }
    
    @staticmethod
    def infer_properties(material_name: str):
        material_name = material_name.lower()
        
        # Simple Semantic Matching (Simulating NLP)
        best_match = None
        for key in PhysicsMaterialSolver.KNOWLEDGE_BASE:
            if key in material_name:
                best_match = PhysicsMaterialSolver.KNOWLEDGE_BASE[key]
                break
                
        if not best_match:
            # Default to "Generic Matte"
            return {"ior": 1.5, "friction": 0.5, "density": 1000, "type": "unknown"}
            
        return best_match
