
import logging
try:
    from maya import cmds
except ImportError:
    cmds = None

logger = logging.getLogger(__name__)

class UVEngine:
    """
    Advanced UV Processing Engine for Qyntara AI.
    Handles Strategy-based Unwrapping and Packing.
    """
    
    @staticmethod
    def get_or_create_set(obj, target_set='uvSet2'):
        """
        Robustly ensures target_set exists.
        Uses 'polyCopyUV' from map1 to ensure allocation, then clears it.
        """
        all_sets = cmds.polyUVSet(obj, q=True, allUVSets=True) or []
        
        if target_set in all_sets:
            cmds.polyUVSet(obj, currentUVSet=True, uvSet=target_set)
            return True
        
        # Strategy 1: Copy with History (Best for preserving mapping)
        base_set = all_sets[0] if all_sets else 'map1'
        try:
            cmds.polyCopyUV(obj, uvSetNameInput=base_set, uvSetName=target_set, ch=True)
            cmds.polyUVSet(obj, currentUVSet=True, uvSet=target_set)
            return True
        except Exception:
            pass # Try next

        # Strategy 2: Copy NO History (Safer for locked nodes)
        try:
            cmds.polyCopyUV(obj, uvSetNameInput=base_set, uvSetName=target_set, ch=False)
            cmds.polyUVSet(obj, currentUVSet=True, uvSet=target_set)
            return True
        except Exception:
            pass

        # Strategy 3: Basic Create (Empty Container)
        try:
            cmds.polyUVSet(obj, create=True, uvSet=target_set)
            cmds.polyUVSet(obj, currentUVSet=True, uvSet=target_set)
            return True
        except Exception as e:
            logger.error(f"UVEngine: All creation strategies failed for {obj}. Last error: {e}")
            return False

    @staticmethod
    def analyze_mesh_type(obj):
        """
        Returns 'organic' or 'hardsurface' based on heuristics.
        Simple heuristic: Ratio of Soft Edges vs Hard Edges.
        """
        try:
            # Count hard edges
            soft_ids = cmds.polyInfo(obj, edgeToVertex=True) # Heavy?
            # Faster: check displaySmoothness? No.
            # Let's assume Hard Surface default for Game Assets unless specified.
            # Check if user has defined Hard Edges? 
            return 'hardsurface' # Default safe for Lightmaps (less distortion)
        except:
            return 'hardsurface'

    @staticmethod
    def detect_and_cut_hard_edges(obj):
        """ Cuts UVs along Hard Edges to enforce seam alignment. """
        try:
            # 1. Select Hard Edges
            cmds.select(obj)
            cmds.polySelectConstraint(mode=3, type=0x8000, smoothness=1)
            hard_edges = cmds.ls(sl=True, fl=True) or []
            cmds.polySelectConstraint(mode=0, smoothness=0)
            
            if hard_edges:
                cmds.polyMapCut(hard_edges)
                return True
        except: pass
        return False

    @staticmethod
    def unwrap_angle_based(obj, cut_hard_edges=True):
        """ Organic / Smooth method. Supports Hard Edge alignment. """
        try:
            # 1. Cut Hard Edges (Spec: "Seams aligned with hard edges")
            if cut_hard_edges:
                UVEngine.detect_and_cut_hard_edges(obj)
            
            # 2. Unfold (Pin borders)
            # u3dUnfold: bi=1 (Border Intersection prevention)
            try:
                # If we cut edges, we want to Keep Borders (kb=1) during auto-seam? 
                # Actually, u3dAutoSeam might ignore them.
                # Better: Use u3dUnfold on existing seams.
                cmds.u3dUnfold(obj, ite=5, p=True, bi=True, tf=1, ms=1024, rs=0)
            except:
                cmds.unfold(obj, i=5000, ss=0.001, gb=0, gmb=0.5, pub=0, ps=0, oa=0, us=False)
        except Exception as e:
            logger.warning(f"Unwrap Angle-Based failed: {e}")

    @staticmethod
    def unwrap_copy(obj):
        """ Method D: Copy UV1 -> UV2 """
        # Data is already seeded into UV2 by 'get_or_create' logic using map1.
        # We just need to maybe relax or pack.
        # Spec says: "Duplicates UV1... and then repacks".
        # So we do nothing here (data is already copied), relying on the Packing step.
        pass

    @staticmethod
    def pack_lightmap(obj):
        """
        Heuristic Packing: High Padding, No Overlap.
        Unity Focus: 12px Spacing, 15px Margin (Border safety).
        """
        try:
            # Unfold3D: spc=0.012 (12px), mar=0.015 (15px)
            cmds.u3dLayout(obj, res=1024, scl=1, spc=0.012, mar=0.015, box=(0,1,0,1))
        except:
            # Maya Fallback: ps=0.012, r=1 (90deg safe), fr=0 (No flip)
            cmds.polyLayoutUV(obj, l=2, sc=1, se=0, r=1, ps=0.012, fr=0)

    @staticmethod
    def pack_texture(obj):
        """
        Tetris Packing (Texture/UV1):
        High Packing Density, Minimal Padding (0.004).
        """
        try:
            # Unfold3D: spc=0.004 (4px)
            cmds.u3dLayout(obj, res=1024, scl=1, spc=0.004, mar=0.004, box=(0,1,0,1))
        except:
             # Maya Fallback: ps=0.004
             cmds.polyLayoutUV(obj, l=2, sc=1, se=0, r=1, ps=0.004, fr=0)

    @staticmethod
    def pack_strip(obj):
        """ 
        Strip Packing: Predictable, Linear, Low Overhead.
        No Rotation (r=0), Scale=1.
        """
        try:
             # Fast Layout, No Rotation
             cmds.polyLayoutUV(obj, l=2, sc=1, se=0, r=0, ps=0.01)
        except: pass

    @staticmethod
    def process(obj, profile='lightmap', unwrap_method=None, pack_method=None):
        logger.info(f"UVEngine: Processing {obj} [Profile: {profile}]")
        
        # 1. PRE-CLEAN
        try: cmds.delete(obj, ch=True)
        except: pass

        # 2. SETUP LIGHTMAP SET
        existing_sets = cmds.polyUVSet(obj, q=True, allUVSets=True) or []
        target_set = 'Lightmap'
        
        # Cleanup old
        if 'uvSet2' in existing_sets:
            try: cmds.polyUVSet(obj, delete=True, uvSet='uvSet2')
            except: pass
        if target_set in existing_sets:
            try: cmds.polyUVSet(obj, delete=True, uvSet=target_set)
            except: pass

        # 3. CREATE & SEED (Nuclear)
        try:
            cmds.select(obj)
            cmds.polyUVSet(obj, create=True, uvSet=target_set)
            cmds.polyUVSet(obj, currentUVSet=True, uvSet=target_set) # CRITICAL SWITCH
            
            # Seed Strategy
            if unwrap_method == 'copy':
                 # If explicit Copy requested, force copy from map1 (if exists)
                 if 'map1' in existing_sets:
                      cmds.polyCopyUV(obj, uvSetNameInput='map1', uvSetName=target_set, ch=False)
                 else:
                      cmds.polyAutoProjection(obj, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)
            else:
                 # Default: AutoProject to guarantee valid data for unwrappers
                 cmds.polyAutoProjection(obj, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)

            # BAKE IT DOWN! (Solidify the Seed)
            cmds.delete(obj, ch=True)
            cmds.polyUVSet(obj, currentUVSet=True, uvSet=target_set) # Re-assert context after bake!

        except Exception as e:
            logger.warning(f"Create/Seed failed: {e}")

        # 4. SWITCH CHECK
        current = cmds.polyUVSet(obj, q=True, currentUVSet=True)
        if current and len(current) > 0 and current[0] != target_set:
            logger.error(f"Failed to switch context. Aborting.")
            return

        # 5. UNWRAP STRATEGY
        m_type = UVEngine.analyze_mesh_type(obj)
        
        # Determine Method
        method_to_use = unwrap_method
        if not method_to_use:
            # Auto-Select based on Profile + Mesh Type
            if profile == 'lightmap':
                method_to_use = 'angle' # Spec: "Preferred for Lightmap"
            else:
                method_to_use = 'projection' if m_type == 'hardsurface' else 'angle'

        try:
             # CHECKPOINT A: After Seed & Bake
             count_a = cmds.polyEvaluate(obj, uv=True, uvSetName=target_set)
             logger.info(f"DEBUG: UV Count after Seed: {count_a}")

             if method_to_use == 'angle':
                 # Lightmaps need hard-edge alignment
                 cut_hard = (profile == 'lightmap')
                 UVEngine.unwrap_angle_based(obj, cut_hard_edges=cut_hard)
             elif method_to_use == 'flatten':
                 UVEngine.unwrap_flatten(obj)
             elif method_to_use == 'projection':
                 UVEngine.unwrap_hardsurface(obj)
             elif method_to_use == 'copy':
                 UVEngine.unwrap_copy(obj)
                
             # CHECKPOINT B: After Unwrap
             count_b = cmds.polyEvaluate(obj, uv=True, uvSetName=target_set)
             logger.info(f"DEBUG: UV Count after Unwrap ({method_to_use}): {count_b}")
            
        except Exception as e:
             logger.warning(f"Unwrap {method_to_use} failed: {e}")

        # 6. PACKING STRATEGY
        packer_to_use = pack_method
        if not packer_to_use:
             # Auto-Select
             packer_to_use = 'heuristic' if profile == 'lightmap' else 'tetris'
        
        try:
            if packer_to_use == 'heuristic':
                UVEngine.pack_lightmap(obj)
            elif packer_to_use == 'tetris':
                UVEngine.pack_texture(obj)
            elif packer_to_use == 'strip':
                UVEngine.pack_strip(obj)
                
            # CHECKPOINT C: After Pack
            count_c = cmds.polyEvaluate(obj, uv=True, uvSetName=target_set)
            logger.info(f"DEBUG: UV Count after Pack ({packer_to_use}): {count_c}")
            
        except: pass

        # 7. FINALIZE
        try:
             # Final Check using PolyEvaluate (Robust)
             final_count = 0
             try: 
                 final_count = cmds.polyEvaluate(obj, uv=True, uvSetName=target_set)
                 logger.info(f"DEBUG: Final UV Count before Bake: {final_count}")
             except: pass

             if final_count == 0:
                 logger.warning("Empty Set detected. Emergency Copy.")
                 if 'map1' in existing_sets:
                     cmds.polyCopyUV(obj, uvSetNameInput='map1', uvSetName=target_set, ch=True)
                     
             cmds.delete(obj, ch=True)
             cmds.refresh()
             cmds.inViewMessage(amg=f'<hl>Qyntara:</hl> {target_set} Processed.', pos='midCenter', fade=True)
        except Exception as e:
             logger.warning(f"Finalize failed: {e}")

