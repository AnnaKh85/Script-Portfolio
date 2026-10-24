import pytest
from tests.test_package_consistency import TestPackageConsistency as PackageChecks

@pytest.mark.parametrize("field, replacement, method", [
    ("type", "OBJECT", "test_estimate_type_matches_db"),
    ("name", "Wrong synthetic name", "test_estimate_name_matches_db"),
])
def test_metadata_mismatch_is_detected(estimates_list, estimate_db_contexts, field, replacement, method):
    estimates_list[0][field] = replacement
    with pytest.raises(AssertionError):
        getattr(PackageChecks(), method)(estimates_list, estimate_db_contexts)

def test_missing_expected_context_fails(estimates_list, estimate_db_contexts):
    estimate_db_contexts.clear()
    with pytest.raises(AssertionError):
        PackageChecks().test_estimate_type_matches_db(estimates_list, estimate_db_contexts)

def test_excluded_status_fails(estimates_list, estimate_db_contexts):
    estimate_db_contexts["demo-local-01"]["status"] = "XML_PARSING_ERROR"
    with pytest.raises(AssertionError, match="XML_PARSING_ERROR"):
        PackageChecks().test_excluded_statuses_not_in_structure(estimates_list, estimate_db_contexts)

def test_total_mismatch_is_detected(estimates_list, estimate_db_contexts):
    estimates_list[0]["data"]["summary"]["totalPrice"]["base"]["value"] = "999"
    with pytest.raises(AssertionError, match="totalPrice"):
        PackageChecks().test_local_summary_total_price(estimates_list, estimate_db_contexts)
