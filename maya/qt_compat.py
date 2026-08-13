"""
Qt Compatibility Layer for Qyntara Nexus.
Ensures we load exactly ONE Qt binding (PySide2 or PySide6) and never mix them.
Provides only the classes required by Qyntara.
Falls back to no-op stubs in environments without Qt (e.g. pytest headless).
"""
import sys

_qt_binding = None

import types

def _is_real_module(mod):
    """Return True only if mod is a genuine Python module, not a MagicMock."""
    return isinstance(mod, types.ModuleType)

def _detect_and_load():
    global _qt_binding
    if _qt_binding is not None:
        return

    # If PySide2/PySide6 is already imported AND is a real module (not a MagicMock
    # injected by conftest), use it.
    ps2 = sys.modules.get("PySide2")
    ps6 = sys.modules.get("PySide6")

    if ps2 is not None and _is_real_module(ps2):
        _qt_binding = "PySide2"
    elif ps6 is not None and _is_real_module(ps6):
        _qt_binding = "PySide6"
    else:
        # Try importing for real — also verify the result is not a MagicMock
        # (conftest seeds sys.modules with mocks, so 'import PySide2' may succeed
        # but return a fake module).
        try:
            import PySide2.QtCore as _ps2core
            if _is_real_module(_ps2core):
                _qt_binding = "PySide2"
            else:
                raise ImportError("PySide2.QtCore is a mock, not a real module")
        except ImportError:
            try:
                import PySide6.QtCore as _ps6core
                if _is_real_module(_ps6core):
                    _qt_binding = "PySide6"
                else:
                    raise ImportError("PySide6.QtCore is a mock, not a real module")
            except ImportError:
                _qt_binding = "STUB"

_detect_and_load()

if _qt_binding == "PySide2":
    from PySide2.QtCore import QObject, QThread, Signal, Slot, QTimer, Qt
    from PySide2 import QtWidgets, QtGui, QtCore
elif _qt_binding == "PySide6":
    from PySide6.QtCore import QObject, QThread, Signal, Slot, QTimer, Qt
    from PySide6 import QtWidgets, QtGui, QtCore
else:
    # No-op stubs for headless test environments (pytest without Maya/PySide)
    class _Signal:
        def __init__(self, *args):
            self._handlers = []
        def emit(self, *args, **kwargs):
            for fn in list(self._handlers):
                try:
                    fn(*args, **kwargs)
                except Exception:
                    pass
        def connect(self, fn):
            if fn not in self._handlers:
                self._handlers.append(fn)
        def disconnect(self, fn=None):
            if fn in self._handlers:
                self._handlers.remove(fn)

    def Signal(*args):
        return _Signal()

    def Slot(*args):
        return lambda fn: fn

    class QObject:
        def __init__(self, parent=None): pass
        def moveToThread(self, thread): pass
        def deleteLater(self): pass

    class QThread:
        def __init__(self, parent=None): self._started = False
        def start(self): self._started = True
        def quit(self): pass
        def wait(self, timeout=None): pass
        def isRunning(self): return self._started
        def deleteLater(self): pass
        started = _Signal()
        finished = _Signal()

    class QTimer:
        def __init__(self, parent=None): self._interval = 0
        def start(self, ms=None):
            if ms is not None: self._interval = ms
        def stop(self): pass
        def isActive(self): return False
        def setInterval(self, ms): self._interval = ms
        timeout = _Signal()

    class Qt:
        WindowModal = 0
        WindowStaysOnTopHint = 0

    class _QtWidgetsStub:
        def __getattr__(self, name):
            class _W:
                def __init__(self, *a, **k): pass
                def __getattr__(self, n): return lambda *a, **k: None
            return _W
    QtWidgets = _QtWidgetsStub()

    class _QtCoreStub:
        Qt = Qt
        def __getattr__(self, name): return lambda *a, **k: None
    QtCore = _QtCoreStub()

    class _QtGuiStub:
        def __getattr__(self, name): return lambda *a, **k: None
    QtGui = _QtGuiStub()
