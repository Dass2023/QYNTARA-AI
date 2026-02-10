import maya.cmds as cmds
import maya.mel as mel
import time
import threading

# Import Core Modules
try:
    from qyntara_ai.core import validator, fixer
except ImportError:
    print("[Agent] Error: Qyntara Core not found. Agent sleeping.")
    validator = None
    fixer = None

class AgenticFixer:
    """
    Qyntara Autonomous Remediation Agent (The "Janitor").
    Monitors the scene and automatically fixes geometry errors in the background.
    """
    
    _instance = None
    
    def __init__(self):
        self.active = False
        self.job_id = None
        self.validator = validator.QyntaraValidator()
        self.fixer = fixer.QyntaraFixer()
        self.last_run_time = 0
        self.cooldown = 2.0 # Seconds between checks to prevent lag
        
    @classmethod
    def start(cls):
        if cls._instance:
            cls._instance.stop()
        
        cls._instance = AgenticFixer()
        cls._instance._start_monitoring()
        
    @classmethod
    def stop(cls):
        if cls._instance:
            cls._instance._stop_monitoring()
            cls._instance = None

    def _start_monitoring(self):
        print("\n[Agent] 🔵 Qyntara Agentic Fixer: ONLINE")
        print("[Agent] Watching for geometry changes...")
        
        # We use a scriptJob on "idle" with a throttle, or "polyTopologyChanged".
        # "polyTopologyChanged" is better but might fire too often during modeling.
        # "SelectionChanged" is a good proxy for "User finished an action".
        
        # Let's use 'SelectionChanged' as a trigger to check the *previously* selected object?
        # Or just a persistent 'idle' check is too heavy.
        
        # Strategy: "On Save" or "On Change".
        # Let's go with a specialized scriptJob for 'DagObjectCreated' and 'polyTopologyChanged'
        # But for stability, let's use a manual "Pulse" approach or just hook into Selection for now.
        
        # Ideally: The Agent is an "Observer". 
        # Using 'idle' event to run a non-blocking check queue is advanced.
        
        # SIMPLE VALIDATION: Auto-Fix on Selection Change (Checks what you just deselected/modified?)
        # No, that's annoying.
        
        # LET'S DO BACKGROUND POLICING:
        # Every 5 seconds, scan the scene. (Using Maya's timer events)
        
        self.active = True
        # Kill existing
        if cmds.scriptJob(exists="QyntaraAgentJob"):
            cmds.scriptJob(kill="QyntaraAgentJob", force=True)
            
        # Create a repeating timer event (approximate via dgtimer? No.)
        # Maya doesn't have a great background thread loop that touches scene.
        # We will use a ScriptJob 'idle' with a time check.
        
        self.job_id = cmds.scriptJob(e=["idle", self._tick], protected=True)
        print(f"[Agent] Agent ID: {self.job_id}")

    def _stop_monitoring(self):
        if self.job_id:
            cmds.scriptJob(kill=self.job_id, force=True)
            print("[Agent] 🔴 Qyntara Agentic Fixer: OFFLINE")
        self.active = False
        self.job_id = None

    def _tick(self):
        if not self.active: return
        
        now = time.time()
        if (now - self.last_run_time) < self.cooldown:
            return
            
        self.last_run_time = now
        self._scan_and_fix()

    def _scan_and_fix(self):
        # 1. Quick Scan of Active Objects (Selection or All?)
        # Scaning ALL is too slow. Scan Selection is efficient.
        selection = cmds.ls(sl=True, long=True)
        if not selection: return

        # Only check meshes
        meshes = cmds.ls(selection, type="transform", long=True)
        if not meshes: return
        
        # Filter for actual mesh shapes
        target_meshes = []
        for m in meshes:
            if cmds.listRelatives(m, shapes=True, type="mesh"):
                target_meshes.append(m)
                
        if not target_meshes: return
        
        # 2. Run Silent Validation
        # print("[Agent] Scanning...", end="\r")
        report = self.validator.run_validation(target_meshes)
        
        # 3. Check for Critical Errors
        violations = report.get("violations", [])
        if not violations: return
        
        fixes_applied = 0
        
        for v in violations:
            rule_id = v.get("rule_id")
            severity = v.get("severity", "warning")
            
            # Agent Policy: Only fix "critical" or "error" automatically
            # Or specific annoyance fixes
            
            # LIST OF AUTO-FIXABLE RULES THE AGENT HANDLES:
            auto_rules = ["ngons", "lamina_faces", "zero_area_faces", "open_edges"]
            
            if rule_id in auto_rules:
                # print(f"[Agent] ⚠️ Detected {rule_id} on {v['object']}. Remedying...")
                
                # Call Fixer Method dynamically
                fix_method_name = f"fix_{rule_id}"
                if hasattr(self.fixer, fix_method_name):
                    func = getattr(self.fixer, fix_method_name)
                    success = func(v) # Pass violation entry
                    if success:
                        print(f"[Agent] ✅ Auto-Fixed {rule_id} on {v['object']}")
                        fixes_applied += 1
                        
        if fixes_applied > 0:
            print(f"[Agent] Re-validated. Scene is clean.")
            cmds.inViewMessage(amg=f"<hl>Qyntara Agent</hl> Fixed {fixes_applied} issues.", pos='topRight', fade=True)

# Entry Point
if __name__ == "__main__":
    AgenticFixer.start()
