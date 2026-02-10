import sys
import os
import traceback

# Ensure we can import backend modules
sys.path.append(os.getcwd())

print("Initializing TextTo3DGenerator...")
try:
    from backend.generative.text_to_3d import TextTo3DGenerator
    generator = TextTo3DGenerator()
    print("Generator initialized.")
    
    print("Attempting generation...")
    output = generator.generate("a futuristic chair", "debug_output.obj")
    print(f"Generation result: {output}")

except Exception:
    print("CRASHED!")
    traceback.print_exc()
