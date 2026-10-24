import copy
import json
from pathlib import Path
import pytest

DATA = Path(__file__).parent / "data"

@pytest.fixture
def package_data():
    return json.loads((DATA / "package.json").read_text(encoding="utf-8"))

@pytest.fixture
def package_id(package_data):
    return package_data["packageId"]

@pytest.fixture
def interdoc_structure(package_data):
    return package_data["structure"]

@pytest.fixture
def estimates_list(interdoc_structure):
    estimates = interdoc_structure["estimates"]
    assert estimates, "Synthetic fixture must exercise at least one estimate"
    assert any(e["type"] == "LOCAL" for e in estimates), "LOCAL coverage is required"
    return estimates

@pytest.fixture
def estimate_db_contexts(package_data, estimates_list):
    contexts = package_data["databaseSnapshot"]
    assert all(e["estimateId"] in contexts for e in estimates_list), "Missing expected context"
    return contexts

@pytest.fixture
def summary():
    return json.loads((DATA / "summary.json").read_text(encoding="utf-8"))

@pytest.fixture
def xml_text():
    return (DATA / "estimate.xml").read_text(encoding="utf-8")

@pytest.fixture
def resource():
    return copy.deepcopy({
        "pricePerUnitBase": {"value": "12.345"},
        "consumptionTotal": {"value": "2"},
        "winterRise": {"value": "1.1"},
        "coefficients": [{"values": [{"value": "1.2"}, {"value": "0.5"}]}],
        "recountCoefficientsSum": "2",
        "totalBase": {"value": "16.30", "validationResult": "SUCCESS"},
        "totalCurrent": {"value": "32.59", "validationResult": "SUCCESS"},
    })
