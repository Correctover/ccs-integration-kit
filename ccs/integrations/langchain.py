"""
LangChain/LangGraph + CCS Integration

Wrap any LangChain agent with CCS conformance verification in 4 lines:

    from ccs import ConformantLangChainAgent
    agent = ConformantLangChainAgent(my_langchain_agent)
    result = agent.invoke("What is the capital of France?")
    print(result.conformant)  # True/False
"""

from typing import Any, Optional
from ccs.validator import CCSValidator, ConformanceReport


class ConformantLangChainAgent:
    """
    CCS-validated wrapper for LangChain/LangGraph agents.
    
    Usage:
        from langchain.agents import initialize_agent
        from ccs import ConformantLangChainAgent
        
        my_agent = initialize_agent(tools, llm)
        conformant_agent = ConformantLangChainAgent(my_agent)
        
        result = conformant_agent.invoke("What is the capital of France?")
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
    
    def invoke(self, input_text: str, **kwargs) -> ConformanceReport:
        """
        Invoke the agent with CCS conformance validation.
        
        Args:
            input_text: The input prompt
            **kwargs: Additional arguments passed to the underlying agent
        
        Returns:
            ConformanceReport with 6-dimension results
        """
        import time
        
        start_time = time.time()
        
        # Execute the underlying LangChain agent
        try:
            if hasattr(self.agent, 'invoke'):
                output = self.agent.invoke(input_text, **kwargs)
            elif hasattr(self.agent, 'run'):
                output = self.agent.run(input_text, **kwargs)
            else:
                output = self.agent(input_text, **kwargs)
        except Exception as e:
            # If execution fails, report non-conformance
            report = self.validator.validate(
                agent_id=self._get_agent_id(),
                action_type="invoke",
                output=None,
                latency_ms=(time.time() - start_time) * 1000,
            )
            report.errors.append(f"Execution failed: {str(e)}")
            return report
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Extract actual output from LangChain response
        actual_output = self._extract_output(output)
        
        # Validate against CCS 6 dimensions
        report = self.validator.validate(
            agent_id=self._get_agent_id(),
            action_type="invoke",
            output=actual_output,
            latency_ms=latency_ms,
            tokens_used=self._extract_tokens(output),
        )
        
        return report
    
    def _get_agent_id(self) -> str:
        """Get agent identifier"""
        if hasattr(self.agent, 'name'):
            return f"langchain:{self.agent.name}"
        return f"langchain:{id(self.agent)}"
    
    def _extract_output(self, output: Any) -> Any:
        """Extract actual output from LangChain response"""
        if isinstance(output, dict):
            return output.get('output', output.get('result', output))
        return output
    
    def _extract_tokens(self, output: Any) -> Optional[int]:
        """Extract token count from LangChain response"""
        if isinstance(output, dict) and 'token_usage' in output:
            usage = output['token_usage']
            if isinstance(usage, dict):
                return usage.get('total_tokens', usage.get('completion_tokens', 0))
        return None
