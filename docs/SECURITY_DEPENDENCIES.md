# Dependency security (Dependabot / pip-audit)

## Pinned for known CVEs

These are pinned in `requirements.txt` or fixed in the Docker build:

| Package     | Minimum version | Notes |
|------------|-----------------|--------|
| urllib3    | 2.6.3           | GHSA-gm62, GHSA-2xpw, GHSA-38jv (transitive) |
| filelock   | 3.20.3          | GHSA-w853, GHSA-qmgc (transitive) |
| pypdf      | 6.7.4           | CVE-2026-28351 (RunLengthDecode DoS) |
| lxml_html_clean | 0.4.0       | PYSEC-2024-160 / CVE-2024-52595 (XSS) |
| pip        | 26.0            | CVE-2025-8869, CVE-2026-1703; upgraded in `docker/run/fs/ins/install_A0.sh` after `uv pip install` |

## Not yet fixed upstream

- **diskcache** (CVE-2025-69872): Arbitrary code execution via pickle in cache; affects ≤5.6.3. No fix released yet. Transitive dependency; monitor for 5.6.4+.
- **langchain-core** (CVE-2026-26013): Fix is in 1.2.x; current stack uses 0.3.x. Upgrading would be a major version change; consider when upgrading the LangChain stack.

## Checking locally

```bash
uv pip install -r requirements.txt -r requirements2.txt
uv run pip-audit
```

In Docker, the image build runs `install_A0.sh`, which installs from `requirements.txt` (with pins) and then upgrades pip.
