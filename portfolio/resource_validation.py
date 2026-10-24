from decimal import Decimal
from typing import Dict, Optional, Tuple
from portfolio.numbers import decimal_from, get_coefficient, quantize_two
def _decimal(value: Optional[object], default: str = "0") -> Decimal:
    return decimal_from(value, default)


def _coeff_product(block: Optional[Dict]) -> Decimal:
    return get_coefficient((block or {}).get("coefficients"))


def _get_nested(source: Optional[Dict], *keys: str, default: str = "0") -> Decimal:
    data: Optional[object] = source or {}
    for key in keys:
        if not isinstance(data, dict):
            return _decimal(None, default)
        data = data.get(key)
    return _decimal(data, default)


def _get_total(block: Optional[Dict], key: str) -> Tuple[Decimal, Optional[str]]:
    total = (block or {}).get(key) or {}
    return _decimal(total.get("value"), "0"), total.get("validationResult")


def _get_recount_sum(block: Optional[Dict]) -> Decimal:
    return _decimal((block or {}).get("recountCoefficientsSum"), "1")


def _assert_validation(matches: bool, validation: Optional[str], context: str) -> None:
    if not matches:
        print(f"Validation result for {context}: {validation}\n")
    if matches:
        assert validation == "SUCCESS", f"Ожидался SUCCESS для {context}, получено {validation}"
    else:
        assert (
            validation == "INCORRECT_CALCULATION"
        ), f"Ожидался INCORRECT_CALCULATION для {context}, получено {validation}"


def _calc_base_simple(tsn: Dict, *, context: str) -> None:
    if tsn.get("totalBase").get("value") is None:
        print(f"-----\n")
        print(f"Проверка {context} totalBase: Не найдено\n")
        return

    actual, validation = _get_total(tsn, "totalBase")
    price_per_unit = _get_nested(tsn, "pricePerUnitBase")
    consumption_total = _get_nested(tsn, "consumptionTotal")
    winter_rise = _get_nested(tsn, "winterRise", default="1")
    coefficients = _coeff_product(tsn)

    expected = quantize_two(price_per_unit * consumption_total * winter_rise * coefficients)
    matches = expected == quantize_two(actual)
    print(f"-----\n")
    print(
        f"Проверка {context} totalBase: {validation}\n"
        f"  Формула: price_per_unit * consumption_total * winter_rise * coefficients\n"
        f"  Расчет: {price_per_unit} * {consumption_total} * {winter_rise} * {coefficients} = {expected}\n"
        f"  Факт: {actual}. Результат: {'SUCCESS' if matches else 'FAIL'}\n"
    )
    _assert_validation(matches, validation, f"{context} totalBase")


def _calc_current_simple(tsn: Dict, *, context: str) -> None:
    if tsn.get("totalCurrent").get("value") is None:
        print(f"-----\n")
        print(f"Проверка {context} totalCurrent: Не найдено\n")
        return

    actual, validation = _get_total(tsn, "totalCurrent")
    price_per_unit = _get_nested(tsn, "pricePerUnitBase")
    consumption_total = _get_nested(tsn, "consumptionTotal")
    winter_rise = _get_nested(tsn, "winterRise", default="1")
    coefficients = _coeff_product(tsn)
    recount_sum = _get_recount_sum(tsn)

    expected = quantize_two(price_per_unit * consumption_total * winter_rise * coefficients * recount_sum)
    print(f"-----\n")
    print(
        f"Проверка {context} totalCurrent: {validation}\n"
        f"  Длинная формула: price_per_unit * consumption_total * winter_rise * coefficients * recount_sum\n"
        f"  Расчет: {price_per_unit} * {consumption_total} * {winter_rise} * {coefficients} * {recount_sum} = {expected}"
    )
    if expected == quantize_two(actual):
        print(f"  Факт: {actual}. Результат: SUCCESS\n")
        _assert_validation(True, validation, f"{context} totalCurrent")
        return

    total_base = _get_nested(tsn, "totalBase")
    expected_short = quantize_two(total_base * recount_sum)
    matches = expected_short == quantize_two(actual)
    print(
        f"  Краткая формула: total_base * recount_sum\n"
        f"  Расчет: {total_base} * {recount_sum} = {expected_short}\n"
        f"  Факт: {actual}. Результат: {'SUCCESS' if matches else 'FAIL'}\n"
    )
    _assert_validation(matches, validation, f"{context} totalCurrent")
