import pytest
from maya.job_state import JobStateMachine, JobState, InvalidStateTransition

def test_initial_state():
    machine = JobStateMachine()
    assert machine.state == JobState.QUEUED

def test_valid_transitions():
    machine = JobStateMachine()
    
    # QUEUED -> PROCESSING
    machine.transition(JobState.PROCESSING)
    assert machine.state == JobState.PROCESSING
    
    # PROCESSING -> COMPLETED
    machine.transition(JobState.COMPLETED)
    assert machine.state == JobState.COMPLETED

def test_invalid_transition():
    machine = JobStateMachine()
    machine.transition(JobState.PROCESSING)
    machine.transition(JobState.COMPLETED)
    
    # Cannot transition out of terminal state
    with pytest.raises(InvalidStateTransition):
        machine.transition(JobState.PROCESSING)

def test_cancellation():
    machine = JobStateMachine()
    machine.transition(JobState.CANCELLED)
    assert machine.state == JobState.CANCELLED
    
    with pytest.raises(InvalidStateTransition):
        machine.transition(JobState.PROCESSING)

def test_retrying_flow():
    machine = JobStateMachine()
    machine.transition(JobState.PROCESSING)
    machine.transition(JobState.RETRYING)
    assert machine.state == JobState.RETRYING
    
    # Recover
    machine.transition(JobState.PROCESSING)
    assert machine.state == JobState.PROCESSING
    
    # Fail
    machine.transition(JobState.FAILED)
    assert machine.state == JobState.FAILED

def test_unknown_state():
    machine = JobStateMachine()
    with pytest.raises(ValueError):
        machine.transition("NOT_A_STATE")
