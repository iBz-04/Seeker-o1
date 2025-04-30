import unittest
from seeker_o1.core.agent.base_agent import BaseAgent

class DummyAgent(BaseAgent):
    def execute(self, task: str, **kwargs):
        return {"task": task, "status": "done"}

class TestBaseAgent(unittest.TestCase):
    def test_initialization(self):
        agent = DummyAgent(name="TestAgent")
        self.assertEqual(agent.name, "TestAgent")
        self.assertEqual(agent.state["status"], "initialized")
        self.assertEqual(agent.history, [])
    def test_update_state(self):
        agent = DummyAgent()
        agent.update_state(status="running", step=1)
        self.assertEqual(agent.state["status"], "running")
        self.assertEqual(agent.state["step"], 1)
    def test_log_action(self):
        agent = DummyAgent()
        agent.log_action("test_action", {"foo": "bar"})
        self.assertEqual(len(agent.history), 1)
        self.assertEqual(agent.history[0]["action"], "test_action")
    def test_get_info(self):
        agent = DummyAgent(name="InfoAgent")
        info = agent.get_info()
        self.assertEqual(info["name"], "InfoAgent")
        self.assertEqual(info["state"], agent.state)
        self.assertEqual(info["history_length"], 0)

if __name__ == "__main__":
    unittest.main() 