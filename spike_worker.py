import sys
import time
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error

# Setup dummy server to simulate delayed HTTP
class DelayedHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(2.0)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"state": "done", "result": "mock_result"}).encode())

    def log_message(self, format, *args):
        pass # Suppress logs

server = HTTPServer(('localhost', 9099), DelayedHandler)
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()

# Load PySide based on Maya version
try:
    from PySide2.QtCore import QThread, Signal, QObject, QTimer, QCoreApplication
except ImportError:
    from PySide6.QtCore import QThread, Signal, QObject, QTimer, QCoreApplication

# Minimal representation of NexusAPIClient
class MockNexusClient:
    def request_json(self, url):
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))

class WorkerSignals(QObject):
    finished = Signal(dict)
    error = Signal(str)

class NetworkWorker(QThread):
    def __init__(self, url):
        super(NetworkWorker, self).__init__()
        self.url = url
        self.signals = WorkerSignals()
        self.client = MockNexusClient()

    def run(self):
        print(f"[Worker Thread ID: {threading.get_ident()}] Sending request to {self.url}...")
        try:
            data = self.client.request_json(self.url)
            self.signals.finished.emit(data)
        except Exception as e:
            self.signals.error.emit(str(e))
        print(f"[Worker Thread ID: {threading.get_ident()}] Worker finished.")

class MainThreadOrchestrator(QObject):
    def __init__(self):
        super(MainThreadOrchestrator, self).__init__()
        self.worker = None
        self.start_time = 0

    def start_request(self):
        print(f"[Main Thread ID: {threading.get_ident()}] Starting request...")
        self.start_time = time.time()
        self.worker = NetworkWorker('http://localhost:9099/test')
        self.worker.signals.finished.connect(self.on_finished)
        self.worker.signals.error.connect(self.on_error)
        self.worker.start()

    def on_finished(self, data):
        elapsed = time.time() - self.start_time
        print(f"[Main Thread ID: {threading.get_ident()}] Received result: {data} after {elapsed:.2f}s")
        self.cleanup()

    def on_error(self, err):
        print(f"[Main Thread ID: {threading.get_ident()}] Received error: {err}")
        self.cleanup()
        
    def cleanup(self):
        if self.worker:
            self.worker.wait()
            self.worker = None
        QCoreApplication.quit()

def tick_main_thread():
    # Simulates Maya's UI remaining responsive
    sys.stdout.write(".")
    sys.stdout.flush()

if __name__ == '__main__':
    print(f"[Main Thread ID: {threading.get_ident()}] Starting Maya Spike...")
    app = QCoreApplication.instance()
    if not app:
        app = QCoreApplication(sys.argv)
        
    orchestrator = MainThreadOrchestrator()
    
    # Tick every 200ms to prove main thread is not blocked
    ui_timer = QTimer()
    ui_timer.timeout.connect(tick_main_thread)
    ui_timer.start(200)
    
    # Start request shortly after
    QTimer.singleShot(500, orchestrator.start_request)
    
    app.exec_() # For PySide2/6 compatibility
    
    server.shutdown()
    print("\n[Main Thread ID: {0}] Test complete.".format(threading.get_ident()))
