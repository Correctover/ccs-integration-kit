"""
AutoGen + CCS Quick Start Example

Prerequisites:
    pip install pyautogen ccs-integration-kit

Usage:
    python quickstart_autogen.py
"""

from autogen import ConversableAgent
from ccs import ConformantAutoGenAgent

# 1. Create your AutoGen agent as usual
assistant = ConversableAgent(
    "assistant",
    llm_config={"model": "gpt-4", "temperature": 0},
    system_message="You are a helpful assistant.",
)

# 2. Wrap with CCS conformance validation (4 lines!)
conformant_agent = ConformantAutoGenAgent(assistant)

# 3. Generate reply with validation
result = conformant_agent.generate_reply("What are the benefits of exercise?")

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
