import sys
import unittest
from unittest.mock import MagicMock

# Mock Maya
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()

# Mock PySide for Headless Env
try:
    from PySide2.QtGui import QImage, QColor
except ImportError:
    class QImage:
        Format_Grayscale8 = 1
        Format_RGB32 = 2
        def __init__(self, path): pass
        def isNull(self): return False
        def convertToFormat(self, f): return self
        def width(self): return 100
        def height(self): return 100
        def pixel(self, x, y): return 0 
            
    class QColor:
        def __init__(self, *args): pass
        def value(self): return 0

    sys.modules["PySide2"] = MagicMock()
    sys.modules["PySide2.QtGui"] = MagicMock()
    sys.modules["PySide2.QtGui"].QImage = QImage
    sys.modules["PySide2.QtGui"].QColor = QColor

from qyntara_ai.core.floorplan_builder import SmartVectorization, Vector2

class TestSmartVectorization(unittest.TestCase):
    def setUp(self):
        self.vec = SmartVectorization()
        
    def test_gap_closing(self):
        # Create two segments that are collinear and close to each other
        # horizontal line y=10, from x=0 to x=50
        # another from x=60 to x=100
        # Gap is 10px. Should merge (threshold is 30)
        
        segments = [
            (Vector2(0, 10), Vector2(50, 10)),
            (Vector2(60, 10), Vector2(100, 10))
        ]
        
        clean = self.vec.regularize_lines(segments)
        # Should result in ONE segment from 0 to 100
        self.assertEqual(len(clean), 1)
        
        p1, p2 = clean[0]
        self.assertEqual(p1.x, 0)
        self.assertEqual(p2.x, 100) # Merged end
        self.assertEqual(p1.y, 12.0) # Snapped to nearest 12
        
    def test_noise_filtering_post_merge(self):
        # Create a small isolated segment
        # length 10px. Should be filtered out (threshold 40px in regularize)
        segments = [
            (Vector2(200, 50), Vector2(210, 50))
        ]
        
        clean = self.vec.regularize_lines(segments)
        self.assertEqual(len(clean), 0)

if __name__ == '__main__':
    unittest.main()
