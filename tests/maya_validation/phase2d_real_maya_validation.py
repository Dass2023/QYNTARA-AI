import sys
import os
import threading
import time

def log(msg, category="MAIN"):
    """Structured logging with thread identity."""
    thread_id = threading.get_ident()
    is_main = threading.current_thread() is threading.main_thread()
    thread_type = "MAIN_THREAD" if is_main else "WORKER_THREAD"
    print(f"[{category}] [TID:{thread_id}] [{thread_type}] {msg}")

def run_validation():
    log("=========================================")
    log("PHASE 2D REAL MAYA VALIDATION SCRIPT")
    log("=========================================")
    
    # TEST A - STARTUP
    log("Starting TEST A: PLUGIN STARTUP")
    try:
        import maya.cmds as cmds
        import maya.api.OpenMaya as om
        log("Maya APIs loaded successfully.")
    except ImportError:
        log("ERROR: Must run inside Maya or mayapy.", "ERROR")
        return

    # Add maya dir to path to import Qyntara modules
    script_dir = os.path.dirname(os.path.abspath(__file__))
    maya_plugin_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "maya"))
    if maya_plugin_dir not in sys.path:
        sys.path.append(maya_plugin_dir)

    try:
        from qyntara_client import QyntaraDockable
        from job_orchestrator import JobOrchestrator
        from job_state import JobState
        log("Qyntara dependencies loaded.")
    except ImportError as e:
        log(f"ERROR loading dependencies: {e}", "ERROR")
        return

    # We only initialize the Qt App if it doesn't exist
    from qt_compat import QtWidgets
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
        is_standalone = True
    else:
        is_standalone = False

    log("Instantiating QyntaraDockable...")
    try:
        client = QyntaraDockable()
        log("QyntaraDockable created successfully.")
    except Exception as e:
        log(f"Failed to create QyntaraDockable: {e}", "ERROR")
        return

    # TEST B - JOB SUBMISSION & THREAD IDENTITY
    log("Starting TEST B: JOB SUBMISSION (Test C, D, E, F will be observed natively)")
    
    # We will intercept the Orchestrator to print thread IDs during states
    original_transition = client.job_orchestrator._transition
    def debug_transition(new_state):
        log(f"STATE TRANSITION: {client.job_orchestrator.state_machine.state} -> {new_state}", "ORCHESTRATOR")
        original_transition(new_state)
    client.job_orchestrator._transition = debug_transition

    # Hook the worker execution to log thread ID
    original_start_worker = client.job_orchestrator._start_worker
    def debug_start_worker(*args, **kwargs):
        log("Starting NetworkWorker...", "ORCHESTRATOR")
        original_start_worker(*args, **kwargs)
        worker = client.job_orchestrator._active_worker
        if worker:
            original_execute = worker.execute
            def debug_execute():
                log(f"Executing Network Task on endpoint: {worker.endpoint}", "NETWORK_WORKER")
                original_execute()
            worker.execute = debug_execute
    client.job_orchestrator._start_worker = debug_start_worker

    # Hook Completion
    original_completed = client._on_orchestrator_completed
    def debug_completed(data):
        log(f"Job Completed. Data: {data}", "MAIN")
        original_completed(data)
        if is_standalone:
            log("Test F (Completion) Finished. Quitting App.", "MAIN")
            app.quit()
    client._on_orchestrator_completed = debug_completed

    # Hook Failure (TEST G)
    original_failed = client._on_orchestrator_failed
    def debug_failed(err):
        log(f"Job Failed! Error: {err}", "MAIN")
        original_failed(err)
        if is_standalone:
            log("Test G (Failure) Finished. Quitting App.", "MAIN")
            app.quit()
    client._on_orchestrator_failed = debug_failed

    log("Mocking a scene object for export...")
    cmds.file(new=True, force=True)
    cmds.polyCube()
    cmds.select('pCube1')

    log("Triggering submit_job...")
    # NOTE: Set QYNTARA_ACCESS_CODE env var for real backend or it will fail auth (Testing G).
    client.submit_job(tasks=["remesh"])

    if is_standalone:
        log("Running standalone event loop to process async tasks...")
        app.exec_()
    else:
        log("Plugin loaded in interactive Maya. Observe UI and Maya viewport responsiveness.", "MAIN")
        client.show()

if __name__ == "__main__":
    run_validation()
