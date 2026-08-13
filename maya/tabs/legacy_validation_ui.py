try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

class RuleWidget(QtWidgets.QFrame):
    fixRequested = QtCore.Signal(str) 

    def __init__(self, rule_data, parent=None):
        super(RuleWidget, self).__init__(parent)
        self.rule_data = rule_data
        self.setObjectName("ruleItem")
        
        # Context Menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setChecked(rule_data.get("enabled", True))
        layout.addWidget(self.checkbox)
        
        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(2)
        
        header_row = QtWidgets.QHBoxLayout()
        self.lbl_name = QtWidgets.QLabel(f"<b>{rule_data['label']}</b>")
        self.lbl_name.setStyleSheet("font-size: 13px; color: #fff;")
        header_row.addWidget(self.lbl_name)
        header_row.addStretch()
        text_layout.addLayout(header_row)
        
        self.lbl_desc = QtWidgets.QLabel(rule_data.get("description", ""))
        self.lbl_desc.setStyleSheet("color: #888; font-size: 11px;")
        text_layout.addWidget(self.lbl_desc)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.lbl_status = QtWidgets.QLabel("READY")
        self.lbl_status.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_status.setStyleSheet("""
            color: #ffffff; 
            font-weight: 800; 
            background: #444444; 
            padding: 8px 16px; 
            border-radius: 6px;
            font-size: 11px;
            letter-spacing: 1px;
        """)
        layout.addWidget(self.lbl_status)

        # Base Card Style
        self.setStyleSheet("""
            #ruleItem {
                background: rgba(20, 20, 25, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-left: 3px solid #444;
                border-radius: 8px;
                margin-bottom: 2px;
            }
            #ruleItem:hover {
                background: rgba(30, 30, 35, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-left: 3px solid #666;
            }
        """)

    def show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        fix_action = menu.addAction("Auto-Fix Issue")
        fix_action.triggered.connect(lambda: self.fixRequested.emit(self.rule_data['id']))
        menu.exec_(self.mapToGlobal(pos))
        
    def update_visuals(self, new_data):
        self.rule_data.update(new_data)
        enabled = self.rule_data.get("enabled", True)
        self.checkbox.setChecked(enabled)
        self.setVisible(enabled)

    def set_status(self, violation_count, severity):
        base_style = "font-weight: 800; padding: 8px 16px; border-radius: 6px; font-size: 11px; letter-spacing: 1px;"
        
        if violation_count > 0:
            self.lbl_status.setText(f"{violation_count} ISSUES")
            if severity == "error":
                self.lbl_status.setStyleSheet(f"color: #ff3366; background: rgba(255, 51, 102, 0.15); border: 1px solid rgba(255, 51, 102, 0.3); {base_style}")
                self.setStyleSheet("""
                    #ruleItemError {
                        background: rgba(20, 20, 25, 0.6);
                        border: 1px solid rgba(255, 51, 102, 0.2);
                        border-left: 4px solid #ff3366;
                        border-radius: 8px;
                        margin-bottom: 2px;
                    }
                    #ruleItemError:hover {
                        background: rgba(255, 51, 102, 0.05);
                        border: 1px solid rgba(255, 51, 102, 0.4);
                        border-left: 4px solid #ff3366;
                    }
                """)
                self.setObjectName("ruleItemError")
            else:
                self.lbl_status.setStyleSheet(f"color: #ffb703; background: rgba(255, 183, 3, 0.15); border: 1px solid rgba(255, 183, 3, 0.3); {base_style}")
                self.setStyleSheet("""
                    #ruleItemWarning {
                        background: rgba(20, 20, 25, 0.6);
                        border: 1px solid rgba(255, 183, 3, 0.2);
                        border-left: 4px solid #ffb703;
                        border-radius: 8px;
                        margin-bottom: 2px;
                    }
                    #ruleItemWarning:hover {
                        background: rgba(255, 183, 3, 0.05);
                        border: 1px solid rgba(255, 183, 3, 0.4);
                        border-left: 4px solid #ffb703;
                    }
                """)
                self.setObjectName("ruleItemWarning")
        else:
            self.lbl_status.setText("PASS")
            self.lbl_status.setStyleSheet(f"color: #00e676; background: rgba(0, 230, 118, 0.15); border: 1px solid rgba(0, 230, 118, 0.3); {base_style}")
            self.setStyleSheet("""
                #ruleItemPass {
                    background: rgba(20, 20, 25, 0.6);
                    border: 1px solid rgba(0, 230, 118, 0.2);
                    border-left: 4px solid #00e676;
                    border-radius: 8px;
                    margin-bottom: 2px;
                }
                #ruleItemPass:hover {
                    background: rgba(0, 230, 118, 0.05);
                    border: 1px solid rgba(0, 230, 118, 0.4);
                    border-left: 4px solid #00e676;
                }
            """)
            self.setObjectName("ruleItemPass")
            
        self.style().unpolish(self)
        self.style().polish(self)
    
    def reset(self):
        self.lbl_status.setText("READY")
        self.lbl_status.setStyleSheet("""
            color: #ffffff; 
            font-weight: 800; 
            background: #444444; 
            padding: 8px 16px; 
            border-radius: 6px;
            font-size: 11px;
            letter-spacing: 1px;
        """)
        self.setStyleSheet("""
            #ruleItem {
                background: rgba(20, 20, 25, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-left: 3px solid #444;
                border-radius: 8px;
                margin-bottom: 2px;
            }
            #ruleItem:hover {
                background: rgba(30, 30, 35, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-left: 3px solid #666;
            }
        """)
        self.setObjectName("ruleItem")
        self.style().unpolish(self)
        self.style().polish(self)


class CollapsibleCategory(QtWidgets.QWidget):
    def __init__(self, title="", parent=None):
        super(CollapsibleCategory, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 5)
        self.layout.setSpacing(0)

        self.toggle_btn = QtWidgets.QPushButton(f"⬢  VIEW {title}")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                text-align: center; 
                background-color: rgba(5, 10, 8, 0.95);
                color: #888888; 
                font-weight: 800; 
                font-size: 13px;
                letter-spacing: 2px;
                padding: 10px; 
                border-top: 1px dotted rgba(136, 136, 136, 0.5);
                border-bottom: 1px dotted rgba(136, 136, 136, 0.5);
                border-left: none;
                border-right: none;
                border-radius: 4px;
                margin-bottom: 15px;
            }
            QPushButton:hover { 
                background-color: rgba(136, 136, 136, 0.1); 
                color: #aaaaaa;
            }
        """)
        self.toggle_btn.toggled.connect(self.toggle_content)
        self.layout.addWidget(self.toggle_btn)

        self.content_area = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(10, 5, 5, 10)
        self.content_layout.setSpacing(2)
        self.layout.addWidget(self.content_area)
        
        self.title = title
        self.content_area.setVisible(self.toggle_btn.isChecked())

    def toggle_content(self, checked):
        self.content_area.setVisible(checked)
        self.toggle_btn.setText(f"⬢  VIEW {self.title}")

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def reset(self):
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                text-align: center; 
                background-color: rgba(5, 10, 8, 0.95);
                color: #888888; 
                font-weight: 800; 
                font-size: 13px;
                letter-spacing: 2px;
                padding: 10px; 
                border-top: 1px dotted rgba(136, 136, 136, 0.5);
                border-bottom: 1px dotted rgba(136, 136, 136, 0.5);
                border-left: none;
                border-right: none;
                border-radius: 4px;
                margin-bottom: 15px;
            }
            QPushButton:hover { 
                background-color: rgba(136, 136, 136, 0.1); 
                color: #aaaaaa;
            }
        """)
        
    def set_status(self, severity):
        if severity == "error":
            color = "#ff3366"
            hover_color = "#ff4d79"
            bg_color = "rgba(255, 51, 102, 0.05)"
            border_color = "rgba(255, 51, 102, 0.5)"
        elif severity == "warning":
            color = "#ffb703"
            hover_color = "#ffc333"
            bg_color = "rgba(255, 183, 3, 0.05)"
            border_color = "rgba(255, 183, 3, 0.5)"
        else:
            # Pass
            color = "#00e676"
            hover_color = "#00ff9d"
            bg_color = "rgba(0, 230, 118, 0.05)"
            border_color = "rgba(0, 230, 118, 0.5)"
            
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                text-align: center; 
                background-color: {bg_color};
                color: {color}; 
                font-weight: 800; 
                font-size: 13px;
                letter-spacing: 2px;
                padding: 10px; 
                border-top: 1px dotted {border_color};
                border-bottom: 1px dotted {border_color};
                border-left: none;
                border-right: none;
                border-radius: 4px;
                margin-bottom: 15px;
            }}
            QPushButton:hover {{ 
                background-color: rgba(255, 255, 255, 0.05); 
                color: {hover_color};
            }}
        """)
