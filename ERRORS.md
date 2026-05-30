# SLH-OP Error Log & Learning

This file tracks production/development errors, their root causes, and prevention strategies to ensure continuous learning and prevent regression.

## [2026-05-30 06:10] - KeyError 'date_start' on /api/chart_data in weekly mode

- **Type**: Integration
- **Severity**: High
- **File**: `metrics.py:531`
- **Agent**: Antigravity
- **Root Cause**: The weekly metrics aggregation helper `aggregate_weekly_metrics()` did not track the minimum and maximum dates (`date_start` and `date_end`) for each week, unlike the monthly helper `aggregate_monthly_metrics()`. When the Presentation Studio switched to weekly mode and fetched `/api/chart_data/<flock_id>?mode=weekly`, the API endpoint attempted to read `a['date_start']` and `a['date_end']`, causing a `KeyError: 'date_start'` and returning a 500 Internal Server Error.
- **Error Message**: 
  ```
  sqlite3.OperationalError / 500 Internal Server Error on /api/chart_data/<flock_id>?mode=weekly
  SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON
  ```
- **Fix Applied**: Added `date_start` and `date_end` tracking to `aggregate_weekly_metrics()` in `metrics.py`. Configured it to set the initial date and dynamically check and update the min/max dates during the daily log aggregation.
- **Prevention**: Created a dedicated unit test suite in `tests/test_api_chart_data.py` to test `/api/chart_data` API in both `daily` and `weekly` modes, and integrated it into the automated pytest suite.
- **Status**: Fixed

---

## [2026-05-30 07:35] - Uncaught SyntaxError: missing ) after argument list in Broiler Flock Detail JS

- **Type**: Syntax
- **Severity**: Critical
- **File**: `app/templates/broiler/broiler_flock_detail.html:593`
- **Agent**: Antigravity
- **Root Cause**: An extra mismatched closing curly brace `}` was present in the inline script block within `broiler_flock_detail.html` right before the tab-resizing listener, causing the JS parser to fail with a `SyntaxError: missing ) after argument list` when loading the page. Additionally, arrow functions and ES6 template literals were present inside template script tags, which can trigger parsing/compatibility errors in certain mobile browsers/stages.
- **Error Message**: 
  ```
  Uncaught SyntaxError: missing ) after argument list
  ```
- **Fix Applied**: Removed the extra mismatched curly brace `}` at line 593. Rewrote all arrow functions (`=>`) and ES6 template literals to fully compatible ES5 compliant functions and string concatenations. Also cleaned up similar arrow functions in `broiler_new_flock.html`.
- **Prevention**: Enforce ES5 function patterns for inline templates and write-to-file code scripts in non-transpiled templates.
- **Status**: Fixed
