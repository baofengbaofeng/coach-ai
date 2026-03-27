# CoachAI Test Report

**Generated:** 2026-03-27T15:19:19.484574
**Duration:** 8.49 seconds
**Overall Status:** FAILED

## Summary

- **Total Test Suites:** 6
- **Passed:** 3
- **Failed:** 3

## Test Suite Results

### ✅ Ddd Domain
- **Status:** PASSED

### ✅ Ddd Application
- **Status:** PASSED

### ✅ Ddd Api
- **Status:** PASSED

### ❌ Legacy Unit
- **Status:** FAILED
- **Error:** ImportError while loading conftest '/home/baofengbaofeng/.openclaw/workspace/coach-ai/tests/conftest.py'.
tests/conftest.py:14: in <module>
    from sqlalchemy import create_engine
../../../.local/lib...

### ❌ Legacy Integration
- **Status:** FAILED
- **Error:** ImportError while loading conftest '/home/baofengbaofeng/.openclaw/workspace/coach-ai/tests/conftest.py'.
tests/conftest.py:14: in <module>
    from sqlalchemy import create_engine
../../../.local/lib...

### ❌ Legacy Api
- **Status:** FAILED
- **Error:** ImportError while loading conftest '/home/baofengbaofeng/.openclaw/workspace/coach-ai/tests/conftest.py'.
tests/conftest.py:14: in <module>
    from sqlalchemy import create_engine
../../../.local/lib...

## Next Steps

❌ Some tests failed. Please review the failed test suites and fix the issues.

Recommended actions:
1. Review the error messages in the detailed test output
2. Check the test configuration and environment setup
3. Run individual test suites to isolate the issues
4. Fix the failing tests and run the full test suite again
