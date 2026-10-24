from decimal import Decimal
from xml.etree import ElementTree as ET
from portfolio.numbers import quantize_two

COST_PATHS = {
    "building": "Building/Total",
    "mounting": "Mounting/Total",
    "equipment": "Equipment/Total",
    "otherPrice": "Other",
}

def validate_summary(xml_text: str, summary: dict) -> None:
    root = ET.fromstring(xml_text)
    namespace = root.tag.partition("}")[0] + "}" if root.tag.startswith("{") else ""

    def number(path):
        text = root.findtext("/".join(namespace + part for part in path.split("/")))
        assert text is not None, f"Missing XML field: {path}"
        return Decimal(text.strip().replace(",", "."))

    for currency in ("base", "current"):
        total = Decimal("0")
        for key, xml_path in COST_PATHS.items():
            path = f"Object/Estimate/EstimatePrice/{xml_path}/Price{currency.capitalize()}"
            expected = quantize_two(number(path) / Decimal("1000"))
            actual = summary[key][currency]["value"]
            assert actual is not None, f"Missing JSON field: {key}.{currency}"
            assert Decimal(str(actual)) == expected, f"{key}.{currency}: {actual} != {expected}"
            total += expected
        actual_total = summary["totalPrice"][currency]["value"]
        assert actual_total is not None, f"Missing JSON totalPrice.{currency}"
        assert Decimal(str(actual_total)) == total, f"totalPrice.{currency}: {actual_total} != {total}"

    expected_labor = number("Object/Estimate/EstimatePrice/Summary/LaborCosts")
    actual_labor = summary["summaryLaborCost"]["value"]
    assert actual_labor is not None, "Missing JSON labor cost"
    assert Decimal(str(actual_labor)) == expected_labor, "Labor cost mismatch"
