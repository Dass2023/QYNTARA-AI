import os

target_file = r"I:\QYNTARA AI\maya\qyntara_client.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if line.startswith("    def generate_html_report(self):"):
        start_idx = i
        break

if start_idx != -1:
    method_lines = lines[start_idx:]
    # Remove from end
    lines = lines[:start_idx]
    
    # Find insertion point (before # --- Close Window Before Open ---)
    insert_idx = -1
    for i in range(len(lines)):
        if lines[i].startswith("# --- Close Window Before Open ---"):
            insert_idx = i
            break
            
    if insert_idx != -1:
        # Insert method lines
        lines.insert(insert_idx, "\n")
        for line in reversed(method_lines):
            lines.insert(insert_idx, line)
            
        with open(target_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("Moved generate_html_report inside QyntaraDockable class.")
    else:
        print("Could not find insert_idx")
else:
    print("Could not find start_idx of generate_html_report")

