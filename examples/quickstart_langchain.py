"""
LangChain + CCS Quick Start Example

Prerequisites:
    pip install langchain langchain-openai ccs-integration-kit

Usage:
    python quickstart_langchain.py
"""

from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from ccs import ConformantLangChainAgent

# 1. Create your LangChain agent as usual
llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    tools=[],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

# 2. Wrap with CCS conformance validation (4 lines!)
conformant_agent = ConformantLangChainAgent(agent)

# 3. Invoke with validation
result = conformant_agent.invoke("What is the capital of France?")

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
