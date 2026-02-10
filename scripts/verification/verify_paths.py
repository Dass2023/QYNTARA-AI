
import os
import sys

print(f"CWD: {os.getcwd()}")
try:
    with open("path_test.txt", "w") as f:
        f.write("WRITE_SUCCESS")
    print("File Write: SUCCESS")
except Exception as e:
    print(f"File Write: FAILED - {e}")
