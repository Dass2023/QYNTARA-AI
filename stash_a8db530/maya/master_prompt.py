
import maya.cmds as cmds
import maya.api.OpenMaya as om2
import json

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

# --- Styling Constants ---
NEON_CYAN = "#00f3ff"
NEON_PURPLE = "#bc13fe"
BG_DARK = "#0a0a0c"
BG_PANEL = "#111115"
BORDER_COLOR = "#333"

class ScopeChip(QtWidgets.QPushButton):
    """Selectable chip for defining agent scope."""
    def __init__(self, label, parent=None):
        super(ScopeChip, self).__init__(label, parent)
        self.setCheckable(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFixedHeight(24)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid #444;
                border-radius: 12px;
                color: #888;
                padding: 0px 12px;
                font-size: 10px;
                font-family: 'Consolas', monospace;
            }}
            QPushButton:hover {{ border-color: {NEON_CYAN}; color: #fff; }}
            QPushButton:checked {{ 
                background-color: {NEON_CYAN}; 
                border-color: {NEON_CYAN}; 
                color: #000; 
                font-weight: bold;
            }}
        """)

class ChatInput(QtWidgets.QTextEdit):
    """Auto-expanding chat input with Enter-to-submit."""
    submitRequested = QtCore.Signal()

    def __init__(self, parent=None):
        super(ChatInput, self).__init__(parent)
        self.setPlaceholderText("Ask Qyntara to generate, edit, or validate...")
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: #1a1a1d;
                border: 1px solid #333;
                border-radius: 8px;
                color: #fff;
                padding: 8px;
                font-size: 13px;
                selection-background-color: {NEON_PURPLE};
            }}
            QTextEdit:focus {{ border: 1px solid {NEON_CYAN}; }}
        """)
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return and not event.modifiers():
            self.submitRequested.emit()
        else:
            super(ChatInput, self).keyPressEvent(event)

class AgentMessage(QtWidgets.QFrame):
    """A chat bubble for User/Agent messages."""
    def __init__(self, text, sender="user", parent=None):
        super(AgentMessage, self).__init__(parent)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        lbl = QtWidgets.QLabel(text)
        lbl.setWordWrap(True)
        
        if sender == "user":
            lbl.setStyleSheet(f"""
                background-color: #222; 
                color: #ccc; 
                border-radius: 8px; 
                padding: 8px;
                font-size: 12px;
            """)
            layout.addStretch()
            layout.addWidget(lbl)
        else:
            # Agent
            lbl.setStyleSheet(f"""
                background-color: rgba(188, 19, 254, 0.2); 
                color: {NEON_CYAN}; 
                border: 1px solid rgba(188, 19, 254, 0.4);
                border-radius: 8px; 
                padding: 8px;
                font-size: 12px;
            """)
            layout.addWidget(lbl)
            layout.addStretch()

class MasterPromptWidget(QtWidgets.QFrame):
    """The Agentic Command Center."""
    commandSignal = QtCore.Signal(str, dict) # text, context

    def __init__(self, parent=None):
        super(MasterPromptWidget, self).__init__(parent)
        self.setStyleSheet(f"background-color: {BG_PANEL}; border-bottom: 1px solid #222;")
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 1. Header (Logo + Status Tiny)
        header_layout = QtWidgets.QHBoxLayout()
        logo = QtWidgets.QLabel("QYNTARA")
        logo.setStyleSheet("font-weight: 900; color: #fff; letter-spacing: 3px; font-size: 14px;")
        ai_tag = QtWidgets.QLabel("AGENT")
        ai_tag.setStyleSheet(f"color: {NEON_CYAN}; font-weight: 300; font-size: 14px; letter-spacing: 2px;")
        
        self.status_dot = QtWidgets.QLabel("●")
        self.status_dot.setStyleSheet("color: #444; margin-left: 10px;")
        self.status_lbl = QtWidgets.QLabel("IDLE")
        self.status_lbl.setStyleSheet("color: #666; font-size: 10px; font-family: 'Consolas';")
        
        header_layout.addWidget(logo)
        header_layout.addWidget(ai_tag)
        header_layout.addWidget(self.status_dot)
        header_layout.addWidget(self.status_lbl)
        header_layout.addStretch()
        
        # 1b. Auth/Settings Button (Tiny)
        self.btn_settings = QtWidgets.QPushButton("⚙")
        self.btn_settings.setStyleSheet("background: transparent; color: #666; border: none;")
        header_layout.addWidget(self.btn_settings)
        
        layout.addLayout(header_layout)

        # 2. Scope Bar
        scope_layout = QtWidgets.QHBoxLayout()
        scope_layout.setSpacing(8)
        self.chips = []
        for label in ["SELECTION", "HIERARCHY", "SCENE", "PROJECT"]:
            chip = ScopeChip(label)
            if label == "SELECTION": chip.setChecked(True)
            scope_layout.addWidget(chip)
            self.chips.append(chip)
        scope_layout.addStretch()
        layout.addLayout(scope_layout)
        
        # 3. Chat History (New)
        self.history_scroll = QtWidgets.QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setStyleSheet("background: transparent; border: none;")
        self.history_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.history_scroll.setFixedHeight(120) # Defined height
        
        self.history_container = QtWidgets.QWidget()
        self.history_layout = QtWidgets.QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.addStretch() # Push messages down
        
        self.history_scroll.setWidget(self.history_container)
        layout.addWidget(self.history_scroll)
        
        # Initial Welcome Message
        self.add_message("Qyntara Agent Ready. Waiting for input...", "agent")

        # 4. Chat Input Row
        input_layout = QtWidgets.QHBoxLayout()
        
        self.chat_input = ChatInput()
        self.chat_input.submitRequested.connect(self.submit_prompt)
        
        self.btn_mic = QtWidgets.QPushButton("🎤")
        self.btn_mic.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_mic.setFixedSize(40, 40)
        self.btn_mic.setStyleSheet(f"""
            QPushButton {{
                background-color: #222;
                border: 1px solid #444;
                border-radius: 20px;
                color: {NEON_CYAN};
                font-size: 16px;
            }}
            QPushButton:hover {{ background-color: #333; }}
        """)
        
        self.btn_send = QtWidgets.QPushButton("⚡")
        self.btn_send.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_send.setFixedSize(40, 40)
        self.btn_send.setStyleSheet(f"""
            QPushButton {{
                background-color: {NEON_PURPLE};
                border: none;
                border-radius: 8px;
                color: #fff;
                font-size: 16px;
            }}
            QPushButton:hover {{ background-color: #d05ce3; }}
        """)
        self.btn_send.clicked.connect(self.submit_prompt)

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.btn_mic)
        input_layout.addWidget(self.btn_send)
        layout.addLayout(input_layout)
        
    def submit_prompt(self):
        text = self.chat_input.toPlainText().strip()
        if not text: return
        
        # Add User Message to History
        self.add_message(text, "user")
        
        # Gather Context
        context = {
            "scope": [c.text() for c in self.chips if c.isChecked()]
        }
        
        # Emit
        self.commandSignal.emit(text, context)
        self.chat_input.clear()
        self.status_lbl.setText("PROCESSING...")
        self.status_dot.setStyleSheet(f"color: {NEON_PURPLE}; margin-left: 10px;")

    def add_message(self, text, sender):
        """Adds a bubble to the history."""
        msg = AgentMessage(text, sender)
        # Add before the stretch item
        self.history_layout.insertWidget(self.history_layout.count()-1, msg)
        # Scroll to bottom
        bar = self.history_scroll.verticalScrollBar()
        QtCore.QTimer.singleShot(10, lambda: bar.setValue(bar.maximum()))

    def set_status(self, text, state="idle"):
        self.status_lbl.setText(text.upper())
        color = "#444"
        if state == "active": color = NEON_CYAN
        elif state == "success": color = "#00ff9d"
        elif state == "error": color = NEON_RED
        elif state == "processing": color = NEON_PURPLE
        self.status_dot.setStyleSheet(f"color: {color}; margin-left: 10px;")
        
        if state in ["success", "error"]:
             self.add_message(text, "agent")

