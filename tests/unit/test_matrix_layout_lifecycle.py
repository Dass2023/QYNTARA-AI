import pytest
from unittest.mock import MagicMock, patch
try:
    from PySide2 import QtWidgets, QtCore
except ImportError:
    from PySide6 import QtWidgets, QtCore

from maya.qyntara_client import IndustryRoadmapDialog, _clear_layout
from maya.nexus_api_client import NexusAPIClient
from maya.industry_mapping import UI_LABEL_TO_INDUSTRY_KEY

@pytest.fixture
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

@pytest.fixture
def mock_parent():
    parent = MagicMock()
    parent.api_client = NexusAPIClient(base_url="http://localhost:8000")
    parent.api_client.token = "valid_lifecycle_token"
    return parent

def process_qt_events():
    app = QtWidgets.QApplication.instance()
    if app:
        app.processEvents()

def test_clear_layout_recursive_function(app):
    # Create parent widget and main layout
    parent_w = QtWidgets.QWidget()
    main_layout = QtWidgets.QVBoxLayout(parent_w)
    
    # Add top widget
    lbl = QtWidgets.QLabel("Top Label")
    main_layout.addWidget(lbl)
    
    # Add nested sub-layout with buttons
    sub_layout = QtWidgets.QHBoxLayout()
    btn1 = QtWidgets.QPushButton("Btn1")
    btn2 = QtWidgets.QPushButton("Btn2")
    sub_layout.addWidget(btn1)
    sub_layout.addWidget(btn2)
    main_layout.addLayout(sub_layout)
    
    # Add stretch spacer
    main_layout.addStretch()
    
    assert main_layout.count() == 3
    
    # Run _clear_layout
    _clear_layout(main_layout)
    process_qt_events()
    
    assert main_layout.count() == 0

def test_initial_dialog_creation(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.parent = lambda: mock_parent
    
    # Initial row is 0 (Gaming)
    assert dialog.det_layout is not None
    initial_count = dialog.det_layout.count()
    assert initial_count > 0

def test_single_industry_switch(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.parent = lambda: mock_parent
    
    initial_count = dialog.det_layout.count()
    dialog.update_details(1) # Switch to Film / VFX
    process_qt_events()
    
    # Layout count must not grow out of bounds
    assert dialog.det_layout.count() == initial_count

def test_repeated_switching_between_two_industries(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.parent = lambda: mock_parent
    
    expected_count = dialog.det_layout.count()
    
    for _ in range(10):
        dialog.update_details(0) # Gaming
        process_qt_events()
        assert dialog.det_layout.count() == expected_count
        
        dialog.update_details(1) # Film / VFX
        process_qt_events()
        assert dialog.det_layout.count() == expected_count

def test_repeated_switching_all_12_industries(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.parent = lambda: mock_parent
    
    expected_count = dialog.det_layout.count()
    
    for row in range(12):
        dialog.update_details(row)
        process_qt_events()
        assert dialog.det_layout.count() == expected_count

def test_rapid_random_switching(app, mock_parent):
    import random
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.parent = lambda: mock_parent
    
    expected_count = dialog.det_layout.count()
    
    for _ in range(30):
        row = random.randint(0, 11)
        dialog.update_details(row)
        process_qt_events()
        assert dialog.det_layout.count() == expected_count

def test_nested_layout_cleanup(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.parent = lambda: mock_parent
    
    # Find btn_layout before switch
    sub_layouts_before = [dialog.det_layout.itemAt(i).layout() for i in range(dialog.det_layout.count()) if dialog.det_layout.itemAt(i).layout() is not None]
    assert len(sub_layouts_before) == 1 # btn_layout
    
    old_sub_layout = sub_layouts_before[0]
    
    # Perform switch
    dialog.update_details(1)
    process_qt_events()
    
    # Verify old_sub_layout items are cleared
    assert old_sub_layout.count() == 0

def test_cloud_and_report_button_uniqueness(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.parent = lambda: mock_parent
    
    for _ in range(5):
        dialog.update_details(0)
        process_qt_events()
        
        # Count buttons in layout
        sub_layout = None
        for i in range(dialog.det_layout.count()):
            item = dialog.det_layout.itemAt(i)
            if item.layout():
                sub_layout = item.layout()
                break
        
        assert sub_layout is not None
        # Should have exactly 2 buttons in btn_layout (cloud_btn & report_btn)
        assert sub_layout.count() == 2

def test_signal_connection_single_execution(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.parent = lambda: mock_parent
    
    # Switch multiple times
    for _ in range(10):
        dialog.update_details(0)
        process_qt_events()
        
    call_count = 0
    def mock_run_analysis(key):
        nonlocal call_count
        call_count += 1
        
    dialog.run_cloud_analysis = mock_run_analysis
    
    # Find btn_cloud and trigger clicked
    sub_layout = [dialog.det_layout.itemAt(i).layout() for i in range(dialog.det_layout.count()) if dialog.det_layout.itemAt(i).layout()][0]
    btn_cloud = sub_layout.itemAt(0).widget()
    btn_cloud.click()
    
    assert call_count == 1 # Must execute EXACTLY once, not 10 times!

def test_100_repeated_switches_no_progressive_growth(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.parent = lambda: mock_parent
    
    expected_item_count = dialog.det_layout.count()
    
    for i in range(100):
        row = i % 12
        dialog.update_details(row)
        process_qt_events()
        assert dialog.det_layout.count() == expected_item_count

def test_roadmap_checkbox_tooltips_assigned(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.parent = lambda: mock_parent
    dialog.update_details(0)
    process_qt_events()
    
    checkboxes = []
    for i in range(dialog.det_layout.count()):
        item = dialog.det_layout.itemAt(i)
        if item.widget() and isinstance(item.widget(), QtWidgets.QCheckBox):
            checkboxes.append(item.widget())
            
    assert len(checkboxes) > 0
    for chk in checkboxes:
        assert chk.toolTip() == chk.text()

