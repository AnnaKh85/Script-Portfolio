import pytest
from portfolio.resource_validation import _calc_base_simple, _calc_current_simple
from portfolio.validation_status import _assert_math

@pytest.mark.parametrize("check", [_calc_base_simple, _calc_current_simple], ids=["base", "current"])
def test_resource_formula(resource, check):
    check(resource, context="synthetic resource")

@pytest.mark.parametrize("validation, passes", [("INCORRECT_CALCULATION", True), ("SUCCESS", False)])
def test_incorrect_amount_requires_error_status(resource, validation, passes):
    resource["totalBase"] = {"value": "99.99", "validationResult": validation}
    if passes:
        _calc_base_simple(resource, context="synthetic incorrect amount")
    else:
        with pytest.raises(AssertionError, match="INCORRECT_CALCULATION"):
            _calc_base_simple(resource, context="synthetic incorrect amount")

def test_current_amount_accepts_rounded_base_fallback(resource):
    resource["totalCurrent"]["value"] = "32.60"
    _calc_current_simple(resource, context="synthetic fallback")

@pytest.mark.parametrize("value, status, accepted", [
    ("1", "SUCCESS", True),
    ("1", "INCORRECT_CALCULATION", True),
    (None, None, True),
    (None, "INCORRECT_CALCULATION", False),
    ("1", "UNEXPECTED_STATUS", False),
])
def test_math_validation_contract(value, status, accepted):
    kwargs = dict(tsn={}, block_name="synthetic.total", value=value, validation_result=status)
    if accepted:
        _assert_math(**kwargs)
    else:
        with pytest.raises(AssertionError):
            _assert_math(**kwargs)
