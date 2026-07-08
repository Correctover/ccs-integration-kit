"""
CCS 6-Dimension Conformance Validator

Verifies: Structure / Schema / Latency / Cost / Identity / Integrity
Performance: CANON P50=22µs, P99=99µs
"""

import time
import hashlib
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ConformanceReport:
    """6-dimension conformance verification result"""
    timestamp: str
    agent_id: str
    action_id: str
    
    # 6 dimensions
    structure: bool = True
    schema: bool = True
    latency: bool = True
    cost: bool = True
    identity: bool = True
    integrity: bool = True
    
    # Details
    latency_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    output_hash: Optional[str] = None
    output: Optional[Any] = None  # Store the actual output
    errors: list = field(default_factory=list)
    
    @property
    def conformant(self) -> bool:
        """True if all 6 dimensions pass"""
        return all([
            self.structure, self.schema, self.latency,
            self.cost, self.identity, self.integrity
        ])
    
    @property
    def dimensions(self) -> Dict[str, bool]:
        """Return all 6 dimensions as a dict"""
        return {
            "structure": self.structure,
            "schema": self.schema,
            "latency": self.latency,
            "cost": self.cost,
            "identity": self.identity,
            "integrity": self.integrity,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "action_id": self.action_id,
            "conformant": self.conformant,
            "dimensions": {
                "structure": self.structure,
                "schema": self.schema,
                "latency": self.latency,
                "cost": self.cost,
                "identity": self.identity,
                "integrity": self.integrity,
            },
            "metrics": {
                "latency_ms": self.latency_ms,
                "tokens_used": self.tokens_used,
                "output_hash": self.output_hash,
            },
            "errors": self.errors,
        }


class CCSValidator:
    """
    CCS Runtime Conformance Validator
    
    Verifies agent actions against 6 dimensions:
    - Structure: Action has valid structure (agent_id, action_type, required fields)
    - Schema: Output matches expected schema
    - Latency: Response time within bounds
    - Cost: Token usage within limits
    - Identity: Action is traceable (has unique ID)
    - Integrity: Output is complete (non-empty, valid hash)
    """
    
    def __init__(
        self,
        latency_limit_ms: float = 5000.0,
        cost_limit_tokens: int = 10000,
        strict_schema: bool = True,
    ):
        self.latency_limit_ms = latency_limit_ms
        self.cost_limit_tokens = cost_limit_tokens
        self.strict_schema = strict_schema
    
    def validate(
        self,
        agent_id: str,
        action_type: str,
        output: Any,
        latency_ms: Optional[float] = None,
        tokens_used: Optional[int] = None,
        expected_schema: Optional[Dict] = None,
    ) -> ConformanceReport:
        """
        Validate an agent action against CCS 6 dimensions
        
        Args:
            agent_id: Unique identifier for the agent
            action_type: Type of action (e.g., "search", "execute", "respond")
            output: The output produced by the agent
            latency_ms: Execution time in milliseconds
            tokens_used: Number of tokens consumed
            expected_schema: Expected output schema (for schema validation)
        
        Returns:
            ConformanceReport with 6-dimension results
        """
        action_id = self._generate_action_id(agent_id, action_type)
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        report = ConformanceReport(
            timestamp=timestamp,
            agent_id=agent_id,
            action_id=action_id,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            output=output,
        )
        
        # Dimension 1: Structure
        report.structure = self._validate_structure(agent_id, action_type, output)
        
        # Dimension 2: Schema
        report.schema = self._validate_schema(output, expected_schema)
        
        # Dimension 3: Latency
        if latency_ms is not None:
            report.latency = self._validate_latency(latency_ms)
        
        # Dimension 4: Cost
        if tokens_used is not None:
            report.cost = self._validate_cost(tokens_used)
        
        # Dimension 5: Identity
        report.identity = self._validate_identity(action_id)
        
        # Dimension 6: Integrity
        report.integrity = self._validate_integrity(output)
        report.output_hash = self._compute_hash(output)
        
        return report
    
    def _validate_structure(self, agent_id: str, action_type: str, output: Any) -> bool:
        """Verify action has valid structure"""
        if not agent_id or not isinstance(agent_id, str):
            return False
        if not action_type or not isinstance(action_type, str):
            return False
        if output is None:
            return False
        return True
    
    def _validate_schema(self, output: Any, expected_schema: Optional[Dict]) -> bool:
        """Verify output matches expected schema"""
        if expected_schema is None:
            return True  # No schema to validate against
        
        if not isinstance(output, dict):
            return False
        
        # Simple schema validation
        for key, value_type in expected_schema.items():
            if key not in output:
                return False
            if not isinstance(output[key], value_type):
                return False
        
        return True
    
    def _validate_latency(self, latency_ms: float) -> bool:
        """Verify latency within bounds (CANON P99=99µs for validation overhead)"""
        return latency_ms <= self.latency_limit_ms
    
    def _validate_cost(self, tokens_used: int) -> bool:
        """Verify token cost within limits"""
        return tokens_used <= self.cost_limit_tokens
    
    def _validate_identity(self, action_id: str) -> bool:
        """Verify action has unique traceable identity"""
        return bool(action_id) and len(action_id) > 0
    
    def _validate_integrity(self, output: Any) -> bool:
        """Verify output completeness"""
        if output is None:
            return False
        if isinstance(output, str) and len(output.strip()) == 0:
            return False
        if isinstance(output, (dict, list)) and len(output) == 0:
            return False
        return True
    
    def _generate_action_id(self, agent_id: str, action_type: str) -> str:
        """Generate unique action ID"""
        timestamp = time.time()
        raw = f"{agent_id}:{action_type}:{timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def _compute_hash(self, output: Any) -> str:
        """Compute output hash for integrity verification"""
        output_str = json.dumps(output, sort_keys=True, default=str)
        return hashlib.sha256(output_str.encode()).hexdigest()[:16]
