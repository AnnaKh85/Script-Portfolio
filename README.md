# Backend Data Validation - Python QA Portfolio

A curated, standalone adaptation of selected checks from a larger test project.
The examples focus on calculation validation, XML-to-JSON mapping, cross-source
consistency, and asynchronous API workflows.

**All included data is synthetic.** The suite runs without company services,
database credentials, work documents, or browser installation.

## What to review

| Example | What it demonstrates | Execution boundary |
| --- | --- | --- |
| [Resource calculations](tests/test_resource_calculations.py) | Decimal arithmetic, coefficient products, rounding, alternative calculation paths, validation-status consistency | Selected original assertion helpers with synthetic inputs |
| [XML mapping](tests/test_xml_summary.py) | XML namespaces, decimal commas, unit conversion, component totals, zero and missing values | Adapted mapping checks using authored XML and JSON fixtures |
| [Package consistency](tests/test_package_consistency.py) | Matching IDs, names, types, statuses, component amounts and totals across representations | Selected original tests against a synthetic database snapshot; no database connection |
| [Fault detection](tests/test_package_fault_detection.py) | Deliberately corrupted metadata and totals are rejected by the selected checks | Negative tests of the validation checks |
| [API workflow](tests/test_api_workflow.py) | Playwright APIRequestContext, status polling, deadline, terminal errors, pagination and teardown | Real HTTP to an in-process loopback demo server; no real backend |

Expected amounts are authored independently of the validation functions. Negative
cases change an amount, status, or field and verify that an assertion fails.

## Structure

```text
portfolio/        Selected validation helpers and adapted API/XML helpers
tests/            Curated checks and negative scenarios
tests/data/       Small, independently authored synthetic fixtures
```

