"""Test runner script for the Smart Agriculture API."""
import sys
import subprocess
import argparse


def run_tests(test_path="tests", verbose=True, coverage=False):
    """Run pytest with specified options."""
    cmd = ["python", "-m", "pytest", test_path]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    cmd.append("--tb=short")
    
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd)
    return result.returncode


def run_specific_test(test_file):
    """Run a specific test file."""
    return run_tests(test_file)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Smart Agriculture API tests")
    parser.add_argument(
        "--test",
        choices=["all", "weather", "market", "disease", "schemes", "integration"],
        default="all",
        help="Which tests to run"
    )
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    test_map = {
        "all": "tests",
        "weather": "tests/test_weather.py",
        "market": "tests/test_market.py",
        "disease": "tests/test_disease.py",
        "schemes": "tests/test_schemes.py",
        "integration": "tests/test_integration.py"
    }
    
    test_path = test_map[args.test]
    return_code = run_tests(test_path, args.verbose, args.coverage)
    
    sys.exit(return_code)


if __name__ == "__main__":
    main()
