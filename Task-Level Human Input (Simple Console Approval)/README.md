# Task-Level Human Input (Simple Console Approval)

This folder contains examples and documentation for implementing **task-level human approval gates** in CrewAI crews using simple console-based input.

## Overview

CrewAI supports adding human approval checkpoints at the task level. When a task completes, if `human_input=True` is set, the crew execution pauses and waits for human approval before proceeding to the next task.

## Use Cases

- **Content Review**: Pause before publishing content to get human approval
- **Quality Gates**: Require approval before proceeding to expensive operations
- **Compliance Checks**: Ensure sensitive outputs are reviewed before use
- **Iterative Refinement**: Allow humans to provide feedback for task revision

## How It Works

1. **Task Configuration**: Set `human_input: true` in your task YAML config
2. **Task Execution**: When the task completes, CrewAI pauses execution
3. **Human Input**: User is prompted via console to approve, reject, or provide feedback
4. **Continue/Stop**: Based on input, crew either continues or stops execution

## Files in This Folder

### `example_human_input_crew.py`
Complete working example showing:
- How to create tasks with `human_input=True`
- Console-based approval handler
- Crew execution flow with approval gates

**Usage:**
```bash
python "Task-Level Human Input (Simple Console Approval)/example_human_input_crew.py"
```

### `example_yaml_config.yaml`
Example YAML configuration showing how to add `human_input: true` to tasks in your `config/tasks.yaml`.

### `integrate_human_input.py`
Code snippets showing how to integrate human input support into your existing `crew/run.py`:
- Updating `_build_task()` to read `human_input` from YAML
- Adding `human_input` to `TASK_PARAMS`
- Creating a handler function

### `test_human_input.py`
Test script to verify human input functionality works correctly.

## Integration Steps

### Step 1: Update `crew/run.py`

Add `human_input` to `TASK_PARAMS`:

```python
TASK_PARAMS = [
    "description",
    "expected_output",
    "agent",
    "context",
    "tools",
    "async_execution",
    "output_file",
    "output_json",
    "output_pydantic",
    "human_input",  # ADD THIS
    # ... other params
]
```

### Step 2: Update `_build_task()` Function

Modify `_build_task()` to handle `human_input` from YAML:

```python
def _build_task(...):
    # ... existing code ...
    
    # Handle human_input from YAML config
    human_input = config.get("human_input", False)
    if isinstance(human_input, str):
        human_input = human_input.lower() in ("true", "yes", "1")
    params["human_input"] = bool(human_input)
    
    # ... rest of code ...
```

### Step 3: Add to YAML Config

In `config/tasks.yaml`, add `human_input: true` to tasks that need approval:

```yaml
tasks:
  review_content_plan:
    name: review_content_plan
    agent: content_planner
    description: Review content plan for approval
    expected_output: Reviewed plan
    human_input: true  # Enable approval gate
    context_from: [create_content_plan]
```

## Console Input Options

When a task with `human_input=True` completes, you'll be prompted:

```
🔍 TASK REQUIRES HUMAN APPROVAL: [task description]
============================================================
📋 Task Output Preview: [preview of task output]
📄 Task Result: [task result]

Options:
  [y/yes] - Approve and continue
  [n/no]  - Reject and stop
  [e/edit] - Provide feedback (crew will revise)

👉 Your decision: 
```

- **`y` or `yes`**: Approve and continue to next task
- **`n` or `no`**: Reject and stop crew execution
- **`e` or `edit`**: Provide feedback (becomes part of task context for revision)

## Example Workflow

```
1. Task 1: create_content_plan (no human_input)
   → Runs automatically
   
2. Task 2: review_content_plan (human_input: true)
   → Completes task
   → ⏸️  PAUSES - waits for human approval
   → User types: "y"
   → ✅ Continues
   
3. Task 3: finalize_content_plan (no human_input)
   → Runs automatically
```

## API Integration

When using human input with the API (`app/api/crew/route.ts`):

- **Console Mode**: Human input works when running Python directly
- **API Mode**: For web-based approval, consider:
  - Using webhooks (`taskWebhookUrl`) to notify external systems
  - Implementing a separate approval endpoint
  - Using CrewAI Cloud with webhook callbacks

## Limitations

1. **Console Only**: This implementation uses console/stdin for input
2. **Synchronous**: Crew execution blocks until approval is received
3. **No Timeout**: Currently no timeout for approval (user must respond)
4. **Single User**: Designed for single-user console sessions

## Future Enhancements

- [ ] Webhook-based approval for API usage
- [ ] Approval timeout configuration
- [ ] Multi-user approval workflows
- [ ] Approval history logging
- [ ] Email/Slack notifications for pending approvals

## References

- [CrewAI Documentation: Human Input](https://docs.crewai.com/concepts/tasks#human-input)
- [CrewAI Tasks: human_input parameter](https://github.com/joaomdmoura/crewAI/blob/main/crewai/tasks/task.py)

## Testing

Run the example to test human input:

```bash
cd "Task-Level Human Input (Simple Console Approval)"
python example_human_input_crew.py
```

Or run the test script:

```bash
python test_human_input.py
```

## Notes

- Human input prompts appear in **stderr** to avoid interfering with JSON output when using `--stdin` mode
- For production deployments, consider implementing webhook-based approval instead of console input
- Human input is useful for quality gates but adds latency to crew execution

## Conclusion

Task-level human input provides a powerful mechanism for adding **quality gates** and **approval checkpoints** to CrewAI workflows. By enabling `human_input: true` on specific tasks, you can:

✅ **Ensure Quality**: Review critical outputs before they proceed through the pipeline  
✅ **Maintain Control**: Stop execution if outputs don't meet requirements  
✅ **Enable Iteration**: Provide feedback that agents can use to refine their work  
✅ **Add Safety**: Prevent automated execution of sensitive or high-risk operations  

### Key Takeaways

1. **Simple Integration**: Adding human input requires minimal code changes—just update `TASK_PARAMS` and `_build_task()` in `crew/run.py`, then add `human_input: true` to your YAML config.

2. **Flexible Workflow**: You can add approval gates at any point in your task chain, allowing you to review outputs at critical junctures without disrupting the entire workflow.

3. **Console-First Approach**: This implementation uses console/stdin for immediate usability during development and testing. For production, consider webhook-based approval systems.

4. **BAGANA AI Integration**: In the context of BAGANA AI's content planning workflow, human input is particularly valuable for:
   - Reviewing content plans before sentiment/trend analysis
   - Approving risk assessments before strategy finalization
   - Validating final content strategies before deployment

### Next Steps

1. **Try the Examples**: Run `example_human_input_crew.py` to see human input in action
2. **Integrate**: Follow `integrate_human_input.py` to add support to your `crew/run.py`
3. **Configure**: Add `human_input: true` to relevant tasks in `config/tasks.yaml`
4. **Test**: Use `test_human_input.py` to verify functionality
5. **Scale**: For production, implement webhook-based approval (see `INTEGRATION_NOTES.md`)

### When to Use Human Input

**Use human input when:**
- Outputs require human judgment or domain expertise
- Quality gates are critical for downstream tasks
- Compliance or regulatory approval is needed
- You want to provide iterative feedback to agents

**Avoid human input when:**
- Tasks run frequently in automated pipelines
- Low latency is critical
- Outputs are deterministic and don't require review
- You need fully automated workflows

By strategically placing human approval gates, you can maintain the benefits of automated AI workflows while ensuring human oversight where it matters most.
