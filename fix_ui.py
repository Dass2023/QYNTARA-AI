import os

target_file = r"I:\QYNTARA AI\maya\qyntara_client.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. We want to remove lines from 1454 (Tool Bar in Block 1) down to just before Tab 1 (GENERATE AI)
start_remove = -1
end_remove = -1

for i in range(len(lines)):
    if "# Tool Bar" in lines[i] and "btn_run_val = QtWidgets.QPushButton" in lines[i+2]:
        # This is the first Tool Bar
        start_remove = i
        break

for i in range(start_remove, len(lines)):
    if "# --- Tab 1: GENERATE AI ---" in lines[i]:
        end_remove = i
        break

if start_remove != -1 and end_remove != -1:
    print(f"Removing redundant block from {start_remove} to {end_remove}")
    del lines[start_remove:end_remove]

# 2. Add the REPORT button to the real Validator Tab (Block 2, which is now shifted up)
insert_idx = -1
for i in range(len(lines)):
    if "self.btn_heatmap = QtWidgets.QPushButton" in lines[i]:
        insert_idx = i
        break

if insert_idx != -1:
    report_btn_code = """
        # Restore HTML Report Button
        self.btn_html_report = QtWidgets.QPushButton("REPORT")
        self.btn_html_report.setStyleSheet("background-color: #444; color: white; font-weight: bold;")
        self.btn_html_report.setCursor(PointingHandCursor)
        self.btn_html_report.clicked.connect(self.generate_html_report)
        val_toolbar.addWidget(self.btn_html_report)
"""
    lines.insert(insert_idx, report_btn_code)
    print("Inserted REPORT button into correct toolbar.")

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("UI Layout fixed!")
