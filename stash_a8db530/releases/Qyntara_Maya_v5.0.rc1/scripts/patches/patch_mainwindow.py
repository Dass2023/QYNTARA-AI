import os

target_file = r"e:\QYNTARA AI\qyntara_ai\ui\main_window.py"
search_str = 'self.tabs.addTab(self.tab_scanner, "Scanner")'
insert_str = '\n\n        from .blueprint_tab import BlueprintWidget\n        self.tab_blueprint = BlueprintWidget()\n        self.tabs.addTab(self.tab_blueprint, "Blueprint Studio")'

if os.path.exists(target_file):
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "BlueprintWidget" in content:
        print("Already patched.")
    elif search_str in content:
        new_content = content.replace(search_str, search_str + insert_str)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully patched main_window.py")
    else:
        print("Error: Search string not found.")
else:
    print("Error: File not found.")
