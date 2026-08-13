
import os

path = r"e:/QYNTARA AI/qyntara_ai/core/geometry.py"

with open(path, 'r') as f:
    lines = f.readlines()

# Lines to remove are 248 to 278 (inclusive 1-based)
# 0-based index: 247 to 277
start_idx = 247 
end_idx = 277 

print(f"Total lines before: {len(lines)}")
print(f"Removing lines {start_idx+1} to {end_idx+1}:")
print("--- START DELETED CONTENT ---")
for i in range(start_idx, end_idx + 1):
    print(lines[i], end='')
print("--- END DELETED CONTENT ---")

new_lines = lines[:start_idx] + lines[end_idx+1:]

print(f"Total lines after: {len(new_lines)}")

with open(path, 'w') as f:
    f.writelines(new_lines)
    
print("Cleanup complete.")
