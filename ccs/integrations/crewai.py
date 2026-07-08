"""
CrewAI + CCS Integration

Wrap any CrewAI agent with CCS conformance verification in 4 lines:

    from ccs import ConformantCrewAgent
    agent = ConformantCrewAgent(my_crewai_agent)
    result = agent.execute_task(task)
    print(result.conformant)  # True/False
"""

from typing import Any, Optional
from ccs.validator import CCSValidator, ConformanceReport


class ConformantCrewAgent:
    """
    CCS-validated wrapper for CrewAI agents.
    
    Usage:
        from crewai import Agent
        from ccs import ConformantCrewAgent
        
        my_agent = Agent(role="Researcher", goal="Find facts")
        conformant_agent = ConformantCrewAgent(my_agent)
        
        result = conformant_agent.execute_task("What is the capital of France?")
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
    
    def execute_task(self, task: str, **kwargs) -> ConformanceReport:
        """
        Execute a task with CCS conformance validation.
        
        Args:
            task: The task description
            **kwargs: Additional arguments passed to the underlying agent
        
        Returns:
            ConformanceReport with 6-dimension results
        """
        import time
        
        start_time = time.time()
        
        # Execute the underlying CrewAI agent
        try:
            output = self.agent.execute_task(task, **kwargs)
        except Exception as e:
            # If execution fails, report non-conformance
            report = self.validator.validate(
                agent_id=self._get_agent_id(),
                action_type="execute_task",
                output=None,
                latency_ms=(time.time() - start_time) * 1000,
            )
            report.errors.append(f"Execution failed: {str(e)}")
            return report
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Validate against CCS 6 dimensions
        report = self.validator.validate(
            agent_id=self._get_agent_id(),
            action_type="execute_task",
            output=output,
            latency_ms=latency_ms,
            tokens_used=self._estimate_tokens(output),
        )
        
        return report
    
    def _get_agent_id(self) -> str:
        """Get agent identifier"""
        if hasattr(self.agent, 'role'):
            return f"crewai:{self.agent.role}"
        return f"crewai:{id(self.agent)}"
    
    def _estimate_tokens(self, output: Any) -> int:
        """Estimate token count (rough: 4 chars per token)"""
        if isinstance(output, str):
            return len(output) // 4
        return 0
