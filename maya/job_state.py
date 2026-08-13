from enum import Enum

class JobState(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class InvalidStateTransition(Exception):
    """Raised when an illegal state transition is attempted."""
    pass

class JobStateMachine:
    """
    Encodes the strict Job State Contract for Qyntara Nexus.
    """
    
    TRANSITIONS = {
        JobState.QUEUED: [JobState.PROCESSING, JobState.CANCELLED],
        JobState.PROCESSING: [JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED, JobState.RETRYING],
        JobState.RETRYING: [JobState.PROCESSING, JobState.FAILED],
        JobState.COMPLETED: [],  # Terminal
        JobState.FAILED: [],     # Terminal
        JobState.CANCELLED: []   # Terminal
    }
    
    def __init__(self, initial_state=JobState.QUEUED):
        self._state = initial_state
        
    @property
    def state(self):
        return self._state
        
    def transition(self, next_state: JobState):
        if not isinstance(next_state, JobState):
            raise ValueError(f"Unknown state: {next_state}")
            
        allowed = self.TRANSITIONS.get(self._state, [])
        if next_state not in allowed:
            raise InvalidStateTransition(f"Cannot transition from {self._state.name} to {next_state.name}")
            
        self._state = next_state
