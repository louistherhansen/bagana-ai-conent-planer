"""
Flow-Level Human Feedback Decorator for CrewAI
Provides a decorator pattern to add human feedback checkpoints at flow-level execution points.

Usage:
    @human_feedback(checkpoint="after_planning")
    def execute_crew(inputs):
        crew = build_crew()
        return crew.kickoff(inputs=inputs)
"""

import functools
import sys
from typing import Callable, Dict, Any, Optional, List
from enum import Enum


class FeedbackAction(Enum):
    """Actions available for human feedback."""
    CONTINUE = "continue"
    STOP = "stop"
    REVISE = "revise"
    SKIP = "skip"


class HumanFeedbackHandler:
    """Handler for collecting and processing human feedback."""
    
    def __init__(self, checkpoint_name: str, description: str = ""):
        self.checkpoint_name = checkpoint_name
        self.description = description
        self.feedback_history: List[Dict[str, Any]] = []
    
    def prompt_feedback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prompt user for feedback at a checkpoint.
        
        Args:
            context: Dictionary containing context about current state
            
        Returns:
            Dictionary with 'action' (FeedbackAction) and optional 'feedback' (str)
        """
        print("\n" + "="*80, file=sys.stderr)
        print(f"🔍 FLOW CHECKPOINT: {self.checkpoint_name}", file=sys.stderr)
        print("="*80, file=sys.stderr)
        
        if self.description:
            print(f"\n📋 {self.description}", file=sys.stderr)
        
        # Display context summary
        if context:
            print("\n📊 Current Context:", file=sys.stderr)
            for key, value in list(context.items())[:5]:  # Show first 5 items
                value_preview = str(value)[:200] if value else "N/A"
                print(f"  • {key}: {value_preview}...", file=sys.stderr)
        
        print("\n" + "-"*80, file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("  [c/continue] - Continue to next stage", file=sys.stderr)
        print("  [s/stop]     - Stop execution", file=sys.stderr)
        print("  [r/revise]   - Provide feedback for revision", file=sys.stderr)
        print("  [k/skip]     - Skip this checkpoint", file=sys.stderr)
        print("-"*80, file=sys.stderr)
        
        while True:
            response = input("\n👉 Your decision: ").strip().lower()
            
            if response in ['c', 'continue']:
                action = FeedbackAction.CONTINUE
                feedback = None
                break
            elif response in ['s', 'stop']:
                action = FeedbackAction.STOP
                feedback = None
                break
            elif response in ['r', 'revise']:
                feedback_input = input("📝 Enter your feedback: ").strip()
                if feedback_input:
                    action = FeedbackAction.REVISE
                    feedback = feedback_input
                    break
                else:
                    print("⚠️  Empty feedback. Please try again.", file=sys.stderr)
            elif response in ['k', 'skip']:
                action = FeedbackAction.SKIP
                feedback = None
                break
            else:
                print("⚠️  Invalid input. Please enter 'c', 's', 'r', or 'k'.", file=sys.stderr)
        
        result = {
            "action": action,
            "feedback": feedback,
            "checkpoint": self.checkpoint_name,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
        
        self.feedback_history.append(result)
        
        action_msg = {
            FeedbackAction.CONTINUE: "✅ Continuing to next stage...",
            FeedbackAction.STOP: "❌ Stopping execution...",
            FeedbackAction.REVISE: f"📝 Feedback received: {feedback}",
            FeedbackAction.SKIP: "⏭️  Skipping checkpoint..."
        }
        
        print(f"\n{action_msg[action]}\n", file=sys.stderr)
        
        return result


def human_feedback(
    checkpoint: str,
    description: str = "",
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
    context_extractor: Optional[Callable[[Any], Dict[str, Any]]] = None
):
    """
    Decorator to add human feedback checkpoints at flow-level execution.
    
    Args:
        checkpoint: Name of the checkpoint (e.g., "after_planning", "before_finalization")
        description: Human-readable description of what this checkpoint is for
        condition: Optional function that takes context and returns bool to conditionally enable checkpoint
        context_extractor: Optional function to extract context from function result/state
    
    Usage:
        @human_feedback(checkpoint="after_planning", description="Review content plan before sentiment analysis")
        def execute_planning_phase(inputs):
            # ... crew execution ...
            return result
    """
    def decorator(func: Callable) -> Callable:
        handler = HumanFeedbackHandler(checkpoint, description)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check condition if provided
            if condition:
                context = kwargs.get("context", {}) or {}
                if not condition(context):
                    # Condition not met, skip checkpoint
                    return func(*args, **kwargs)
            
            # Execute function
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                # On error, still prompt for feedback if desired
                error_context = {"error": str(e), "function": func.__name__}
                feedback = handler.prompt_feedback(error_context)
                
                if feedback["action"] == FeedbackAction.STOP:
                    raise
                elif feedback["action"] == FeedbackAction.REVISE:
                    # Could retry with feedback, but for now just re-raise
                    raise
                else:
                    raise
            
            # Extract context from result
            context = {}
            if context_extractor:
                context = context_extractor(result)
            elif isinstance(result, dict):
                context = result
            elif hasattr(result, "__dict__"):
                context = {k: str(v)[:200] for k, v in vars(result).items()}
            else:
                context = {"result": str(result)[:500]}
            
            # Add function args/kwargs to context
            if args:
                context["args_count"] = len(args)
            if kwargs:
                context.update({f"arg_{k}": str(v)[:100] for k, v in list(kwargs.items())[:3]})
            
            # Prompt for feedback
            feedback = handler.prompt_feedback(context)
            
            # Handle feedback action
            if feedback["action"] == FeedbackAction.STOP:
                # Return early with stop signal
                if isinstance(result, dict):
                    result["_feedback"] = feedback
                    result["_stopped"] = True
                    return result
                return {"status": "stopped", "feedback": feedback, "previous_result": result}
            
            elif feedback["action"] == FeedbackAction.REVISE:
                # Add feedback to result for downstream processing
                if isinstance(result, dict):
                    result["_feedback"] = feedback
                    result["_needs_revision"] = True
                # Could trigger revision logic here
            
            elif feedback["action"] == FeedbackAction.SKIP:
                # Continue without modification
                pass
            
            # CONTINUE: proceed normally
            return result
        
        # Attach handler for external access
        wrapper._feedback_handler = handler
        wrapper._checkpoint_name = checkpoint
        
        return wrapper
    
    return decorator


def multi_checkpoint_feedback(checkpoints: List[Dict[str, Any]]):
    """
    Decorator factory for multiple checkpoints in a single flow.
    
    Args:
        checkpoints: List of checkpoint configs, each with 'name', 'description', 'condition', etc.
    
    Usage:
        @multi_checkpoint_feedback([
            {"checkpoint": "after_planning", "description": "Review plan"},
            {"checkpoint": "after_analysis", "description": "Review analysis"}
        ])
        def execute_full_flow(inputs):
            # ... multi-stage execution ...
    """
    def decorator(func: Callable) -> Callable:
        handlers = {}
        for cp_config in checkpoints:
            cp_name = cp_config.get("checkpoint", "unknown")
            handlers[cp_name] = HumanFeedbackHandler(
                cp_name,
                cp_config.get("description", "")
            )
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # This is a simplified version - full implementation would
            # require more sophisticated flow control
            return func(*args, **kwargs)
        
        wrapper._feedback_handlers = handlers
        return wrapper
    
    return decorator
