from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Dict, Iterable, Optional


def decimal_from(value: Optional[object], default: str) -> Decimal:
    if isinstance(value, dict):
        value = value.get("value")
    if value is None or value == "":
        return Decimal(default)
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def get_coefficient(coefficients: Optional[Iterable]) -> Decimal:
    values = []
    if coefficients:
        for coefficient in coefficients:
            if isinstance(coefficient, dict):
                if "values" in coefficient:
                    nested = coefficient.get("values")
                    if isinstance(nested, list):
                        values.extend(nested)
                    elif isinstance(nested, dict):
                        values.append(nested)
                    else:
                        values.append({"value": nested})
                if "value" in coefficient:
                    values.append(coefficient)
            else:
                values.append({"value": coefficient})

    if not values:
        return Decimal("1")

    product = Decimal("1")
    for coefficient_value in values:
        product *= decimal_from(coefficient_value, "1")
    return product


def quantize_two(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def extract_text(field: Optional[Dict]) -> str:
    if isinstance(field, dict):
        return str(field.get("value") or "")
    return str(field or "")


__all__ = [
    "decimal_from",
    "extract_text",
    "get_coefficient",
    "quantize_two",
]
