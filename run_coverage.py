import os
import sys
import subprocess


def run_coverage():
    print("=" * 60)
    print("         LOOM ENGINE AUTOMATED CODE COVERAGE RUNNER         ")
    print("=" * 60)

    try:
        import coverage
        has_coverage = True
    except ImportError:
        has_coverage = False
        print("[Notice]: 'coverage' package not found in Python environment.")
        print("          Running standard unittest discovery instead...\n")

    env = os.environ.copy()
    env["TESTING"] = "true"

    if has_coverage:
        cmd = [
            sys.executable, "-m", "coverage", "run", "-m", "unittest", "discover",
            "-s", "tests/unit", "-p", "test_*.py"
        ]
        subprocess.run(cmd, env=env)
        print("\n" + "=" * 60)
        print("                  CODE COVERAGE SUMMARY REPORT              ")
        print("=" * 60)
        report_cmd = [
            sys.executable, "-m", "coverage", "report",
            "--omit=tests/*,benchmarks/*,scratch/*"
        ]
        subprocess.run(report_cmd)
    else:
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests/unit", "-p", "test_*.py"]
        subprocess.run(cmd, env=env)


if __name__ == "__main__":
    run_coverage()
