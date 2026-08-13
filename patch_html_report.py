import os

source_file = r"I:\QYNTARA AI\temp_backup\qyntara_ai\ui\main_window.py"
target_file = r"I:\QYNTARA AI\maya\qyntara_client.py"

with open(source_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith("    def generate_visual_report(self):"):
        start_idx = i
        break

if start_idx != -1:
    for i in range(start_idx + 1, len(lines)):
        if lines[i].startswith("    def ") or lines[i].startswith("class ") or lines[i].startswith("    # ---"):
            end_idx = i
            break
            
method_lines = lines[start_idx:end_idx]

# Rename the method
method_lines[0] = "    def generate_html_report(self):\n"

# Inject code to build self.last_report if it doesn't exist
mock_report_code = """
        # Build mock self.last_report from current val_tree
        self.last_report = {"summary": {"total_issues": 0, "health_score": 100}, "details": []}
        try:
            root = self.val_tree.invisibleRootItem()
            total = 0
            for i in range(root.childCount()):
                cat_item = root.child(i)
                for j in range(cat_item.childCount()):
                    item = cat_item.child(j)
                    # Use literal 256 + 3 for UserRole + 3
                    results = item.data(0, 256 + 3)
                    count = len(results) if results else 0
                    if count > 0:
                        total += count
                        self.last_report["details"].append({
                            "rule_id": item.text(0),
                            "description": item.data(0, 256 + 1) or "",
                            "failing_nodes": results,
                            "severity": item.data(0, 256 + 4) or "warning"
                        })
            self.last_report["summary"]["total_issues"] = total
            self.last_report["summary"]["health_score"] = max(0, 100 - total*5)
        except Exception as e:
            print("Warning building mock report:", e)

"""
method_lines.insert(1, mock_report_code)

with open(target_file, "a", encoding="utf-8") as f:
    f.writelines(method_lines)

print("Injected generate_html_report successfully.")
