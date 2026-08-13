import traceback
import urllib.error
from qt_compat import QObject, Signal, Slot
from nexus_api_client import AuthExpiredError, APIConnectionError

class NetworkWorker(QObject):
    """
    QObject that performs network work.
    Must be moved to a QThread execution context by the orchestrator.
    It contains ZERO Maya or UI access.
    """
    started = Signal()
    finished = Signal(dict)
    failed = Signal(dict)
    cancelled = Signal()

    def __init__(self, api_client, endpoint, payload=None, method="GET", is_upload=False, file_path=None):
        super().__init__()
        self.api_client = api_client
        self.endpoint = endpoint
        self.payload = payload
        self.method = method
        self.is_upload = is_upload
        self.file_path = file_path
        self._is_cancelled = False

    def cancel(self):
        """Signals the worker to cancel. Network I/O blocking may prevent immediate abort."""
        self._is_cancelled = True

    @Slot()
    def execute(self):
        """Executes the actual network request on the worker thread."""
        self.started.emit()
        if self._is_cancelled:
            self.cancelled.emit()
            return

        try:
            if self.is_upload and self.file_path:
                result_path = self.api_client.upload_multipart(self.endpoint, self.file_path)
                if not result_path:
                    raise RuntimeError("Upload failed to return a path.")
                data = {"path": result_path}
                status = 200
            else:
                if self.method == "POST":
                    data, status = self.api_client.post_json(self.endpoint, self.payload)
                else:
                    data, status = self.api_client.request_json(self.endpoint)

            if self._is_cancelled:
                self.cancelled.emit()
                return

            if status == 200:
                self.finished.emit(data or {})
            else:
                self._emit_structured_error(
                    category="HTTP_ERROR",
                    message=f"Backend returned HTTP {status}",
                    status=status
                )
                
        except AuthExpiredError as e:
            self._emit_structured_error("AUTH_ERROR", str(e), status=401, exc=e)
        except APIConnectionError as e:
            self._emit_structured_error("CONNECTION_ERROR", str(e), exc=e)
        except urllib.error.URLError as e:
            if isinstance(e.reason, TimeoutError) or "timed out" in str(e.reason).lower():
                self._emit_structured_error("TIMEOUT", "Network request timed out", exc=e)
            else:
                self._emit_structured_error("NETWORK_ERROR", str(e), exc=e)
        except Exception as e:
            self._emit_structured_error("UNEXPECTED_ERROR", str(e), exc=e)

    def _emit_structured_error(self, category, message, status=None, exc=None):
        """Emits a structured error dictionary."""
        error_payload = {
            "category": category,
            "message": message,
            "status": status,
            "traceback": traceback.format_exc() if exc else None
        }
        self.failed.emit(error_payload)


import time
from qt_compat import QThread, QTimer
from job_state import JobStateMachine, JobState

class JobOrchestrator(QObject):
    """
    Main-thread owned orchestrator.
    Manages JobStateMachine, JobMonitor, and coordinates NetworkWorkers via signals.
    """
    job_completed = Signal(dict)
    job_failed = Signal(dict)
    job_state_changed = Signal(str, str) # old, new

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.state_machine = None
        
        # We must keep references to active workers/threads to prevent GC
        self._active_worker = None
        self._active_thread = None
        
        self.job_id = None
        self.poll_in_flight = False
        
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._on_poll_tick)
        self.start_time = 0

    def submit(self, payload, file_path=None, endpoint="/execute"):
        """
        Accepts job submission intent.
        Starts the background worker to execute the initial submission.
        """
        if self._active_worker or self.state_machine:
            raise RuntimeError("A job is already in progress. Qyntara currently supports 1 active job.")

        self.state_machine = JobStateMachine(JobState.QUEUED)
        self.job_state_changed.emit("None", JobState.QUEUED.name)
        
        self.start_time = time.monotonic()
        
        self._pending_payload = payload
        self._pending_endpoint = endpoint
        
        if file_path:
            # Step 1: Upload the file
            self._start_worker("/upload", method="POST", is_upload=True, file_path=file_path, is_submission=True)
        else:
            # Skip directly to Execute
            self._start_worker(endpoint, payload=payload, method="POST", is_submission=True)

    def _start_worker(self, endpoint, payload=None, method="GET", is_upload=False, file_path=None, is_submission=False):
        """Internal helper to instantiate and route a NetworkWorker on a QThread."""
        self._active_thread = QThread(self)
        self._active_worker = NetworkWorker(
            self.api_client, 
            endpoint, 
            payload=payload, 
            method=method, 
            is_upload=is_upload, 
            file_path=file_path
        )
        self._active_worker.moveToThread(self._active_thread)

        self._active_thread.started.connect(self._active_worker.execute)
        
        # Route signals back to main thread orchestrator
        if is_submission:
            self._active_worker.finished.connect(self._on_submission_finished)
            self._active_worker.failed.connect(self._on_submission_failed)
        else:
            self._active_worker.finished.connect(self._on_poll_finished)
            self._active_worker.failed.connect(self._on_poll_failed)

        # Cleanup hooks
        self._active_worker.finished.connect(self._active_thread.quit)
        self._active_worker.failed.connect(self._active_thread.quit)
        self._active_worker.cancelled.connect(self._active_thread.quit)
        self._active_thread.finished.connect(self._active_worker.deleteLater)
        self._active_thread.finished.connect(self._active_thread.deleteLater)

        self._active_thread.start()

    @Slot(dict)
    def _on_submission_finished(self, data):
        self._clear_worker_refs()
        
        if "task_id" in data:
            self.job_id = data["task_id"]
            self._transition(JobState.PROCESSING)
            self.poll_timer.start(1000) # Start JobMonitor
        elif "path" in data:
            # Upload succeeded, now execute
            server_path = data["path"]
            payload = self._pending_payload
            if payload:
                if "meshes" in payload:
                    payload["meshes"] = [server_path]
                else:
                    payload["meshes"] = [server_path]
            self._start_worker(self._pending_endpoint, payload=payload, method="POST", is_submission=True)

    @Slot(dict)
    def _on_submission_failed(self, err_dict):
        self._clear_worker_refs()
        self._transition(JobState.FAILED)
        self.job_failed.emit(err_dict)

    # ==========================
    # JOB MONITOR
    # ==========================
    @Slot()
    def _on_poll_tick(self):
        if self.poll_in_flight:
            return
            
        elapsed = time.monotonic() - self.start_time
        if elapsed > 600:
            self.poll_timer.stop()
            self._transition(JobState.FAILED)
            self.job_failed.emit({"category": "TIMEOUT", "message": "Job exceeded 600 seconds"})
            return

        if not self.job_id:
            return

        self.poll_in_flight = True
        self._start_worker(f"/tasks/{self.job_id}", method="GET")

    @Slot(dict)
    def _on_poll_finished(self, data):
        self._clear_worker_refs()
        self.poll_in_flight = False
        
        state_str = data.get("state", "").lower()
        if state_str == "done":
            self.poll_timer.stop()
            self._transition(JobState.COMPLETED)
            self.job_completed.emit(data)
        elif state_str == "failed":
            self.poll_timer.stop()
            self._transition(JobState.FAILED)
            self.job_failed.emit({"category": "JOB_ERROR", "message": data.get("error", "Unknown job error")})
        # If running/queued, do nothing, let next tick handle it

    @Slot(dict)
    def _on_poll_failed(self, err_dict):
        self._clear_worker_refs()
        self.poll_in_flight = False
        # Do not instantly fail the job on a temporary network blip during polling.
        # It will retry on the next tick until the 600s monotonic timeout is hit.

    def _transition(self, new_state):
        if not self.state_machine:
            return
        old_name = self.state_machine.state.name
        self.state_machine.transition(new_state)
        self.job_state_changed.emit(old_name, new_state.name)

    def _clear_worker_refs(self):
        # We don't delete them immediately, we let deleteLater handle it on the thread's event loop,
        # but we remove our strong references so we can start new ones.
        self._active_worker = None
        self._active_thread = None

    def cancel(self):
        """Cooperatively stops monitoring and attempts to abort active workers."""
        if self.poll_timer.isActive():
            self.poll_timer.stop()
        
        if self._active_worker:
            self._active_worker.cancel()
            
        if self.state_machine and self.state_machine.state not in (JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED):
            self._transition(JobState.CANCELLED)
        
        # Fire-and-forget cancellation to backend if we have a job ID
        if self.job_id:
            cancel_worker = NetworkWorker(self.api_client, f"/tasks/{self.job_id}/cancel", method="POST")
            # We don't track this thread heavily, it just runs and dies
            t = QThread(self)
            cancel_worker.moveToThread(t)
            t.started.connect(cancel_worker.execute)
            cancel_worker.finished.connect(t.quit)
            cancel_worker.failed.connect(t.quit)
            t.finished.connect(cancel_worker.deleteLater)
            t.finished.connect(t.deleteLater)
            t.start()

    def shutdown(self):
        """Mandatory cleanup when Maya or the UI closes."""
        self.cancel()
        if self._active_thread and self._active_thread.isRunning():
            self._active_thread.quit()
            self._active_thread.wait(1000) # wait up to 1s for cooperative exit

