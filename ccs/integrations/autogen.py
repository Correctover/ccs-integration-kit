"""
AutoGen + CCS Integration

Wrap any AutoGen agent with CCS conformance verification in 4 lines:

    from ccs import ConformantAutoGenAgent
    agent = ConformantAutoGenAgent(my_autogen_agent)
    result = agent.generate_reply("What is the capital of France?")
    print(result.conformant)  # True/False
"""

from typing import Any, Optional
from ccs.validator import CCSValidator, ConformanceReport


class ConformantAutoGenAgent:
    """
    CCS-validated wrapper for AutoGen agents.
    
    Usage:
        from autogen import ConversableAgent
        from ccs import ConformantAutoGenAgent
        
        my_agent = ConversableAgent("assistant", llm_config={...})
        conformant_agent = ConformantAutoGenAgent(my_agent)
        
        result = conformant_agent.generate_reply("What is the capital of France?")
        if result.conformant:
            print(result.output)
    """
    
    def __init__(
        self,
        agent: Any,
        latency_limit_ms: float = 5000.0,
        cost_limit_tokens: int = 10000,
    ):
        self.agent = agent
        self.validator = CCSValidator(
            latency_limit_ms=latency_limit_ms,
            cost_limit_tokens=cost_limit_tokens,
        )
    
    def generate_reply(self, messages: Any, **kwargs) -> ConformanceReport:
        """
        Generate a reply with CCS conformance validation.
        
        Args:
            messages: The input messages (string or list of messages)
            **kwargs: Additional arguments passed to the underlying agent
        
        Returns:
            ConformanceReport with 6-dimension results
        """
        import time
        
        start_time = time.time()
        
        # Execute the underlying AutoGen agent
        try:
            if hasattr(self.agent, 'generate_reply'):
                output = self.agent.generate_reply(messages, **kwargs)
            elif hasattr(self.agent, 'chat'):
                output = self.agent.chat(messages, **kwargs)
            else:
                output = self.agent(messages, **kwargs)
        except Exception as e:
            # If execution fails, report non-conformance
            report = self.validator.validate(
                agent_id=self._get_agent_id(),
                action_type="generate_reply",
                output=None,
                latency_ms=(time.time() - start_time) * 1000,
            )
            report.errors.append(f"Execution failed: {str(e)}")
            return report
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Extract actual output from AutoGen response
        actual_output = self._extract_output(output)
        
        # Validate against CCS 6 dimensions
        report = self.validator.validate(
            agent_id=self._get_agent_id(),
            action_type="generate_reply",
            output=actual_output,
            latency_ms=latency_ms,
            tokens_used=self._extract_tokens(output),
        )
        
        return report
    
    def _get_agent_id(self) -> str:
        """Get agent identifier"""
        if hasattr(self.agent, 'name'):
            return f"autogen:{self.agent.name}"
        return f"autogen:{id(self.agent)}"
    
    def _extract_output(self, output: Any) -> Any:
        """Extract actual output from AutoGen response"""
        if isinstance(output, dict):
            return output.get('content', output.get('response', output))
        if isinstance(output, list) and len(output) > 0:
            # AutoGen may return a list of messages
            last_msg = output[-1]
            if isinstance(last_msg, dict):
                return last_msg.get('content', last_msg)
        return output
    
    def _extract_tokens(self, output: Any) -> Optional[int]:
        """Extract token count from AutoGen response"""
        if isinstance(output, dict) and 'usage' in output:
            usage = output['usage']
            if isinstance(usage, dict):
                return usage.get('total_tokens', usage.get('completion_tokens', 0))
        return None
