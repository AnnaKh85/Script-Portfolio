import pytest
from portfolio.xml_mapping import validate_summary

@pytest.mark.parametrize("namespace", [False, True], ids=["plain", "namespaced"])
def test_xml_to_json_mapping_and_totals(xml_text, summary, namespace):
    if namespace:
        xml_text = xml_text.replace("<Document>", '<Document xmlns="urn:portfolio:estimate">')
    validate_summary(xml_text, summary)

@pytest.mark.parametrize("field", ["building", "totalPrice", "summaryLaborCost"])
def test_mapping_detects_incorrect_response(xml_text, summary, field):
    if field == "summaryLaborCost":
        summary[field]["value"] = "999"
        message = "Labor cost"
    else:
        summary[field]["base"]["value"] = "999"
        message = field
    with pytest.raises(AssertionError, match=message):
        validate_summary(xml_text, summary)

def test_missing_xml_field_is_not_treated_as_zero(xml_text, summary):
    xml_text = xml_text.replace("<PriceBase>12345</PriceBase>", "")
    with pytest.raises(AssertionError, match="Missing XML field"):
        validate_summary(xml_text, summary)

def test_zero_amount_is_valid(xml_text, summary):
    xml_text = xml_text.replace("<PriceBase>12345</PriceBase>", "<PriceBase>0</PriceBase>")
    summary["building"]["base"]["value"] = "0"
    summary["totalPrice"]["base"]["value"] = "5.00"
    validate_summary(xml_text, summary)
