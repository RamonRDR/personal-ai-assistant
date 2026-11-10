"""Keep static README test badges aligned with a real pytest JUnit XML report.

Usage: python scripts/check_readme_badges.py pytest-results.xml
No GitHub write access, secrets, external service, or additional package needed.
"""

import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
READMES = ("README.md", "README.pt-BR.md", "README.es.md")
SHIELDS = re.compile(r"https://img[.]shields[.]io/badge/[^)\s]+")
PYTEST = re.compile(r"/badge/pytest-(\d+)%20passing-")
EVAL = re.compile(r"/badge/Synthetic%20Evals-(\d+)%2F(\d+)%20passing-")


def verify(junit_path: Path) -> None:
    """Assert the badge snapshot reflects the passing JUnit cases on this run."""
    cases = ElementTree.parse(junit_path).findall(".//testcase")
    if not cases:
        raise ValueError("JUnit report contains no test cases")
    passed = sum(
        not any(case.find(tag) is not None for tag in ("skipped", "failure", "error"))
        for case in cases
    )
    scenarios = json.loads((ROOT / "evals/scenarios.json").read_text(encoding="utf-8"))
    base = None

    for path in READMES:
        text = (ROOT / path).read_text(encoding="utf-8")
        badges = SHIELDS.findall(text)
        if len(badges) < 15:
            raise ValueError(f"{path}: expected the full technical badge inventory")
        if base is not None and badges != base:
            raise ValueError(f"{path}: shields differ from README.md")
        base = badges
        if not text.startswith('<div align="center">'):
            raise ValueError(f"{path}: missing centered header")
        if any(label not in text for label in READMES if label != path):
            raise ValueError(f"{path}: missing language navigation")
        matches = PYTEST.findall(text)
        if matches != [str(passed)]:
            raise ValueError(f"{path}: pytest badge {matches} != {passed} passing cases")
        match = EVAL.findall(text)
        count = str(len(scenarios))
        if match != [(count, count)]:
            raise ValueError(f"{path}: synthetic evaluation badge does not match cases")

    print(
        f"README badge check OK: {passed}/{len(cases)} pytest cases passed; "
        f"{len(scenarios)} synthetic scenarios declared; "
        f"{len(base)} Shields badges consistent across {len(READMES)} READMEs."
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/check_readme_badges.py pytest-results.xml")
    try:
        verify(Path(sys.argv[1]))
    except (OSError, ValueError, ElementTree.ParseError) as error:
        raise SystemExit(str(error)) from error
