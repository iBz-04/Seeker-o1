import unittest
from instructions import Planning_Script


class DummyAgent:
    state = None

    async def run(self, prompt: str) -> str:
        return "dummy run result"

class DummyPlanningFlow(Planning_Script.PlanningFlow):
    def __init__(self, agents):
        super().__init__(agents)
        self.primary_agent = agents.get("primary", None)

class TestPlanningFlowSmall(unittest.TestCase):
    def test_get_executor_with_valid_type(self):
        dummy_primary = DummyAgent()
        dummy_search = DummyAgent()
        agents = {"primary": dummy_primary, "search": dummy_search}
        flow = DummyPlanningFlow(agents)
        executor = flow.get_executor("search")
        self.assertEqual(executor, dummy_search)

    def test_get_executor_fallback(self):
        dummy_primary = DummyAgent()
        agents = {"primary": dummy_primary}
        flow = DummyPlanningFlow(agents)
        executor = flow.get_executor("nonexistent")
        self.assertEqual(executor, dummy_primary)

if __name__ == '__main__':
    unittest.main()
