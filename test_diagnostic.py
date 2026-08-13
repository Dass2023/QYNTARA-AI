import sys
import os

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

import maya
print("maya module:", maya)
print("maya path:", getattr(maya, '__path__', None))
print("maya file:", getattr(maya, '__file__', None))

import maya.qyntara_client
print("SUCCESS!")
