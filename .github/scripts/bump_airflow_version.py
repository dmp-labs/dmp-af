"""Apply an Airflow version bump to the test matrix and (on minor bumps) the pyproject cap.

Invoked by .github/workflows/check-airflow-release.yml after the integration test
against the discovered latest version passes. Intentionally minimal: appends to
AIRFLOW_3_VERSIONS and (only on a minor bump) rewrites the apache-airflow upper
bound in pyproject.toml and the docs install snippet.

Does not touch README.md's compat-matrix table — that's a manual reviewer step
flagged in the auto-PR body, since regex-rewriting a markdown table is brittle.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from packaging.version import Version

REPO = Path(__file__).resolve().parents[2]


def bump(latest_str: str, kind: str) -> None:
    latest = Version(latest_str)

    integration_tests = REPO / '.ci' / 'src' / 'dmp_af_ci' / 'integration_tests.py'
    text = integration_tests.read_text()
    new_text, n = re.subn(
        r"(AIRFLOW_3_VERSIONS = \[\n(?:    Version\('[^']+'\),\n)+)",
        rf"\1    Version('{latest_str}'),\n",
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit(f'Could not find AIRFLOW_3_VERSIONS list in {integration_tests}')
    integration_tests.write_text(new_text)

    if kind != 'minor':
        return

    new_cap = f'<{latest.major}.{latest.minor + 1}.0'

    pyproject = REPO / 'pyproject.toml'
    text = pyproject.read_text()
    new_text, n = re.subn(
        r'"apache-airflow\[fab,cncf-kubernetes\] >=2\.6,<\d+\.\d+\.\d+"',
        f'"apache-airflow[fab,cncf-kubernetes] >=2.6,{new_cap}"',
        text,
    )
    if n != 1:
        raise SystemExit(f'Could not find apache-airflow constraint in {pyproject}')
    pyproject.write_text(new_text)

    install_doc = REPO / 'docs' / 'getting-started' / 'installation.md'
    if install_doc.exists():
        text = install_doc.read_text()
        new_text, _ = re.subn(
            r'"apache-airflow >=2\.6,<\d+\.\d+\.\d+"',
            f'"apache-airflow >=2.6,{new_cap}"',
            text,
        )
        install_doc.write_text(new_text)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: bump_airflow_version.py <version> <patch|minor>')
    bump(sys.argv[1], sys.argv[2])
