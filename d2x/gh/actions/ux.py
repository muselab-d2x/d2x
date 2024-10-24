import os


def summary(text: str) -> None:
    """Write to GitHub Actions job summary"""
    if summary_path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary_path, "a") as f:
            f.write(f"{text}\n")


def output(name: str, value: str) -> None:
    """Set GitHub Actions output variable"""
    if env_file := os.environ.get("GITHUB_OUTPUT"):
        with open(env_file, "a") as f:
            f.write(f"{name}={value}\n")
