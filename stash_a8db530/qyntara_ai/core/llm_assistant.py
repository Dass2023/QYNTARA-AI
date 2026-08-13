import logging
import re

logger = logging.getLogger(__name__)

class LLMAssistant:
    """
    Simulates a Natural Language Processor (LLM) for Qyntara.
    Maps text inputs to internal function calls.
    
    Architecture:
    In production, this would call OpenAI API or a local Llama model.
    Here, we use 'Regex/Keyword Matching' to prototype the UX.
    """
    
    def __init__(self, main_window=None):
        self.main_window = main_window # Reference to UI to trigger actions
        
        # Knowledge Base of Actions
        # Format: (Regex Pattern, Description, Action Callback)
        self.intents = [
            (r"(run|start|check|do)\s+validation", "Run Validation", self._action_validate),
            (r"fix\s+(everything|all|issues|errors)", "Auto-Fix All", self._action_autofix),
            (r"(switch|change|set)\s+to\s+(game|unreal|unity)", "Set Profile: Game", lambda: self._action_profile("game")),
            (r"(switch|change|set)\s+to\s+(vfx|film|cinematic)", "Set Profile: VFX", lambda: self._action_profile("vfx")),
            (r"(switch|change|set)\s+to\s+(lidar|scan)", "Set Profile: LiDAR", lambda: self._action_profile("lidar")),
            (r"(clean|clear)\s+(scene|outliner)", "Clean Outliner", self._action_clean_scene)
        ]

    def process_prompt(self, text):
        """
        Parses text and returns a response string + execution result.
        """
        text = text.lower().strip()
        logger.info(f"AI Assistant received: '{text}'")
        
        for pattern, desc, callback in self.intents:
            if re.search(pattern, text):
                logger.info(f"Intent matched: {desc}")
                try:
                    callback()
                    return f"✅ Executed: {desc}"
                except Exception as e:
                    return f"❌ Error executing {desc}: {e}"
                    
        return "🤔 I didn't understand that. Try 'Run validation' or 'Fix all'."

    # --- Actions ---
    def _action_validate(self):
        if self.main_window:
            self.main_window.run_validation()
            
    def _action_autofix(self):
        if self.main_window:
            self.main_window.auto_fix()

    def _action_profile(self, profile_name):
        if self.main_window:
            # Map simple names to UI combos if needed, or just set validator
            # We need to update the UI Combo box to reflect state
            combo = self.main_window.combo_pipeline
            # Find index
            mapping = {"game": 0, "ar": 1, "vfx": 2, "web": 3} # Approximate indices based on UI
            # LiDAR isn't in main combo, handled implicitly.
            
            if profile_name == "lidar":
                self.main_window.validator.set_pipeline_profile("lidar")
                # Maybe switch tab?
                self.main_window.tabs.setCurrentIndex(5) # Scanner Tab
            else:
                # Update combo
                for i in range(combo.count()):
                    if profile_name in combo.itemText(i).lower():
                        combo.setCurrentIndex(i)
                        break

    def _action_clean_scene(self):
        # Specific utility call example
        from maya import cmds
        print("Cleaning Scene (Mock)...")
        # Could call qyntara_ai.core.scene.check_clean_outliner(fix=True) logic
