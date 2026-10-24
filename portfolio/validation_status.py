from typing import Dict, Optional, Sequence
MATH_ALLOWED = {"SUCCESS", "INCORRECT_CALCULATION", None}
def _as_dict(value: Optional[object]) -> Dict:
    return value if isinstance(value, dict) else {}


def _extract_value(block: Optional[Dict], value_key: str = "value") -> Optional[object]:
    block = _as_dict(block)
    return block.get(value_key)


def _log_validation_error(
    *,
    tsn: Optional[Dict],
    block_name: str,
    validation_result: Optional[str],
    value: Optional[object],
) -> None:
    tsn = _as_dict(tsn)
    num = _extract_value(tsn.get("num"))
    code = _extract_value(tsn.get("code"))
    print(
        f"В позиции {num} шифр: {code} в блоке {block_name} в поле validationResult "
        f"заполнено [{validation_result}], значение в поле value = [{value}]"
    )


def _assert_allowed(
    *,
    tsn: Optional[Dict],
    block_name: str,
    validation_result: Optional[str],
    value: Optional[object],
    allowed_values: Sequence[Optional[str]],
) -> None:
    if validation_result not in allowed_values:
        _log_validation_error(
            tsn=tsn,
            block_name=block_name,
            validation_result=validation_result,
            value=value,
        )
    assert validation_result in allowed_values


def _assert_math(
    *,
    tsn: Optional[Dict],
    block_name: str,
    value: Optional[object],
    validation_result: Optional[str],
) -> None:
    _assert_allowed(
        tsn=tsn,
        block_name=block_name,
        validation_result=validation_result,
        value=value,
        allowed_values=MATH_ALLOWED,
    )
    if value is None and validation_result == "INCORRECT_CALCULATION":
        _log_validation_error(
            tsn=tsn,
            block_name=block_name,
            validation_result=validation_result,
            value=value,
        )
    assert not (value is None and validation_result == "INCORRECT_CALCULATION")
