# CCS Integration Kit

**4-line runtime conformance verification for LLM agents.**

[![CCS v1.0](https://zenodo.org/badge/DOI/10.5281/zenodo.21234580.svg)](https://doi.org/10.5281/zenodo.21234580)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

---

## What is CCS?

The **Correctover Conformance Standard (CCS)** defines runtime conformance criteria for autonomous AI agents operating in production environments. Unlike static testing frameworks that validate behavior under controlled conditions, CCS captures the stochastic nature of real-world execution where faults compound, context drifts, and decisions become irreproducible.

**Key Insight:** Single-fault self-healing achieves 97.4% success, while compound fault chains degrade to ~72%, exposing 19,251 failure paths (38.5% of test space) that remain uncovered by existing frameworks.

📄 **Paper:** [CCS v1.0 Formal Specification](https://zenodo.org/records/21234580) | DOI: 10.5281/zenodo.21234580

---

## Quick Start

**Install:**
```bash
pip install ccs-integration-kit
```

**Use (4 lines):**

```python
from ccs import ConformantCrewAgent  # or ConformantLangChainAgent, ConformantAutoGenAgent

agent = ConformantCrewAgent(my_crewai_agent)
result = agent.execute_task("Your task here")
print(result.conformant)  # True/False
```

That's it. Your agent now has 6-dimension runtime conformance verification.

---

## 6-Dimension Verification

CCS validates every agent action against six dimensions:

| Dimension | What it verifies |
|-----------|------------------|
| **Structure** | Action has valid structure (agent_id, action_type, required fields) |
| **Schema** | Output matches expected schema |
| **Latency** | Response time within bounds |
| **Cost** | Token usage within limits |
| **Identity** | Action is traceable (unique ID) |
| **Integrity** | Output is complete (non-empty, valid hash) |

**Result:** Every action is either conformant or non-conformant, with detailed metrics.

---

## Performance

| Metric | Value |
|--------|-------|
| Validation overhead (P50) | **22 µs** |
| Validation overhead (P99) | **99 µs** |
| MAPE-K decision | 50-100 µs |
| L3 Failover (end-to-end) | 949 ms |
| Self-healing rules | 87 |

**Benchmarked on:** CANON P50 across 50,000 production-derived decision traces spanning 13 LLM providers.

---

## Supported Frameworks

- ✅ **CrewAI** — `ConformantCrewAgent`
- ✅ **LangChain / LangGraph** — `ConformantLangChainAgent`
- ✅ **AutoGen** — `ConformantAutoGenAgent`

Adding support for your framework? See [Contributing](#contributing).

---

## Examples

### CrewAI

```python
from crewai import Agent
from ccs import ConformantCrewAgent

researcher = Agent(role="Researcher", goal="Find facts", backstory="Expert researcher")
conformant_agent = ConformantCrewAgent(researcher)

result = conformant_agent.execute_task("What are the top 3 programming languages in 2024?")

print(f"Conformant: {result.conformant}")
print(f"Latency: {result.latency_ms:.2f}ms")
print(f"Dimensions: {result.dimensions}")
```

### LangChain

```python
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from ccs import ConformantLangChainAgent

llm = ChatOpenAI(temperature=0)
agent = initialize_agent(tools=[], llm=llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
conformant_agent = ConformantLangChainAgent(agent)

result = conformant_agent.invoke("What is the capital of France?")

print(f"Conformant: {result.conformant}")
print(f"Output: {result.output}")
```

### AutoGen

```python
from autogen import ConversableAgent
from ccs import ConformantAutoGenAgent

assistant = ConversableAgent("assistant", llm_config={"model": "gpt-4"})
conformant_agent = ConformantAutoGenAgent(assistant)

result = conformant_agent.generate_reply("What are the benefits of exercise?")

print(f"Conformant: {result.conformant}")
print(f"Dimensions: {result.dimensions}")
```

---

## Configuration

Customize validation thresholds:

```python
conformant_agent = ConformantCrewAgent(
    my_agent,
    latency_limit_ms=5000.0,    # Max acceptable latency
    cost_limit_tokens=10000,     # Max acceptable token cost
)
```

---

## Why CCS?

### The Problem

Autonomous agents in production face a fundamental challenge: **the absence of verifiable runtime conformance criteria**. Static testing validates behavior under controlled conditions, but fails to capture:

- Stochastic execution patterns
- Fault compounding across decision chains
- Context drift over long-running tasks
- Irreproducible decisions due to non-determinism

### The Solution

CCS formalizes runtime conformance as the set inclusion `Required(τ) ⊆ Supported(τ)` for each agent transition τ. This simple criterion, grounded in empirical analysis, reveals:

- **97.4%** success rate for single-fault self-healing
- **~72%** success rate for compound fault chains
- **19,251** uncovered failure paths in existing frameworks

### The Impact

- **For developers:** Know when your agent is conformant vs. non-conformant, in real-time
- **For operations:** Detect anomalies before they cascade
- **For compliance:** Formal verification for regulated industries

---

## Comparison

| Feature | CCS | Manual Error Handling | Framework Defaults |
|---------|-----|----------------------|-------------------|
| 6-dimension verification | ✅ | ❌ | ❌ |
| Runtime conformance | ✅ | ❌ | ❌ |
| Sub-100µs overhead | ✅ (P99=99µs) | N/A | Varies |
| Multi-framework support | ✅ CrewAI/LangChain/AutoGen | Custom | Single |
| Formal specification | ✅ (DOI: 10.5281/zenodo.21234580) | ❌ | ❌ |
| Self-healing rules | ✅ (87 rules) | Custom | Limited |

---

## Contributing

We welcome contributions! To add support for your agent framework:

1. Fork the repository
2. Create a new integration in `ccs/integrations/`
3. Follow the `ConformantCrewAgent` pattern
4. Add tests and examples
5. Submit a PR

**Guidelines:**
- Maintain the 4-line integration principle
- Keep validation overhead under 100µs
- Follow the 6-dimension verification model

---

## Citation

If you use CCS in your research, please cite:

```bibtex
@software{correctover_ccs_2026,
  title={Correctover Conformance Standard v1.0: A Protocol-Level Validation Framework for LLM Agent Systems},
  author={{Correctover Research Group}},
  year={2026},
  doi={10.5281/zenodo.21234580},
  url={https://zenodo.org/records/21234580}
}
```

---

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

## Contact

- **Website:** [correctover.com](https://correctover.com)
- **GitHub:** [github.com/Correctover](https://github.com/Correctover)
- **Email:** wangguigui@correctover.com

---

**Guigui Wang | Correctover — Failover ≠ Correctover™**
