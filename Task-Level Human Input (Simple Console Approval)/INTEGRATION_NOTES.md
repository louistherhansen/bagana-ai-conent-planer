# Integration Notes: Task-Level Human Input

## Connection to Integration Artifact

This folder implements **task-level human approval gates** as referenced in `project-context/2.build/integration.md`.

## Use Case in BAGANA AI Context

For the BAGANA AI content planning workflow, human input can be added at critical checkpoints:

1. **After Content Plan Creation** (`create_content_plan`)
   - Review plan before sentiment/trend analysis
   - Ensure plan meets brand requirements

2. **After Sentiment Analysis** (`analyze_sentiment`)
   - Approve risk assessment before proceeding
   - Review flagged risks

3. **Before Final Content Strategy** (`create_content_strategy`)
   - Final approval before generating strategy
   - Opportunity to provide feedback

## Integration with Existing Crew

To add human input to your existing crew workflow:

### Option 1: Add to Existing Tasks

Edit `config/tasks.yaml` and add `human_input: true` to specific tasks:

```yaml
tasks:
  analyze_sentiment:
    name: analyze_sentiment
    agent: sentiment_analyst
    # ... existing config ...
    human_input: true  # Add this line
```

### Option 2: Add Review Tasks

Add new review tasks between existing tasks:

```yaml
tasks:
  # Existing task
  create_content_plan:
    # ... existing config ...
  
  # NEW: Review task with human input
  review_content_plan:
    name: review_content_plan
    agent: content_planner
    description: Review content plan before proceeding to sentiment analysis
    expected_output: Approved content plan
    human_input: true
    context_from: [create_content_plan]
  
  # Existing task (now uses reviewed plan)
  analyze_sentiment:
    # ... existing config ...
    context_from: [review_content_plan]  # Changed from create_content_plan
```

## API Considerations

When using human input with the API (`app/api/crew/route.ts`):

- **Console Mode**: Works when running Python directly (`python -m crew.run --stdin`)
- **API Mode**: Requires webhook-based approval or separate approval endpoint
- **CrewAI Cloud**: Supports `taskWebhookUrl` for async approval workflows

## Recommended Approach

For BAGANA AI MVP:

1. **Development/Testing**: Use console-based human input (this folder's examples)
2. **Production**: Implement webhook-based approval via `taskWebhookUrl` in API route
3. **Future**: Add approval UI in Next.js frontend (`/chat` or `/review` page)

## Files Reference

- `example_human_input_crew.py` - Standalone example
- `example_yaml_config.yaml` - YAML configuration pattern
- `integrate_human_input.py` - Code snippets for `crew/run.py` integration
- `test_human_input.py` - Test suite
- `README.md` - Complete documentation

## Next Steps

1. Review `integrate_human_input.py` for code changes needed in `crew/run.py`
2. Test with `example_human_input_crew.py` to understand behavior
3. Add `human_input: true` to tasks in `config/tasks.yaml` as needed
4. For API integration, implement webhook handler in `app/api/crew/webhook/route.ts`
