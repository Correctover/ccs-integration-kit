"""
CCS Integration Kit — Wrapper Tests (unittest + mock)

Tests the 3 ConformantAgent wrappers (CrewAI, AutoGen, LangChain)
without requiring any framework dependencies.

Each test mocks the underlying agent to verify:
  - execute_task/invoke/generate_reply returns ConformanceReport
  - 6-dimension validation is applied
  - Errors from underlying agent are captured
"""
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from ccs.validator import CCSValidator, ConformanceReport
from ccs.integrations.crewai import ConformantCrewAgent
from ccs.integrations.autogen import ConformantAutoGenAgent
from ccs.integrations.langchain import ConformantLangChainAgent


class TestConformantCrewAgent(unittest.TestCase):
    """ConformantCrewAgent — CrewAI wrapper tests."""

    def setUp(self):
        self.mock_agent = MagicMock()
        self.mock_agent.role = "TestResearcher"
        self.wrapper = ConformantCrewAgent(self.mock_agent)

    def test_execute_task_success(self):
        """Happy path: agent returns output → report is conformant."""
        self.mock_agent.execute_task.return_value = "Paris is the capital of France."

        report = self.wrapper.execute_task("What is the capital of France?")

        self.assertIsInstance(report, ConformanceReport)
        self.assertTrue(report.conformant)
        self.assertEqual(report.agent_id, "crewai:TestResearcher")
        self.assertEqual(report.output, "Paris is the capital of France.")
        self.assertIsNotNone(report.latency_ms)

    def test_execute_task_agent_raises(self):
        """Agent raises → report is NOT conformant with error."""
        self.mock_agent.execute_task.side_effect = RuntimeError("API timeout")

        report = self.wrapper.execute_task("Do something")

        self.assertIsInstance(report, ConformanceReport)
        self.assertFalse(report.conformant)
        self.assertGreater(len(report.errors), 0)
        self.assertIn("API timeout", report.errors[0])

    def test_execute_task_passes_kwargs(self):
        """Additional kwargs are forwarded to the underlying agent."""
        self.mock_agent.execute_task.return_value = "done"
        self.wrapper.execute_task("task", context="extra", max_iterations=5)
        self.mock_agent.execute_task.assert_called_once_with("task", context="extra", max_iterations=5)

    def test_agent_id_fallback(self):
        """Agent without role attribute gets fallback ID."""
        class _AgentNoRole:
            def execute_task(self, task, **kwargs):
                return "ok"

        wrapper = ConformantCrewAgent(_AgentNoRole())
        report = wrapper.execute_task("test")
        self.assertIn("crewai:", report.agent_id)

    def test_custom_validator_params(self):
        """Custom latency/token limits are passed to the validator."""
        wrapper = ConformantCrewAgent(self.mock_agent, latency_limit_ms=1000.0, cost_limit_tokens=500)
        self.assertEqual(wrapper.validator.latency_limit_ms, 1000.0)
        self.assertEqual(wrapper.validator.cost_limit_tokens, 500)


class TestConformantAutoGenAgent(unittest.TestCase):
    """ConformantAutoGenAgent — AutoGen wrapper tests."""

    def setUp(self):
        self.mock_agent = MagicMock()
        self.mock_agent.name = "AssistantBot"
        self.wrapper = ConformantAutoGenAgent(self.mock_agent)

    def test_generate_reply_dict_output(self):
        """AutoGen returns dict with 'content' → extracted."""
        self.mock_agent.generate_reply.return_value = {
            "content": "Hello from AutoGen",
            "role": "assistant"
        }

        report = self.wrapper.generate_reply("Hi")

        self.assertIsInstance(report, ConformanceReport)
        self.assertTrue(report.conformant)
        self.assertEqual(report.agent_id, "autogen:AssistantBot")
        self.assertEqual(report.output, "Hello from AutoGen")

    def test_generate_reply_list_of_messages(self):
        """AutoGen returns list of messages → last message content extracted."""
        self.mock_agent.generate_reply.return_value = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello back!"},
        ]

        report = self.wrapper.generate_reply("Hi team")
        self.assertTrue(report.conformant)
        self.assertEqual(report.output, "Hello back!")

    def test_generate_reply_uses_chat_fallback(self):
        """Agent without generate_reply → tries .chat()."""
        class _ChatOnlyAgent:
            name = "ChatBot"
            def chat(self, messages, **kwargs):
                return "chat result"

        wrapper = ConformantAutoGenAgent(_ChatOnlyAgent())
        report = wrapper.generate_reply("Hello")
        self.assertTrue(report.conformant)
        self.assertEqual(report.output, "chat result")

    def test_generate_reply_fallback_to_call(self):
        """Agent without generate_reply or chat → falls back to __call__."""
        class _CallOnlyAgent:
            name = "CallBot"
            def __call__(self, messages, **kwargs):
                return "call result"

        wrapper = ConformantAutoGenAgent(_CallOnlyAgent())
        report = wrapper.generate_reply("Hello")
        self.assertTrue(report.conformant)
        self.assertEqual(report.output, "call result")

    def test_generate_reply_agent_raises(self):
        """Agent raises → non-conformant report with error."""
        self.mock_agent.generate_reply.side_effect = ValueError("Bad input")

        report = self.wrapper.generate_reply("crash me")
        self.assertFalse(report.conformant)
        self.assertGreater(len(report.errors), 0)

    def test_generate_reply_with_token_usage(self):
        """Dict with 'usage' → token count extracted."""
        self.mock_agent.generate_reply.return_value = {
            "content": "Result",
            "usage": {"total_tokens": 150}
        }

        report = self.wrapper.generate_reply("Test")
        self.assertEqual(report.tokens_used, 150)


class TestConformantLangChainAgent(unittest.TestCase):
    """ConformantLangChainAgent — LangChain/LangGraph wrapper tests."""

    def setUp(self):
        self.mock_agent = MagicMock()
        self.mock_agent.name = "LCBot"
        self.wrapper = ConformantLangChainAgent(self.mock_agent)

    def test_invoke_dict_output(self):
        """LangChain returns dict with 'output' → extracted."""
        self.mock_agent.invoke.return_value = {
            "output": "LangChain result",
            "intermediate_steps": []
        }

        report = self.wrapper.invoke("Hello")

        self.assertIsInstance(report, ConformanceReport)
        self.assertTrue(report.conformant)
        self.assertEqual(report.agent_id, "langchain:LCBot")
        self.assertEqual(report.output, "LangChain result")

    def test_invoke_uses_run_fallback(self):
        """Agent without invoke() → tries .run()."""
        class _RunOnlyAgent:
            name = "RunBot"
            def run(self, input_text, **kwargs):
                return "run result"

        wrapper = ConformantLangChainAgent(_RunOnlyAgent())
        report = wrapper.invoke("Test")
        self.assertTrue(report.conformant)
        self.assertEqual(report.output, "run result")

    def test_invoke_string_output(self):
        """Plain string output → passed through directly."""
        self.mock_agent.invoke.return_value = "Simple string response"

        report = self.wrapper.invoke("Hi")
        self.assertTrue(report.conformant)
        self.assertEqual(report.output, "Simple string response")

    def test_invoke_result_key_fallback(self):
        """Dict without 'output' key → falls back to 'result'."""
        self.mock_agent.invoke.return_value = {"result": "fallback result"}

        report = self.wrapper.invoke("Test")
        self.assertEqual(report.output, "fallback result")

    def test_invoke_agent_raises(self):
        """Agent raises → non-conformant report with error."""
        self.mock_agent.invoke.side_effect = ConnectionError("LLM unavailable")

        report = self.wrapper.invoke("Crash")
        self.assertFalse(report.conformant)
        self.assertGreater(len(report.errors), 0)

    def test_invoke_with_token_usage(self):
        """Dict with 'token_usage' → token count extracted."""
        self.mock_agent.invoke.return_value = {
            "output": "Result",
            "token_usage": {"total_tokens": 200}
        }

        report = self.wrapper.invoke("Test")
        self.assertEqual(report.tokens_used, 200)

    def test_custom_validator_params(self):
        """Custom params propagated."""
        wrapper = ConformantLangChainAgent(self.mock_agent, latency_limit_ms=2000.0, cost_limit_tokens=8000)
        self.assertEqual(wrapper.validator.latency_limit_ms, 2000.0)
        self.assertEqual(wrapper.validator.cost_limit_tokens, 8000)


class TestConformanceReport(unittest.TestCase):
    """ConformanceReport edge cases."""

    def test_conformant_all_pass(self):
        report = ConformanceReport(
            timestamp="t", agent_id="a", action_id="x",
            structure=True, schema=True, latency=True,
            cost=True, identity=True, integrity=True,
        )
        self.assertTrue(report.conformant)
        self.assertTrue(all(report.dimensions.values()))

    def test_conformant_any_fail(self):
        report = ConformanceReport(
            timestamp="t", agent_id="a", action_id="x",
            structure=True, schema=False, latency=True,
            cost=True, identity=True, integrity=True,
        )
        self.assertFalse(report.conformant)
        self.assertFalse(report.dimensions["schema"])

    def test_to_dict_serialization(self):
        report = ConformanceReport(
            timestamp="2026-07-14T10:00:00Z",
            agent_id="test_agent",
            action_id="abc123",
            output="hello",
        )
        d = report.to_dict()
        self.assertIn("timestamp", d)
        self.assertIn("dimensions", d)
        self.assertIn("metrics", d)
        self.assertEqual(d["agent_id"], "test_agent")

    def test_errors_list(self):
        report = ConformanceReport(
            timestamp="t", agent_id="a", action_id="x",
            errors=["error1", "error2"],
        )
        self.assertEqual(len(report.errors), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
