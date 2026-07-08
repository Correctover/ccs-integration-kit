"""
CCS - Correctover Conformance Standard
Runtime Verification for LLM Agent Systems

v1.0 | DOI: 10.5281/zenodo.21234580
Performance: CANON P50=22µs, P99=99µs

6-Dimension Contract Verification:
  - Structure: Action structure integrity
  - Schema: Output schema compliance
  - Latency: Response time bounds
  - Cost: Token cost predictability
  - Identity: Action traceability
  - Integrity: Output completeness
"""

__version__ = "1.0.0"
__author__ = "Correctover Research Group"

from ccs.validator import CCSValidator, ConformanceReport
from ccs.integrations.crewai import ConformantCrewAgent
from ccs.integrations.langchain import ConformantLangChainAgent
from ccs.integrations.autogen import ConformantAutoGenAgent

__all__ = [
    "CCSValidator",
    "ConformanceReport",
    "ConformantCrewAgent",
    "ConformantLangChainAgent",
    "ConformantAutoGenAgent",
]
