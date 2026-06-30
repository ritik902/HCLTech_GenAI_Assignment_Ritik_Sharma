import unittest
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent import load_json, select_tools, run_prompt_layer, decide_claim


class AgentBehaviorTests(unittest.TestCase):
    def setUp(self):
        base_dir = Path(__file__).resolve().parents[1]
        self.policy = load_json(str(base_dir / 'travel_policy.json'))
        self.claim = {
            'claim_id': 'T-100',
            'employee': 'Nina',
            'category': 'meals',
            'amount': 90,
            'receipt_present': False,
            'duplicate': False,
            'exception_request': False,
            'description': 'Dinner during travel'
        }

    def test_select_tools_includes_receipt_check_when_receipt_missing(self):
        tools = select_tools(self.claim, self.policy)
        self.assertIn('policy_lookup', tools)
        self.assertIn('receipt_completeness_check', tools)

    def test_prompt_layer_returns_agentic_trace(self):
        result = run_prompt_layer(self.claim, self.policy)
        self.assertIn('prompt', result)
        self.assertIn('selected_tools', result)
        self.assertIn('conversation_flow', result)
        self.assertIn('reasoning_summary', result)

    def test_decide_claim_includes_agentic_trace(self):
        result = decide_claim(self.claim, self.policy)
        self.assertIn('agentic_trace', result)
        self.assertIn('decision', result)


if __name__ == '__main__':
    unittest.main()
