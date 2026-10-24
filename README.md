# Backend Data Validation — Python QA Portfolio

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

## Run locally

Requires Python 3.10 or later. From the project directory:

```sh
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```sh
# macOS / Linux
source .venv/bin/activate
```

Then install dependencies and run:

```sh
python -m pip install -r requirements.txt
python -m pytest -q
```

The API examples use Playwright's request client, so `playwright install` is not
needed. The demo HTTP server binds to `127.0.0.1` on an OS-assigned port and is
closed after each test. Run only non-HTTP checks with:

```sh
python -m pytest -q -m "not api"
```

## Structure

```text
portfolio/        Selected validation helpers and adapted API/XML helpers
tests/            Curated checks and negative scenarios
tests/data/       Small, independently authored synthetic fixtures
docs/             Selection rationale and sanitization scope
```

## Adaptation and scope

The original project included live API calls, PostgreSQL queries, browser tests,
bulk files, and operational reports. This export intentionally selects a narrow
set of checks and replaces external inputs with synthetic fixtures.

- The numeric utility module and selected resource and package checks retain
  their source logic. Some original diagnostic messages remain in Russian.
- XML summary mapping was refactored to use Decimal and explicit failures for
  missing required fields. The example covers four cost categories and labor;
  it does not preserve every mapping from the larger suite.
- API polling/pagination was adapted to a small fictional contract. The local
  service and negative scenarios were added for this portfolio version.
- Original resource helpers retain their permissive default conversion and
  early-return behavior for absent totals. The selected calculation fixtures
  supply the required totals; this export does not claim strict schema validation.
- Passing this suite demonstrates the selected checks against the supplied
  examples. It does not verify production behavior, PostgreSQL integration,
  browser UI behavior, or the complete original business rules.

See [selection rationale](docs/SELECTION.md) and
[sanitization scope](docs/SANITIZATION.md).
