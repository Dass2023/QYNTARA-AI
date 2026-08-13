
import re
import json

class HeuristicEngine:
    """
    Advanced Logic for Parameter Optimization.
    Simulates 'Future AI' reasoning by applying checks based on context.
    """
    
    @staticmethod
    def select_generation_model(prompt):
        """
        Algorithm: Chooses generation method based on prompt content.
        Spec: Hard-surface -> Hunyuan3D / TRELLIS, Organic -> Point-E / Shap-E.
        """
        prompt = prompt.lower()
        
        # Hard Surface / ArchViz Keywords
        hard_surface_keys = ["crate", "box", "robot", "car", "building", "weapon", "mech", "armor", "table", "chair"]
        if any(k in prompt for k in hard_surface_keys):
            return "hunyuan3d" # or trellis
            
        # Organic / Soft Keywords
        organic_keys = ["character", "creature", "animal", "plant", "flower", "face", "monster", "tree"]
        if any(k in prompt for k in organic_keys):
            return "point-e"
            
        return "balanced" # Default

    @staticmethod
    def refine_remesh(args):
        """Optimizes remesh settings based on target count and implied object type."""
        # 1. High Poly Rule
        if args.get("target_count", 0) > 20000:
            args["adaptive"] = True
            
        # 2. Curvature Classifier (Simulated)
        # In the future, this calls an ONNX model to check mesh curvature
        if args.get("target_count", 0) < 1000:
             # Low poly fallback logic could go here
             pass
             
        return args

    @staticmethod
    def refine_material(args):
        """Optimizes material settings based on prompt keywords and Physics-Aware Logic."""
        p = args.get("prompt", "")
        
        # 1. Transparent Materials
        if any(x in p for x in ["glass", "water", "ice", "crystal", "liquid"]):
            args["transmission"] = 1.0
            args["roughness"] = 0.05
            args["ior"] = 1.45
            
        # 2. Metallic Materials
        elif any(x in p for x in ["gold", "metal", "silver", "chrome", "copper", "steel"]):
            args["metallic"] = 1.0
            args["roughness"] = 0.2
            
        # 3. Physics-Aware Suggestions (Friction/Roughness)
        elif "polished" in p:
             args["roughness"] = 0.1
        elif "worn" in p or "rough" in p:
             args["roughness"] = 0.8
             
        return args

    @staticmethod
    def refine_uv(args):
        """Applies SeamGPT logic logic."""
        # Future: If 'hidden seams' requested, enable SeamGPT mode
        return args

class MCPBridgeStub:
    """
    Future-Proofing: This class will handle JSON-RPC calls to the external MCP Server.
    Currently acts as a pass-through.
    """
    @staticmethod
    def send_tool_call(tool, args):
        print(f"MCP CALL: {tool} -> {args}")
        return True

class AgentBrain:
    """
    The Intelligence Layer.
    Translates Natural Language -> Structured Job Envelopes (JSON).
    """
    
    @staticmethod
    def parse_intent(text, context=None):
        """
        Analyzes text and returns a (tool_name, args_dict) tuple.
        """
        text = text.lower()
        context = context or {}
        
        # --- 1. GENERATE AI ---
        if any(w in text for w in ["generate", "create", "make a"]):
            prompt = re.sub(r"generate|create|make a|make an", "", text).strip()
            
            # Smart Model Selection
            model = HeuristicEngine.select_generation_model(prompt)
            
            args = {
                "prompt": prompt,
                "model": model, # Injected by Heuristics
                "quality": "high" if "high" in text else "medium",
                "format": "glb"
            }
            return "generate_ai", args
            
        # --- 2. QUAD REMESH ---
        elif any(w in text for w in ["remesh", "retopo", "topology", "quads"]):
            target = 5000 
            match = re.search(r"(\d+)[k]?", text)
            if match:
                val = int(match.group(1))
                target = val * 1000 if "k" in match.group(0) else val
                
            args = {
                "target_count": target,
                "adaptive": "adaptive" in text,
                "symmetry": "symmetry" in text
            }
            # Apply AI Heuristics
            args = HeuristicEngine.refine_remesh(args)
            return "quad_remesh", args
            
        # --- 3. MATERIAL AI ---
        elif any(w in text for w in ["material", "texture", "shader", "look like"]):
            prompt = re.sub(r"material|texture|make it look like|apply|assign", "", text).strip()
            args = {
                "prompt": prompt,
                "resolution": 2048 if "2k" in text else 1024,
                "workflow": "pbr"
            }
            # Apply AI Heuristics
            args = HeuristicEngine.refine_material(args)
            return "material_ai", args
            
        # --- 4. VALIDATE ---
        elif any(w in text for w in ["validate", "check", "health", "fix", "inspect"]):
            return "validate_scene", {
                "fix_ngons": "fix" in text,
                "check_uvs": "uv" in text,
                "profile": "unreal" if "unreal" in text else "unity" if "unity" in text else "general"
            }
            
        # --- 5. UNIVERSAL UV ---
        elif any(w in text for w in ["uv", "unwrap", "map"]):
            # SeamGPT Intent
            mode = "auto"
            if "seam" in text or "smart" in text:
                mode = "seam_gpt"
                
            return "universal_uv", {
                "resolution": 2048,
                "mode": mode,
                "margin": 0.05
            }
            
        return None, None

    @staticmethod
    def construct_job_envelope(tool, args, context):
        """Builds the Master Spec JSON Envelope."""
        return {
            "job_id": "auto_generated",
            "module": tool,
            "scene_context": context,
            "pipeline_flags": {f"run_{tool}": True},
            "settings": {
                tool: args
            }
        }
