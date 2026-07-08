"""
CrewAI + CCS Quick Start Example

Prerequisites:
    pip install crewai ccs-integration-kit

Usage:
    python quickstart_crewai.py
"""

from crewai import Agent, Task, Crew
from ccs import ConformantCrewAgent

# 1. Create your CrewAI agent as usual
researcher = Agent(
    role="Researcher",
    goal="Find accurate information",
    backstory="Expert at finding facts and data",
    verbose=False,
)

# 2. Wrap with CCS conformance validation (4 lines!)
conformant_agent = ConformantCrewAgent(researcher)

# 3. Execute with validation
task = "What are the top 3 programming languages in 2024?"
result = conformant_agent.execute_task(task)

# 4. Check conformance
print(f"Conformant: {result.conformant}")
print(f"Output: {result.output if result.conformant else 'Non-conformant'}")
print(f"Latency: {result.latency_ms:.2f}ms")
print(f"Errors: {result.errors}")

# 5. Full report
print("\n6-Dimension Verification:")
for dim, passed in result.dimensions.items():
    status = "✓" if passed else "✗"
    print(f"  {status} {dim}")
