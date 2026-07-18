import maya.cmds as cmds
import importlib

# --- QYNTARA NEXUS TOPOLOGY OPTIMIZER DEMO ---
# Run this script inside the Maya Script Editor to see the Phase 1-4 features in action!

def setup_demo_scene():
    print("// [Qyntara Demo] Setting up test scene...")
    cmds.file(new=True, force=True)
    
    # Hero Object (Organic/Curvature testing)
    hero = cmds.polySphere(name="Hero_Asset", radius=5, subdivisionsX=40, subdivisionsY=40)[0]
    cmds.move(0, 5, 0, hero)
    
    # Factory Scan Data (Planar Snapping testing)
    factory = cmds.polyCube(name="Factory_Wall_Scan", width=10, height=10, depth=1, subdivisionsX=10, subdivisionsY=10)[0]
    cmds.move(-15, 5, 0, factory)
    
    # 50 Instances (Instancing Estimator testing)
    screw_master = cmds.polyCylinder(name="Screw_Master", radius=0.2, height=1, subdivisionsZ=1)[0]
    cmds.move(10, 0, 0, screw_master)
    
    screws = [screw_master]
    for i in range(1, 10):
        for j in range(5):
            new_screw = cmds.duplicate(screw_master, name=f"Screw_Clone_{i}_{j}")[0]
            cmds.move(10 + (i*0.5), 0, (j*0.5), new_screw)
            screws.append(new_screw)
            
    print("// [Qyntara Demo] Scene generation complete!")
    return hero, factory, screws

def run_demo():
    hero, factory, screws = setup_demo_scene()
    
    print("\n// --- INITIALIZING QYNTARA NEXUS TOPOLOGY ENGINE ---")
    try:
        from qyntara_ai.core.topology_engine import TopologyEngine
        import qyntara_ai.core.topology_engine
        importlib.reload(qyntara_ai.core.topology_engine)
        
        from qyntara_ai.core.mesh_optimizer import MeshOptimizer
        import qyntara_ai.core.mesh_optimizer
        importlib.reload(qyntara_ai.core.mesh_optimizer)
        
        engine = TopologyEngine()
        
        print("\n// 1. Testing Optimization & Instancing Estimator & Neural Layer")
        cmds.select(screws)
        # Ask the engine to optimize the screws to 20 faces.
        # It should run Neural Scan, identify 50 clones, reduce 1, and instance the rest.
        res = engine.tool_optimize_topology(target_faces=20, shield_shape=False, lock_uvs=True)
        print(f"Result: {res}")
        
        print("\n// 2. Testing Core Solvers: Planar Snapping")
        cmds.select(factory)
        res_planar = engine.analyze_intent_and_execute("Snap factory wall to planar contours")
        print(f"Result: {res_planar}")
        
        print("\n// 3. Testing UV AI Seam Placement")
        cmds.select(hero)
        res_seam = engine.analyze_intent_and_execute("Cut seams for Rizom")
        print(f"Result: {res_seam}")
        
        print("\n// 4. Testing LOD Matrix Batcher")
        cmds.select(hero)
        opt = MeshOptimizer()
        opt.generate_lod_chain([hero], levels=3)
        print("Result: LOD Chain generated in Outliner.")
        
        print("\n// [Qyntara Demo] All Systems Go! Check the Maya Outliner and Viewport.")
    except Exception as e:
        print(f"// [Qyntara Demo] Error running engine: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_demo()
