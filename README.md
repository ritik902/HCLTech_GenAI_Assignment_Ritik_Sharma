# Travel Reimbursement Approval Agent

This prototype demonstrates a lightweight GenAI-style agent for evaluating travel reimbursement claims against a mock policy.

## What it does
- Accepts sample reimbursement claims from a JSON file.
- Uses policy context and two meaningful tools/functions:
  - policy lookup
  - receipt completeness check
- Produces a structured decision with approved amount, missing documents, policy references, confidence, and explanation.
 - Produces a structured decision with approved amount, missing documents, policy references, confidence, explanation, and an `agentic_trace` showing reasoning and selected tools.

## Files
- agent.py: Main workflow and decision logic.
- travel_policy.json: Mock policy and rules.
- sample_claims.json: Sample reimbursement claims.
 - tests/test_agent.py: Unit tests demonstrating agentic tool selection and prompt-layer trace.

## Run
```bash
python agent.py
```

## Agentic behavior and trace

- The prototype now includes a lightweight prompt layer (`run_prompt_layer`) and explicit tool selection (`select_tools`).
- Each output includes an `agentic_trace` with the generated prompt, selected tools, conversation flow, and a short reasoning summary. This allows you to demonstrate how the agent would call tools and reason before deciding.

## Tests

Run the unit tests that exercise the agentic behavior:

```bash
python -m unittest discover -s tests -v
```

## Notes for reviewers

- The solution is intentionally simple and runnable without external dependencies. Optional enhancements (LLM integration, UI, API) can be added in `requirements.txt` as extras for reviewers who want to run an extended demo.

## Design choices
- The solution is intentionally lightweight and practical rather than production-grade.
- It uses simple rule-based logic to mirror an agent workflow with tool-like functions.
- Manual review is used when policy exceptions or missing information create ambiguity.

## Assumptions and limitations
- This is a mock prototype using sample data only.
- No real employee or company data is used.
- The agent does not connect to a real LLM API, but the workflow is structured to support that extension.
