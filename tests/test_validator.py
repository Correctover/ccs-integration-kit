"""
Test CCS Validator Core Functionality
"""

import pytest
from ccs.validator import CCSValidator, ConformanceReport


def test_validator_initialization():
    """Test validator can be initialized"""
    validator = CCSValidator()
    assert validator.latency_limit_ms == 5000.0
    assert validator.cost_limit_tokens == 10000


def test_structure_validation_pass():
    """Test structure validation passes for valid input"""
    validator = CCSValidator()
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output="Valid output",
    )
    assert report.structure is True


def test_structure_validation_fail_empty_agent():
    """Test structure validation fails for empty agent_id"""
    validator = CCSValidator()
    report = validator.validate(
        agent_id="",
        action_type="execute",
        output="Valid output",
    )
    assert report.structure is False


def test_structure_validation_fail_none_output():
    """Test structure validation fails for None output"""
    validator = CCSValidator()
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output=None,
    )
    assert report.structure is False


def test_schema_validation_pass():
    """Test schema validation passes for matching schema"""
    validator = CCSValidator()
    output = {"name": "John", "age": 30}
    schema = {"name": str, "age": int}
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output=output,
        expected_schema=schema,
    )
    assert report.schema is True


def test_schema_validation_fail_missing_key():
    """Test schema validation fails for missing key"""
    validator = CCSValidator()
    output = {"name": "John"}
    schema = {"name": str, "age": int}
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output=output,
        expected_schema=schema,
    )
    assert report.schema is False


def test_schema_validation_fail_wrong_type():
    """Test schema validation fails for wrong type"""
    validator = CCSValidator()
    output = {"name": "John", "age": "thirty"}
    schema = {"name": str, "age": int}
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output=output,
        expected_schema=schema,
    )
    assert report.schema is False


def test_latency_validation_pass():
    """Test latency validation passes within limit"""
    validator = CCSValidator(latency_limit_ms=5000.0)
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output="Valid output",
        latency_ms=1000.0,
    )
    assert report.latency is True


def test_latency_validation_fail():
    """Test latency validation fails when exceeding limit"""
    validator = CCSValidator(latency_limit_ms=5000.0)
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output="Valid output",
        latency_ms=10000.0,
    )
    assert report.latency is False


def test_cost_validation_pass():
    """Test cost validation passes within limit"""
    validator = CCSValidator(cost_limit_tokens=10000)
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output="Valid output",
        tokens_used=5000,
    )
    assert report.cost is True


def test_cost_validation_fail():
    """Test cost validation fails when exceeding limit"""
    validator = CCSValidator(cost_limit_tokens=10000)
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output="Valid output",
        tokens_used=20000,
    )
    assert report.cost is False


def test_identity_validation_pass():
    """Test identity validation always passes (action_id is generated)"""
    validator = CCSValidator()
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output="Valid output",
    )
    assert report.identity is True
    assert len(report.action_id) > 0


def test_integrity_validation_pass():
    """Test integrity validation passes for non-empty output"""
    validator = CCSValidator()
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output="Valid output",
    )
    assert report.integrity is True
    assert report.output_hash is not None


def test_integrity_validation_fail_empty_string():
    """Test integrity validation fails for empty string"""
    validator = CCSValidator()
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output="   ",
    )
    assert report.integrity is False


def test_integrity_validation_fail_empty_dict():
    """Test integrity validation fails for empty dict"""
    validator = CCSValidator()
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute",
        output={},
    )
    assert report.integrity is False


def test_conformance_report_conformant():
    """Test ConformanceReport.conformant property"""
    report = ConformanceReport(
        timestamp="2026-07-08T19:30:00Z",
        agent_id="test_agent",
        action_id="abc123",
        structure=True,
        schema=True,
        latency=True,
        cost=True,
        identity=True,
        integrity=True,
    )
    assert report.conformant is True


def test_conformance_report_non_conformant():
    """Test ConformanceReport.conformant property when any dimension fails"""
    report = ConformanceReport(
        timestamp="2026-07-08T19:30:00Z",
        agent_id="test_agent",
        action_id="abc123",
        structure=True,
        schema=True,
        latency=True,
        cost=False,  # One dimension fails
        identity=True,
        integrity=True,
    )
    assert report.conformant is False


def test_full_validation_flow():
    """Test complete validation flow"""
    validator = CCSValidator(
        latency_limit_ms=5000.0,
        cost_limit_tokens=10000,
    )
    
    report = validator.validate(
        agent_id="test_agent",
        action_type="execute_task",
        output={"result": "success", "data": [1, 2, 3]},
        latency_ms=1500.0,
        tokens_used=3000,
        expected_schema={"result": str, "data": list},
    )
    
    # All dimensions should pass
    assert report.conformant is True
    assert report.structure is True
    assert report.schema is True
    assert report.latency is True
    assert report.cost is True
    assert report.identity is True
    assert report.integrity is True
    
    # Metrics should be recorded
    assert report.latency_ms == 1500.0
    assert report.tokens_used == 3000
    assert report.output_hash is not None
    assert len(report.errors) == 0
    
    # Report should be serializable
    report_dict = report.to_dict()
    assert "timestamp" in report_dict
    assert "agent_id" in report_dict
    assert "conformant" in report_dict
    assert "dimensions" in report_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
