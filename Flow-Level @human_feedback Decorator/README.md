# Flow-Level @human_feedback Decorator

This folder contains a **decorator-based implementation** for adding human feedback checkpoints at the **flow level** (entire crew execution) rather than individual task level.

## Overview

While **task-level human input** (`human_input=True` on tasks) pauses at individual task completion, **flow-level feedback** allows you to add checkpoints at strategic points in the overall workflow execution, regardless of task boundaries.

### Key Differences

| Feature | Task-Level Human Input | Flow-Level Feedback Decorator |
|---------|----------------------|-------------------------------|
| **Scope** | Individual tasks | Entire flow/phases |
| **Placement** | At task completion | At any function/phase boundary |
| **Control** | Task-level config | Decorator-based |
| **Flexibility** | Fixed to task lifecycle | Customizable checkpoints |
| **Use Case** | Task approval gates | Flow control, phase reviews |

## Use Cases

- **Phase Reviews**: Review entire planning phase before analysis phase
- **Conditional Checkpoints**: Only prompt feedback under certain conditions
- **Multi-Stage Workflows**: Add checkpoints between workflow stages
- **Error Recovery**: Prompt feedback when errors occur
- **Quality Gates**: Review outputs before expensive downstream operations

## Architecture

```
User Input
    ↓
@human_feedback(checkpoint="before_execution")
    ↓
execute_planning_phase()
    ↓
@human_feedback(checkpoint="after_planning")
    ↓
execute_analysis_phase()
    ↓
@human_feedback(checkpoint="before_finalization")
    ↓
Final Result
```

## Files in This Folder

### `human_feedback_decorator.py`
Core decorator implementation:
- `@human_feedback` - Main decorator for single checkpoints
- `HumanFeedbackHandler` - Handles feedback collection and processing
- `FeedbackAction` - Enum for available actions (CONTINUE, STOP, REVISE, SKIP)
- `multi_checkpoint_feedback` - Decorator for multiple checkpoints

### `example_flow_feedback.py`
Complete working examples showing:
- Single checkpoint usage
- Conditional checkpoints
- Custom context extraction
- Multi-stage flows

**Usage:**
```bash
python "Flow-Level @human_feedback Decorator/example_flow_feedback.py"
```

### `integrate_flow_feedback.py`
Integration guide with code snippets for:
- Adding decorator to `crew/run.py`
- Wrapping `kickoff()` function
- Adding checkpoints at specific phases
- API integration patterns

### `test_flow_feedback.py`
Test suite to verify decorator functionality.

## Quick Start

### Basic Usage

```python
from human_feedback_decorator import human_feedback

@human_feedback(
    checkpoint="after_planning",
    description="Review content plan before proceeding"
)
def execute_planning(inputs: dict):
    crew = build_crew()
    return crew.kickoff(inputs=inputs)

# Usage
result = execute_planning({"user_input": "Create a plan"})
```

### Conditional Checkpoint

```python
def should_review(context: dict) -> bool:
    """Only review complex plans."""
    return len(context.get("user_input", "")) > 100

@human_feedback(
    checkpoint="conditional_review",
    condition=should_review
)
def execute_conditional(inputs: dict):
    crew = build_crew()
    return crew.kickoff(inputs=inputs)
```

### Custom Context Extraction

```python
def extract_context(result) -> dict:
    """Extract relevant context from result."""
    return {
        "output_length": len(str(result)),
        "status": result.get("status", "unknown")
    }

@human_feedback(
    checkpoint="review",
    context_extractor=extract_context
)
def execute_with_context(inputs: dict):
    crew = build_crew()
    return crew.kickoff(inputs=inputs)
```

## Feedback Actions

When prompted at a checkpoint, you can choose:

- **`c` or `continue`**: Continue to next stage
- **`s` or `stop`**: Stop execution immediately
- **`r` or `revise`**: Provide feedback for revision
- **`k` or `skip`**: Skip this checkpoint (for conditional checkpoints)

## Integration Steps

### Step 1: Import Decorator

Add to `crew/run.py`:

```python
from pathlib import Path
import sys

DECORATOR_PATH = Path(__file__).parent.parent / "Flow-Level @human_feedback Decorator"
if str(DECORATOR_PATH) not in sys.path:
    sys.path.insert(0, str(DECORATOR_PATH))

from human_feedback_decorator import human_feedback
```

### Step 2: Wrap Functions

Add decorators to your execution functions:

```python
@human_feedback(checkpoint="after_planning", description="Review plan")
def execute_planning_phase(inputs: dict):
    # ... crew execution ...
    return result
```

### Step 3: Handle Feedback

The decorator automatically handles feedback and modifies execution flow based on user input.

## Advanced Patterns

### Multi-Stage Flow

```python
@human_feedback(checkpoint="after_stage1")
def stage1(inputs):
    # Execute stage 1
    return result1

@human_feedback(checkpoint="after_stage2")
def stage2(inputs, stage1_result):
    # Execute stage 2 with stage1 context
    return result2

def full_flow(inputs):
    r1 = stage1(inputs)
    if r1.get("_stopped"):
        return r1
    r2 = stage2(inputs, r1)
    return {"stage1": r1, "stage2": r2}
```

### Error Recovery

```python
@human_feedback(checkpoint="error_recovery")
def execute_with_recovery(inputs):
    try:
        return crew.kickoff(inputs)
    except Exception as e:
        # Decorator will prompt for feedback on error
        raise
```

## API Integration

### Console Mode (Current)

Works directly when running Python:
```bash
python -m crew.run --stdin
```

### Web Mode (Future)

For web-based feedback, implement:
1. State management (store checkpoint state)
2. Feedback endpoint (`PUT /api/crew/feedback`)
3. Resume mechanism (continue after feedback)

See `integrate_flow_feedback.py` for API integration patterns.

## Comparison with Task-Level Human Input

| Aspect | Task-Level | Flow-Level Decorator |
|--------|-----------|---------------------|
| **Configuration** | YAML (`human_input: true`) | Python decorator |
| **Granularity** | Per task | Per function/phase |
| **Flexibility** | Fixed to task lifecycle | Customizable |
| **Conditional** | No | Yes (via `condition` param) |
| **Context** | Task output only | Custom extractable |
| **Use Case** | Task approval | Flow control |

## Limitations

1. **Console Only**: Current implementation uses console/stdin
2. **Synchronous**: Blocks execution until feedback received
3. **No Timeout**: No automatic timeout for feedback
4. **Single Session**: Designed for single-user console sessions

## Future Enhancements

- [ ] Webhook-based feedback for API usage
- [ ] Feedback timeout configuration
- [ ] Async feedback collection
- [ ] Feedback history persistence
- [ ] Multi-user approval workflows
- [ ] YAML-based checkpoint configuration

## Testing

Run the example to test flow-level feedback:

```bash
cd "Flow-Level @human_feedback Decorator"
python example_flow_feedback.py
```

Or run the test suite:

```bash
python test_flow_feedback.py
```

## Notes

- Feedback prompts appear in **stderr** to avoid interfering with JSON output
- Decorator preserves function signature and metadata
- Feedback history is stored in handler for audit trail
- For production, consider webhook-based approval instead of console

## References

- [CrewAI Documentation](https://docs.crewai.com)
- [Python Decorators](https://docs.python.org/3/glossary.html#term-decorator)
- Related: `Task-Level Human Input (Simple Console Approval)` folder for task-level patterns

## Conclusion

The Flow-Level `@human_feedback` decorator provides a **flexible and powerful pattern** for adding human oversight to CrewAI workflows at strategic phase boundaries, complementing task-level human input for comprehensive workflow control.

### Key Advantages

✅ **Flexible Placement**: Add checkpoints at any function/phase boundary, not just task completion  
✅ **Conditional Logic**: Enable checkpoints only when needed via `condition` parameter  
✅ **Custom Context**: Extract and present relevant context for human review  
✅ **Flow Control**: Control entire workflow phases, not just individual tasks  
✅ **Pythonic Pattern**: Uses familiar decorator pattern for clean, readable code  

### When to Use Flow-Level vs Task-Level

**Use Flow-Level Decorator when:**
- You need checkpoints between workflow phases (planning → analysis → strategy)
- Checkpoints should be conditional based on context
- You want to review aggregated results from multiple tasks
- You need custom context extraction for human review
- You want programmatic control over checkpoint placement

**Use Task-Level Human Input when:**
- You need approval after every task completion
- Checkpoints are tied to specific task lifecycle events
- You prefer YAML-based configuration
- You want simpler, declarative checkpoint configuration

### Integration Strategy

For BAGANA AI's content planning workflow, consider a **hybrid approach**:

1. **Flow-Level**: Add phase checkpoints (after planning, after analysis, before finalization)
2. **Task-Level**: Add critical task approvals (e.g., brand safety compliance)
3. **Combined**: Use both patterns together for comprehensive oversight

### Best Practices

1. **Strategic Placement**: Place checkpoints at natural phase boundaries, not after every function
2. **Clear Descriptions**: Provide meaningful descriptions so humans understand what they're reviewing
3. **Context Extraction**: Extract concise, relevant context—humans need quick decisions
4. **Conditional Checkpoints**: Use conditions to avoid unnecessary interruptions
5. **Feedback Handling**: Handle all feedback actions (CONTINUE, STOP, REVISE, SKIP) appropriately

### Next Steps

1. **Try the Examples**: Run `example_flow_feedback.py` to see decorators in action
2. **Integrate**: Follow `integrate_flow_feedback.py` to add decorators to your workflow
3. **Test**: Use `test_flow_feedback.py` to verify functionality
4. **Combine**: Consider using both flow-level and task-level patterns together
5. **Scale**: For production, implement webhook-based feedback (see `INTEGRATION_NOTES.md`)

### Summary

The Flow-Level `@human_feedback` decorator empowers you to add **strategic human oversight** to your CrewAI workflows, enabling quality gates, phase reviews, and flow control at the right level of abstraction. By combining this with task-level human input, you can achieve comprehensive human-in-the-loop control over your AI-powered content planning workflows.

Whether you need to review entire phases, add conditional checkpoints, or extract custom context for human review, the decorator pattern provides a clean, Pythonic way to integrate human feedback into your automated workflows.
