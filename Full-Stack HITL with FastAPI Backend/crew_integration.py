"""
CrewAI Integration Layer for HITL Workflows
Handles crew execution with checkpoint integration.
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio
from hitl_state_manager import StateManager, ExecutionState, CheckpointStatus


class CrewExecutor:
    """Executor for CrewAI workflows with HITL checkpoints."""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.project_root = Path(__file__).parent.parent
    
    def _get_python_command(self) -> str:
        """Get Python command based on platform."""
        import platform
        if platform.system() != "Windows":
            return "python3"
        return "python"
    
    async def execute_with_hitl(
        self,
        execution_id: str,
        inputs: Dict[str, Any],
        checkpoints: List[str]
    ):
        """
        Execute crew workflow with HITL checkpoints.
        This runs in background and manages checkpoint flow.
        """
        try:
            # Update state to running
            self.state_manager.update_execution_state(
                execution_id,
                ExecutionState.RUNNING
            )
            
            # Execute crew in phases based on checkpoints
            result = await self._execute_phased(
                execution_id=execution_id,
                inputs=inputs,
                checkpoints=checkpoints
            )
            
            # Mark as completed
            self.state_manager.update_execution_state(
                execution_id,
                ExecutionState.COMPLETED,
                result=result
            )
            
        except Exception as e:
            # Mark as error
            self.state_manager.update_execution_state(
                execution_id,
                ExecutionState.ERROR,
                error=str(e)
            )
    
    async def _execute_phased(
        self,
        execution_id: str,
        inputs: Dict[str, Any],
        checkpoints: List[str]
    ) -> Dict[str, Any]:
        """
        Execute crew in phases, creating checkpoints at specified points.
        """
        # Phase 1: Planning
        if "after_planning" in checkpoints:
            planning_result = await self._execute_phase(
                execution_id=execution_id,
                phase_name="planning",
                inputs=inputs,
                checkpoint_name="after_planning",
                checkpoint_description="Review content plan before proceeding to analysis"
            )
            
            # Check if stopped
            execution = self.state_manager.get_execution(execution_id)
            if execution and execution.state == ExecutionState.STOPPED:
                return {"status": "stopped", "phase": "planning", "result": planning_result}
            
            # Add planning result to inputs for next phase
            inputs["planning_context"] = planning_result
        
        # Phase 2: Analysis (sentiment + trends)
        if "after_analysis" in checkpoints:
            analysis_result = await self._execute_phase(
                execution_id=execution_id,
                phase_name="analysis",
                inputs=inputs,
                checkpoint_name="after_analysis",
                checkpoint_description="Review sentiment and trend analysis before strategy creation"
            )
            
            execution = self.state_manager.get_execution(execution_id)
            if execution and execution.state == ExecutionState.STOPPED:
                return {"status": "stopped", "phase": "analysis", "result": analysis_result}
            
            inputs["analysis_context"] = analysis_result
        
        # Phase 3: Final execution (if no more checkpoints or final phase)
        final_result = await self._execute_crew_direct(inputs)
        
        return {
            "status": "complete",
            "output": final_result.get("output", ""),
            "task_outputs": final_result.get("task_outputs", [])
        }
    
    async def _execute_phase(
        self,
        execution_id: str,
        phase_name: str,
        inputs: Dict[str, Any],
        checkpoint_name: str,
        checkpoint_description: str
    ) -> Dict[str, Any]:
        """
        Execute a phase and create checkpoint.
        """
        # Execute crew for this phase
        # In real implementation, you'd filter tasks by phase
        result = await self._execute_crew_direct(inputs)
        
        # Create checkpoint
        checkpoint = self.state_manager.create_checkpoint(
            execution_id=execution_id,
            checkpoint_name=checkpoint_name,
            description=checkpoint_description,
            context={
                "phase": phase_name,
                "result_preview": str(result.get("output", ""))[:500],
                "status": result.get("status", "unknown")
            }
        )
        
        # Wait for feedback (polling or event-based)
        await self._wait_for_feedback(execution_id, checkpoint.checkpoint_id)
        
        # Get feedback
        feedback = self.state_manager.get_checkpoint_feedback(checkpoint.checkpoint_id)
        
        # Add feedback to result
        result["_checkpoint"] = checkpoint_name
        result["_feedback"] = feedback
        
        return result
    
    async def _wait_for_feedback(
        self,
        execution_id: str,
        checkpoint_id: str,
        timeout: int = 3600  # 1 hour timeout
    ):
        """
        Wait for feedback on a checkpoint.
        Polls state manager until feedback is received or timeout.
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Checkpoint {checkpoint_id} timed out waiting for feedback")
            
            # Check if feedback received
            checkpoint = self.state_manager.get_pending_checkpoint(execution_id)
            if not checkpoint or checkpoint.checkpoint_id != checkpoint_id:
                # Feedback received or checkpoint resolved
                break
            
            # Check if execution cancelled
            execution = self.state_manager.get_execution(execution_id)
            if execution and execution.state == ExecutionState.CANCELLED:
                raise Exception("Execution cancelled")
            
            # Poll interval
            await asyncio.sleep(1)  # Poll every second
    
    async def _execute_crew_direct(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute crew directly via subprocess (same as Next.js API route).
        """
        python_cmd = self._get_python_command()
        crew_module = "crew.run"
        
        # Run crew in subprocess
        process = await asyncio.create_subprocess_exec(
            python_cmd, "-m", crew_module, "--stdin",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.project_root)
        )
        
        # Write inputs as JSON
        input_json = json.dumps(inputs)
        stdout, stderr = await process.communicate(input=input_json.encode())
        
        # Parse output
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            return {"status": "error", "error": error_msg}
        
        try:
            result = json.loads(stdout.decode())
            return result
        except json.JSONDecodeError:
            return {
                "status": "error",
                "error": f"Invalid JSON output: {stdout.decode()[:200]}"
            }
    
    async def resume_execution(self, execution_id: str):
        """
        Resume execution after feedback received.
        """
        execution = self.state_manager.get_execution(execution_id)
        if not execution:
            return
        
        if execution.state != ExecutionState.RUNNING:
            return  # Not in running state
        
        # Continue execution from where it left off
        # This would continue the phased execution
        # For simplicity, we'll re-execute the remaining phases
        # In production, you'd want to save and restore execution state
        
        try:
            # Get current phase based on completed checkpoints
            completed = execution.completed_checkpoints
            checkpoints = execution.checkpoints
            
            # Determine remaining phases
            remaining_checkpoints = [
                cp for cp in checkpoints
                if cp not in [self.state_manager._checkpoints[cid].checkpoint_name
                             for cid in completed if cid in self.state_manager._checkpoints]
            ]
            
            # Continue execution
            result = await self._execute_phased(
                execution_id=execution_id,
                inputs=execution.inputs,
                checkpoints=remaining_checkpoints
            )
            
            self.state_manager.update_execution_state(
                execution_id,
                ExecutionState.COMPLETED,
                result=result
            )
            
        except Exception as e:
            self.state_manager.update_execution_state(
                execution_id,
                ExecutionState.ERROR,
                error=str(e)
            )
