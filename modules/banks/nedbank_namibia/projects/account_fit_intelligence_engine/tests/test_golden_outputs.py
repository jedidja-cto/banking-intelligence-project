"""
Golden regression tests (exact line match) for frozen single-account outputs.
"""
import subprocess
import sys
from pathlib import Path
import pytest

# Find project root relative to this test file
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_engine_command(account_type: str) -> str:
    """Run the intelligence engine and capture stdout."""
    engine_path = PROJECT_ROOT / "code" / "src" / "engine" / "account_fit.py"
    cmd = [sys.executable, str(engine_path), "--account", account_type]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
        cwd=str(PROJECT_ROOT)
    )
    return result.stdout.replace("\r\n", "\n")

def compare_outputs(expected: str, actual: str):
    """Compare two outputs line by line and fail with a clear message on mismatch."""
    expected_lines = expected.splitlines()
    actual_lines = actual.splitlines()
    
    max_lines = max(len(expected_lines), len(actual_lines))
    
    for i in range(max_lines):
        exp = expected_lines[i] if i < len(expected_lines) else "[EOF]"
        act = actual_lines[i] if i < len(actual_lines) else "[EOF]"
        
        if exp != act:
            pytest.fail(
                f"Mismatch at line {i + 1}:\n"
                f"Expected: {exp}\n"
                f"Actual:   {act}"
            )

@pytest.mark.parametrize("account_type, golden_file", [
    ("silver_payu", "silver_payu_v021.txt"),
    ("basic_banking", "basic_banking_v031.txt"),
])
def test_golden_regression(account_type, golden_file):
    """Verify that current output exactly matches the golden snapshot."""
    golden_path = PROJECT_ROOT / "tests" / "golden" / golden_file
    
    with open(golden_path, "r", encoding="utf-8") as f:
        expected_output = f.read().replace("\r\n", "\n")
    
    actual_output = run_engine_command(account_type)
    
    compare_outputs(expected_output, actual_output)
