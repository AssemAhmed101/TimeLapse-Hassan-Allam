import subprocess
import sys


def main():
    commands = [
        [sys.executable, "-m", "pytest", "-q"],
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-m",
            "integration or e2e",
            "tests/test_phase17_integration_e2e.py",
        ],
    ]

    for command in commands:
        print("$", " ".join(command))
        result = subprocess.run(command)
        if result.returncode != 0:
            raise SystemExit(result.returncode)

    print("Phase 17 test suite passed.")


if __name__ == "__main__":
    main()
