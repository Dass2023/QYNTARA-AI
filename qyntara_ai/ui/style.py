
# Premium Dark Theme for Qyntara AI
STYLESHEET = """
QWidget {
    background-color: #1a1a1a;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 13px;
}

/* --- Headers & Labels --- */
QLabel {
    color: #cccccc;
}
QLabel#headerTitle {
    font-size: 20px;
    font-weight: bold;
    color: #ffffff;
    padding: 0px;
}
QLabel#sectionTitle {
    font-weight: 600;
    color: #888888;
    margin-top: 10px;
    text-transform: uppercase;
    font-size: 10px;
    letter-spacing: 1.2px;
}
QLabel#metricLabel {
    font-size: 36px;
    font-weight: 300;
    color: #00CEC9; /* Premium Teal */
}

/* --- Buttons --- */
QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 8px 16px;
    color: #f0f0f0;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #383838;
    border-color: #555;
}
QPushButton:pressed {
    background-color: #00CEC9;
    color: #111;
    border-color: #00CEC9;
}
QPushButton:disabled {
    background-color: #222;
    color: #555;
    border-color: #2a2a2a;
}

/* Action Buttons */
QPushButton#primaryAction {
    background-color: #00CEC9;
    color: #111;
    border: 1px solid #00b5b5;
    font-weight: bold;
}
QPushButton#primaryAction:hover {
    background-color: #00e0db;
}
QPushButton#fixAction {
    background-color: #2d2d2d;
    color: #00CEC9;
    border: 1px solid #00CEC9;
}
QPushButton#fixAction:hover {
    background-color: #00CEC9;
    color: #111;
}

/* --- Tabs --- */
QTabWidget::pane {
    border: 1px solid #333;
    background: #111111;
    border-radius: 6px;
}
QTabWidget::tab-bar {
    left: 10px; 
}
QTabBar::tab {
    background: transparent;
    color: #888;
    border: none;
    padding: 10px 16px;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #00CEC9;
    border-bottom: 2px solid #00CEC9;
}
QTabBar::tab:hover {
    color: #ddd;
}

/* --- Progress Bar --- */
QProgressBar {
    border: none;
    background-color: #2d2d2d;
    border-radius: 2px;
    height: 4px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #00CEC9;
    border-radius: 2px;
}

/* --- Logs / Console --- */
QTextEdit#logConsole {
    background-color: #111111;
    border: 1px solid #333;
    font-family: 'Consolas', monospace;
    font-size: 11px;
    color: #aaa;
    border-radius: 6px;
    padding: 5px;
}

/* --- Rule Items (Card Design) --- */
QFrame#ruleItem {
    background-color: #222222;
    border: 1px solid #333;
    border-radius: 8px;
    margin-bottom: 4px;
}
QFrame#ruleItem:hover {
    background-color: #2a2a2a;
    border: 1px solid #444;
}
QFrame#ruleItemError {
    background-color: rgba(248, 81, 73, 0.1); /* Subtle Red Tint */
    border: 1px solid #5a1e1e;
    border-left: 4px solid #f85149;
    border-radius: 8px;
}
QFrame#ruleItemWarning {
    background-color: rgba(210, 153, 34, 0.1); /* Subtle Gold Tint */
    border: 1px solid #4a3b1e;
    border-left: 4px solid #d29922;
    border-radius: 8px;
}
QFrame#ruleItemPass {
    background-color: rgba(46, 160, 67, 0.05);
    border: 1px solid #1e3a25;
    border-left: 4px solid #2ea043;
    border-radius: 8px;
}

/* --- Scroll Area --- */
QScrollArea {
    border: none;
    background: transparent;
}
QWidget#scrollContent {
    background-color: #1a1a1a;
}

/* --- Metric Label --- */
QLabel#metricLabel {
    font-family: 'Segoe UI', sans-serif;
    font-size: 28px;
    font-weight: 300;
    color: #00CEC9;
}

/* --- Bottom Action Bar --- */
QFrame#bottomFrame {
    background-color: #202020;
    border-top: 1px solid #333;
    min-height: 120px;
}
"""
