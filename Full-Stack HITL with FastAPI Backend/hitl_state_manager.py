"""
State Manager for Human-In-The-Loop Workflows
Manages execution state, checkpoints, and feedback.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from threading import Lock


class ExecutionState(Enum):
    """Execution state enum."""
    PENDING = "pending"
    RUNNING = "running"
    WAITING_FEEDBACK = "waiting_feedback"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"
    STOPPED = "stopped"


class CheckpointStatus(Enum):
    """Checkpoint status enum."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISED = "revised"
    SKIPPED = "skipped"


class FeedbackAction(Enum):
    """Feedback action enum."""
    CONTINUE = "continue"
    STOP = "stop"
    REVISE = "revise"
    SKIP = "skip"


@dataclass
class CheckpointState:
    """State for a single checkpoint."""
    checkpoint_id: str
    execution_id: str
    checkpoint_name: str
    description: str
    context: Dict[str, Any]
    status: CheckpointStatus = CheckpointStatus.PENDING
    feedback: Optional[str] = None
    action: Optional[FeedbackAction] = None
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class ExecutionStateData:
    """State for an execution."""
    execution_id: str
    inputs: Dict[str, Any]
    state: ExecutionState = ExecutionState.PENDING
    checkpoints: List[str] = field(default_factory=list)
    current_checkpoint: Optional[str] = None
    completed_checkpoints: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class StateManager:
    """Thread-safe state manager for HITL workflows."""
    
    def __init__(self):
        self._executions: Dict[str, ExecutionStateData] = {}
        self._checkpoints: Dict[str, CheckpointState] = {}
        self._execution_checkpoints: Dict[str, List[str]] = {}  # execution_id -> checkpoint_ids
        self._lock = Lock()
    
    def create_execution(
        self,
        execution_id: str,
        inputs: Dict[str, Any],
        checkpoints: List[str]
    ) -> ExecutionStateData:
        """Create a new execution state."""
        with self._lock:
            execution = ExecutionStateData(
                execution_id=execution_id,
                inputs=inputs,
                checkpoints=checkpoints,
                state=ExecutionState.PENDING
            )
            self._executions[execution_id] = execution
            self._execution_checkpoints[execution_id] = []
            return execution
    
    def get_execution(self, execution_id: str) -> Optional[ExecutionStateData]:
        """Get execution state."""
        with self._lock:
            return self._executions.get(execution_id)
    
    def update_execution_state(
        self,
        execution_id: str,
        state: ExecutionState,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """Update execution state."""
        with self._lock:
            execution = self._executions.get(execution_id)
            if not execution:
                return False
            
            execution.state = state
            execution.updated_at = datetime.now()
            if result is not None:
                execution.result = result
            if error is not None:
                execution.error = error
            
            return True
    
    def create_checkpoint(
        self,
        execution_id: str,
        checkpoint_name: str,
        description: str,
        context: Dict[str, Any]
    ) -> CheckpointState:
        """Create a new checkpoint."""
        checkpoint_id = str(uuid.uuid4())
        
        with self._lock:
            checkpoint = CheckpointState(
                checkpoint_id=checkpoint_id,
                execution_id=execution_id,
                checkpoint_name=checkpoint_name,
                description=description,
                context=context
            )
            self._checkpoints[checkpoint_id] = checkpoint
            
            # Link to execution
            if execution_id not in self._execution_checkpoints:
                self._execution_checkpoints[execution_id] = []
            self._execution_checkpoints[execution_id].append(checkpoint_id)
            
            # Update execution state
            execution = self._executions.get(execution_id)
            if execution:
                execution.current_checkpoint = checkpoint_id
                execution.state = ExecutionState.WAITING_FEEDBACK
                execution.updated_at = datetime.now()
        
        return checkpoint
    
    def get_pending_checkpoint(self, execution_id: str) -> Optional[CheckpointState]:
        """Get current pending checkpoint for an execution."""
        with self._lock:
            execution = self._executions.get(execution_id)
            if not execution or not execution.current_checkpoint:
                return None
            
            checkpoint_id = execution.current_checkpoint
            checkpoint = self._checkpoints.get(checkpoint_id)
            
            if checkpoint and checkpoint.status == CheckpointStatus.PENDING:
                return checkpoint
            
            return None
    
    def submit_feedback(
        self,
        execution_id: str,
        checkpoint_id: str,
        action: FeedbackAction,
        feedback: Optional[str] = None
    ) -> bool:
        """Submit feedback for a checkpoint."""
        with self._lock:
            checkpoint = self._checkpoints.get(checkpoint_id)
            if not checkpoint or checkpoint.execution_id != execution_id:
                return False
            
            if checkpoint.status != CheckpointStatus.PENDING:
                return False  # Already processed
            
            # Update checkpoint
            checkpoint.action = action
            checkpoint.feedback = feedback
            checkpoint.resolved_at = datetime.now()
            
            # Map action to status
            if action == FeedbackAction.CONTINUE:
                checkpoint.status = CheckpointStatus.APPROVED
            elif action == FeedbackAction.STOP:
                checkpoint.status = CheckpointStatus.REJECTED
            elif action == FeedbackAction.REVISE:
                checkpoint.status = CheckpointStatus.REVISED
            elif action == FeedbackAction.SKIP:
                checkpoint.status = CheckpointStatus.SKIPPED
            
            # Update execution
            execution = self._executions.get(execution_id)
            if execution:
                execution.completed_checkpoints.append(checkpoint_id)
                execution.current_checkpoint = None
                execution.updated_at = datetime.now()
                
                if action == FeedbackAction.STOP:
                    execution.state = ExecutionState.STOPPED
                elif action in [FeedbackAction.CONTINUE, FeedbackAction.SKIP]:
                    execution.state = ExecutionState.RUNNING
            
            return True
    
    def get_checkpoint_feedback(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback for a checkpoint."""
        with self._lock:
            checkpoint = self._checkpoints.get(checkpoint_id)
            if not checkpoint or checkpoint.status == CheckpointStatus.PENDING:
                return None
            
            return {
                "action": checkpoint.action.value if checkpoint.action else None,
                "feedback": checkpoint.feedback,
                "status": checkpoint.status.value
            }
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an execution."""
        with self._lock:
            execution = self._executions.get(execution_id)
            if not execution:
                return False
            
            execution.state = ExecutionState.CANCELLED
            execution.updated_at = datetime.now()
            return True
    
    def get_active_executions(self) -> List[str]:
        """Get list of active execution IDs."""
        with self._lock:
            return [
                eid for eid, exec_data in self._executions.items()
                if exec_data.state in [
                    ExecutionState.RUNNING,
                    ExecutionState.WAITING_FEEDBACK,
                    ExecutionState.PENDING
                ]
            ]
    
    def get_pending_checkpoints(self) -> List[str]:
        """Get list of pending checkpoint IDs."""
        with self._lock:
            return [
                cid for cid, checkpoint in self._checkpoints.items()
                if checkpoint.status == CheckpointStatus.PENDING
            ]
    
    def list_executions(self) -> List[ExecutionStateData]:
        """List all executions."""
        with self._lock:
            return list(self._executions.values())
