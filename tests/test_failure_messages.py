import json
import subprocess
from unittest.mock import patch

import sympy as sp

from integral_compass import analyze, integrate
from integral_compass.models import IntegrationResult
from integral_compass.search import search_core


def test_risch_certificate_is_a_string_while_depth_exhaustion_is_none():
    certified = integrate("exp(-x**2)")
    assert certified == "None, verified by Risch"
    assert isinstance(certified, str)
    assert integrate("x*exp(x)", 1) is None


def test_root_unsupported_rule_has_its_own_reason():
    result = analyze("Abs(x)", 1)
    assert result.status == "unknown"
    assert result.reason_code == "unsupported_rule"
    assert result.value.startswith("unknown, unsupported rule:")
    assert "absolute-value" in result.value


def test_unresolved_branches_are_not_misreported_as_exhausted():
    result = analyze("log(x)**2", 2)
    assert result.status == "unknown"
    assert result.reason_code == "unresolved_branch"
    assert not result.search_complete
    assert result.value.startswith("unknown, unresolved branches:")
    assert "log(x)**2" in result.value
    assert any(node["status"] == "exhausted" for node in result.search_tree)
    assert any(node["reason_code"] == "unresolved_branch"
               for node in result.search_tree if node.get("reason_code"))
    assert analyze("log(x)**2", 3).status == "elementary"


def test_timeout_message_explains_the_limit():
    value = integrate("x", 1, timeout=0.000001)
    assert value.startswith("unknown, timeout:")
    assert "seconds" in value


def test_worker_crash_and_invalid_json_are_backend_errors():
    for returncode, output in [(1, ""), (0, "not json")]:
        with patch("integral_compass.api.subprocess.run", return_value=
                   subprocess.CompletedProcess([], returncode, stdout=output, stderr="")):
            result = analyze("x", 1)
        assert result.status == "unknown"
        assert result.reason_code == "backend_error"
        assert result.value.startswith("unknown, backend error:")


def test_forced_verification_failure_is_not_none_or_an_answer():
    x = sp.Symbol("x", real=True)
    with patch("integral_compass.search._verified", side_effect=[True, False]):
        result = search_core(x, x, 1)
    assert result.status == "unknown"
    assert result.reason_code == "verification_failed"
    assert result.value.startswith("unknown, verification failed:")


def test_json_and_text_represent_the_same_public_value():
    x = sp.Symbol("x", real=True)
    for result in [
        IntegrationResult("non_elementary", x, x, method="risch"),
        IntegrationResult("exhausted", x, x),
        IntegrationResult("unknown", x, x, reason="example", reason_code="unsupported_rule"),
    ]:
        data = json.loads(json.dumps(result.to_dict()))
        assert data["value"] == result.value
        assert repr(result.value) in result.explain()
