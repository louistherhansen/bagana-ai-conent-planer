# Integration Notes: Flow-Level @human_feedback Decorator

## Connection to Integration Artifact

This folder implements **flow-level human feedback** as a decorator pattern, complementing the task-level human input documented in `project-context/2.build/integration.md`.

## Use Case in BAGANA AI Context

For the BAGANA AI content planning workflow, flow-level feedback decorators can be added at strategic phases:

### Phase 1: Planning Phase
```python
@human_feedback(
    checkpoint="after_planning",
    description="Review content plan before sentiment/trend analysis"
)
def execute_planning_phase(inputs: dict):
    # Execute create_content_plan task
    return planning_result
```

### Phase 2: Analysis Phase
```python
@human_feedback(
    checkpoint="after_analysis",
    description="Review sentiment and trend analysis before strategy creation"
)
def execute_analysis_phase(inputs: dict, plan_result: dict):
    # Execute analyze_sentiment and research_trends tasks
    return analysis_result
```

### Phase 3: Strategy Creation
```python
@human_feedback(
    checkpoint="before_finalization",
    description="Final review before completing content strategy"
)
def execute_strategy_phase(inputs: dict, plan_result: dict, analysis_result: dict):
    # Execute create_content_strategy task
    return strategy_result
```

## Integration with Existing Crew

### Option 1: Wrap Entire kickoff()

Modify `crew/run.py`:

```python
from human_feedback_decorator import human_feedback

@human_feedback(checkpoint="before_execution", description="Review inputs")
def kickoff(inputs: dict | None = None) -> dict:
    # ... existing kickoff() code ...
```

### Option 2: Phase-Based Checkpoints

Split execution into phases:

```python
def execute_planning(inputs: dict) -> dict:
    """Execute planning tasks only."""
    crew = build_crew()
    planning_tasks = [t for t in crew.tasks if t.name == "create_content_plan"]
    planning_crew = Crew(agents=crew.agents, tasks=planning_tasks)
    return planning_crew.kickoff(inputs=inputs)

@human_feedback(checkpoint="after_planning")
def execute_analysis(inputs: dict, plan_result: dict) -> dict:
    """Execute analysis tasks."""
    crew = build_crew()
    analysis_tasks = [t for t in crew.tasks if "sentiment" in t.name or "trend" in t.name]
    analysis_crew = Crew(agents=crew.agents, tasks=analysis_tasks)
    inputs["plan_context"] = plan_result
    return analysis_crew.kickoff(inputs=inputs)
```

### Option 3: Step Callback Integration

Enhance `_step_callback` to trigger checkpoints:

```python
def _step_callback_with_feedback(step: object) -> None:
    """Enhanced callback with flow-level checkpoints."""
    _step_callback(step)  # Existing logging
    
    # Trigger checkpoint after specific tasks
    if hasattr(step, "task") and step.task:
        task_name = getattr(step.task, "name", "")
        if task_name == "create_content_plan":
            from human_feedback_decorator import HumanFeedbackHandler
            handler = HumanFeedbackHandler("after_planning", "Review plan")
            feedback = handler.prompt_feedback({"task": task_name})
            if feedback["action"].value == "stop":
                raise KeyboardInterrupt("Stopped by feedback")
```

## API Integration Considerations

### Console Mode (Current)

Works directly when running Python:
- Decorator prompts via stdin/stderr
- User responds via console
- Execution continues based on feedback

### Web Mode (Future)

For web-based feedback, implement:

1. **State Management**: Store checkpoint state (Redis, DB, or in-memory)
2. **Feedback Endpoint**: `PUT /api/crew/feedback` to submit feedback
3. **Resume Mechanism**: Continue execution after feedback received
4. **WebSocket/SSE**: Stream checkpoint notifications to frontend

Example API flow:
```
1. Crew execution reaches checkpoint
2. API returns: { status: "checkpoint", checkpoint: "after_planning" }
3. Frontend shows approval UI
4. User submits feedback: PUT /api/crew/feedback { checkpoint_id, action, feedback }
5. API resumes execution with feedback context
```

## Comparison: Task-Level vs Flow-Level

| Aspect | Task-Level (`human_input: true`) | Flow-Level Decorator |
|--------|-------------------------------|---------------------|
| **When** | After each task completion | At function/phase boundaries |
| **Config** | YAML task config | Python decorator |
| **Scope** | Single task | Entire phase/flow |
| **Flexibility** | Fixed to task lifecycle | Customizable |
| **Use Case** | Task approval gates | Flow control, phase reviews |

## Recommended Approach for BAGANA AI

1. **Development/Testing**: Use flow-level decorators for phase reviews
2. **Production**: Combine both:
   - Task-level for critical task approvals
   - Flow-level for phase-level reviews
3. **Future**: Implement webhook-based feedback for web UI

## Files Reference

- `human_feedback_decorator.py` - Core decorator implementation
- `example_flow_feedback.py` - Usage examples
- `integrate_flow_feedback.py` - Integration guide
- `test_flow_feedback.py` - Test suite
- `README.md` - Complete documentation

## Next Steps

1. Review `integrate_flow_feedback.py` for integration patterns
2. Test with `example_flow_feedback.py` to understand behavior
3. Add decorators to `crew/run.py` at strategic phases
4. For API integration, implement webhook handler in `app/api/crew/webhook/route.ts`

## Related

- See `Task-Level Human Input (Simple Console Approval)` folder for task-level patterns
- See `WebSocket Testing` folder for async feedback patterns
- See `Streaming Testing` folder for real-time feedback patterns
