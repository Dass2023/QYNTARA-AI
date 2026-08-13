import pytest
from unittest.mock import MagicMock
import urllib.error
import socket
import sys

# qt_compat.py provides built-in no-op stubs when PySide is not available.
# No external patching is needed or safe here — it caused cross-test contamination.
from maya.job_orchestrator import NetworkWorker
# Import from the same bare path job_orchestrator.py uses — in pytest, maya.nexus_api_client
# and nexus_api_client are separate module objects; mismatched class identity breaks except clauses.
from nexus_api_client import APIConnectionError, AuthExpiredError

# Lightweight observable signal for verifying emit calls in tests.
class DummySignal:
    def __init__(self):
        self.called = False
        self.call_args = None
    def emit(self, *args, **kwargs):
        self.called = True
        self.call_args = (args, kwargs)
    def connect(self, func):
        pass

@pytest.fixture
def api_client():
    client = MagicMock()
    return client

@pytest.fixture
def worker(api_client):
    worker = NetworkWorker(api_client, "/test")
    worker.started = DummySignal()
    worker.finished = DummySignal()
    worker.failed = DummySignal()
    worker.cancelled = DummySignal()
    return worker

def test_worker_success(worker, api_client):
    api_client.request_json.return_value = ({"status": "ok"}, 200)
    worker.execute()
    
    assert worker.started.called
    assert worker.finished.called
    assert worker.finished.call_args[0][0] == {"status": "ok"}
    assert not worker.failed.called

def test_worker_http_error(worker, api_client):
    api_client.request_json.return_value = (None, 500)
    worker.execute()
    
    assert worker.failed.called
    err_dict = worker.failed.call_args[0][0]
    assert err_dict["category"] == "HTTP_ERROR"
    assert err_dict["status"] == 500

def test_worker_auth_error(worker, api_client):
    api_client.request_json.side_effect = AuthExpiredError("Expired")
    worker.execute()
    
    assert worker.failed.called
    err_dict = worker.failed.call_args[0][0]
    assert err_dict["category"] == "AUTH_ERROR"
    assert err_dict["status"] == 401

def test_worker_connection_error(worker, api_client):
    api_client.request_json.side_effect = APIConnectionError("Failed")
    worker.execute()
    
    assert worker.failed.called
    err_dict = worker.failed.call_args[0][0]
    assert err_dict["category"] == "CONNECTION_ERROR"

def test_worker_timeout(worker, api_client):
    err = urllib.error.URLError(TimeoutError("timed out"))
    api_client.request_json.side_effect = err
    worker.execute()
    
    assert worker.failed.called
    err_dict = worker.failed.call_args[0][0]
    assert err_dict["category"] == "TIMEOUT"

def test_worker_unexpected_exception(worker, api_client):
    api_client.request_json.side_effect = ValueError("Something broke")
    worker.execute()
    
    assert worker.failed.called
    err_dict = worker.failed.call_args[0][0]
    assert err_dict["category"] == "UNEXPECTED_ERROR"
    assert "Something broke" in err_dict["message"]

def test_worker_cancellation(worker, api_client):
    worker.cancel()
    worker.execute()
    
    assert worker.cancelled.called
    assert not worker.finished.called
    assert not worker.failed.called
