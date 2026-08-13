
"""
Qyntara AI - UI Demo Automation
Runs a 'Self-Driving' UI sequence for Screen Recording purposes.
Usage:
    import run_ui_demo_mode
    run_ui_demo_mode.run_demo()
"""
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
    except ImportError:
        raise ImportError("Could not find PySide2 or PySide6. Ensure you are running this script inside Maya.")
import maya.cmds as cmds

def find_main_window():
    app = QtWidgets.QApplication.instance()
    for widget in app.topLevelWidgets():
        if "Qyntara AI Validator" in widget.windowTitle():
            return widget
    return None

class DemoDriver(QtCore.QObject):
    def __init__(self, win):
        super(DemoDriver, self).__init__()
        self.win = win
        self.step = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.next_step)
        
    def start(self):
        print("--- Starting UI Demo Sequence (5s Delay) ---")
        print("PREPARE SCREEN RECORDING NOW...")
        QtCore.QTimer.singleShot(5000, self.next_step)

    def highlight(self, widget, color="#ff00ff"):
        # simple flash effect
        orig = widget.styleSheet()
        widget.setStyleSheet(f"border: 2px solid {color}; background: #444;")
        QtCore.QTimer.singleShot(200, lambda: widget.setStyleSheet(orig))

    def type_text(self, widget, text, interval=50):
        # Simulate Typing
        widget.clear()
        self.typing_text = text
        self.typing_widget = widget
        self.typing_idx = 0
        self.type_timer = QtCore.QTimer()
        self.type_timer.timeout.connect(self._type_char)
        self.type_timer.start(interval)
        
    def _type_char(self):
        if self.typing_idx < len(self.typing_text):
            char = self.typing_text[self.typing_idx]
            self.typing_widget.insert(char)
            self.typing_idx += 1
        else:
            self.type_timer.stop()

    def next_step(self):
        self.step += 1
        print(f"Demo Step: {self.step}")
        
        if self.step == 1:
            # 1. Focus Industry 4.0
            self.win.tabs.setCurrentIndex(0) # Logic index might vary, checking...
            # The tabs were added: 0=Ind4, 1=Ind5, 2=Val? 
            # In code: Validation was added at Index 2 usually. Ind4 at 0.
            # Let's try name match
            for i in range(self.win.tabs.count()):
                if "INDUSTRY 4.0" in self.win.tabs.tabText(i):
                    self.win.tabs.setCurrentIndex(i)
                    break
            self.timer.start(2000)

        elif self.step == 2:
            # 2. Type Asset ID
            # Access widget from tab instance
            tab = self.win.tab_industry40
            self.type_text(tab.txt_id, "ASSET-8842-X")
            self.timer.start(2000)

        elif self.step == 3:
            # 3. Click Connect
            tab = self.win.tab_industry40
            self.highlight(tab.btn_sync)
            tab.btn_sync.click() # Real click
            self.timer.start(3000)

        elif self.step == 4:
            # 4. Switch to Validation
            for i in range(self.win.tabs.count()):
                if "Validation" in self.win.tabs.tabText(i):
                    self.win.tabs.setCurrentIndex(i)
                    break
            self.timer.start(2000)

        elif self.step == 5:
            # 5. Click Validate
            self.highlight(self.win.btn_validate)
            self.win.btn_validate.click()
            self.timer.start(4000)

        elif self.step == 6:
            # 6. Click Auto-Fix
            self.highlight(self.win.btn_fix)
            self.win.btn_fix.click()
            self.timer.start(3000)

        elif self.step == 7:
            # 7. Switch to Industry 5.0
            for i in range(self.win.tabs.count()):
                if "INDUSTRY 5.0" in self.win.tabs.tabText(i):
                    self.win.tabs.setCurrentIndex(i)
                    break
            self.timer.start(2000)

        elif self.step == 8:
            # 8. Evolve Design
            self.highlight(self.win.tab_industry50.btn_evolve)
            self.win.tab_industry50.btn_evolve.click()
            self.timer.start(5000) # Wait for evolution

        elif self.step == 9:
            # 9. Neural Link
            self.highlight(self.win.tab_industry50.btn_neural_connect)
            self.win.tab_industry50.btn_neural_connect.click()
            self.timer.start(3000)

        elif self.step == 10:
            print("--- Starting Full Suite Walkthrough ---")
            # Iterate through remaining tabs (Alignment, UVs, Baking, Export, Scanner, Blueprint)
            # Find generic tabs by name or index
            self.current_tab_idx = 3 # Starting after Ind5 (which is usually around 2 or 3 depending on insert order)
            # Check actual count
            self.total_tabs = self.win.tabs.count()
            self.timer.start(500)

        elif self.step > 10 and self.step < 20:
             # Dynamic Tab Cycle
             idx = self.step - 11 + 3 # Logic: step 11 -> tab 3
             if idx < self.win.tabs.count():
                 self.win.tabs.setCurrentIndex(idx)
                 tab_name = self.win.tabs.tabText(idx)
                 print(f"Showing Tab: {tab_name}")
                 self.timer.start(3000) # Give 3s to look at it
             else:
                 self.step = 20 # Done
                 self.timer.start(100)

        elif self.step == 21:
            print("--- Demo Complete ---")
            self.timer.stop()

# Global reference to keep alive
_driver = None

def run_demo():
    global _driver
    win = find_main_window()
    if not win:
        print("Error: Qyntara Window not found. Open it first.")
        return
    
    win.raise_()
    win.activateWindow()
    
    _driver = DemoDriver(win)
    _driver.start()
