import json
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent


def select_tools(claim: Dict[str, Any], policy: Dict[str, Any]) -> List[str]:
    tools = ['policy_lookup']
    if not claim.get('receipt_present', False):
        tools.append('receipt_completeness_check')
    if claim.get('exception_request', False) or claim.get('duplicate', False):
        tools.append('manual_review_check')
    return tools


def run_prompt_layer(claim: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    selected_tools = select_tools(claim, policy)
    prompt = (
        f"You are a travel reimbursement approval agent. "
        f"Review the claim for employee {claim.get('employee', 'unknown')} "
        f"in category {claim.get('category')} with amount {claim.get('amount')}. "
        f"Use the following tools in this sequence: {', '.join(selected_tools)}. "
        f"Return a concise reasoning summary and a final decision."
    )
    reasoning_summary = (
        "Assess policy fit, confirm whether the receipt requirement is satisfied, "
        "and determine whether the case should be auto-approved, partially approved, rejected, "
        "or sent for manual review."
    )
    conversation_flow = [
        "1. Receive claim input",
        "2. Select relevant tools based on claim context",
        "3. Gather policy and evidence context",
        "4. Decide and explain the outcome"
    ]
    return {
        'prompt': prompt,
        'selected_tools': selected_tools,
        'conversation_flow': conversation_flow,
        'reasoning_summary': reasoning_summary
    }


def load_json(path: str) -> Any:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def policy_lookup(policy: Dict[str, Any], claim: Dict[str, Any]) -> Dict[str, Any]:
    category = claim.get('category')
    amount = claim.get('amount')
    receipt_present = claim.get('receipt_present', False)
    duplicate = claim.get('duplicate', False)
    exception_request = claim.get('exception_request', False)

    checks = []
    reasons = []
    approved_amount = amount

    if category not in policy['allowed_categories']:
        checks.append('invalid_category')
        reasons.append('Category is not allowed by policy.')
        approved_amount = 0
    else:
        category_limit = policy['category_limits'].get(category)
        if category_limit is not None and amount > category_limit:
            checks.append('category_limit_exceeded')
            reasons.append(f'Amount exceeds the {category} limit of {category_limit}.')
            approved_amount = category_limit

    if amount >= policy['receipt_requirement_threshold'] and not receipt_present:
        checks.append('missing_receipt')
        reasons.append('Receipt is required for claims above the threshold.')

    if duplicate:
        checks.append('duplicate_claim')
        reasons.append('Duplicate claim detected.')

    if exception_request:
        checks.append('exception_request')
        reasons.append('Exception request requires manual review.')

    if amount > policy['approval_threshold']:
        checks.append('high_amount')
        reasons.append('Claim exceeds approval threshold and needs senior review.')

    return {
        'checks': checks,
        'reasons': reasons,
        'approved_amount': approved_amount,
        'policy_reference': policy['policy_name']
    }


def receipt_completeness_check(claim: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'receipt_complete': claim.get('receipt_present', False),
        'status': 'complete' if claim.get('receipt_present', False) else 'missing'
    }


def output_validator(decision: str, approved_amount: float, reasons: List[str]) -> Dict[str, Any]:
    return {
        'decision': decision,
        'approved_amount': approved_amount,
        'reason_codes': reasons,
        'valid': bool(decision and approved_amount >= 0)
    }


def decide_claim(claim: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    prompt_result = run_prompt_layer(claim, policy)
    policy_result = policy_lookup(policy, claim)
    receipt_result = receipt_completeness_check(claim)

    reasons = policy_result['reasons'][:]
    if not receipt_result['receipt_complete']:
        reasons.append('Receipt is missing.')

    manual_review = any(flag in policy_result['checks'] for flag in policy['manual_review_triggers'])
    if manual_review:
        decision = 'Manual Review'
    elif policy_result['approved_amount'] == 0:
        decision = 'Reject'
    elif policy_result['approved_amount'] < claim['amount']:
        decision = 'Partially Approve'
    else:
        decision = 'Approve'

    validation = output_validator(decision, policy_result['approved_amount'], reasons)

    return {
        'claim_id': claim['claim_id'],
        'employee': claim.get('employee'),
        'decision': decision,
        'approved_amount': validation['approved_amount'],
        'deductions_or_rejected_amount': round(claim['amount'] - validation['approved_amount'], 2),
        'missing_documents': [] if receipt_result['receipt_complete'] else ['receipt'],
        'policy_references': policy_result['policy_reference'],
        'confidence': 'high' if decision in {'Approve', 'Reject'} else 'medium',
        'explanation': ' ; '.join(reasons) if reasons else 'Claim aligns with policy.',
        'agentic_trace': {
            'prompt': prompt_result['prompt'],
            'selected_tools': prompt_result['selected_tools'],
            'conversation_flow': prompt_result['conversation_flow'],
            'reasoning_summary': prompt_result['reasoning_summary']
        }
    }


def main() -> None:
    policy = load_json(str(BASE_DIR / 'travel_policy.json'))
    claims = load_json(str(BASE_DIR / 'sample_claims.json'))

    results = [decide_claim(claim, policy) for claim in claims]
    for result in results:
        print(json.dumps(result, indent=2))
        print()


if __name__ == '__main__':
    main()
