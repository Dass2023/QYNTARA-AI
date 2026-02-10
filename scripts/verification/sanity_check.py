
import os
try:
    with open(r"e:\QYNTARA AI\sanity_check.txt", "w") as f:
        f.write("SANITY CHECK PASSED")
    print("Wrote file.")
except Exception as e:
    print(f"Failed: {e}")
