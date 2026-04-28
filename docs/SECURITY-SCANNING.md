# Security Scanning — CI/CD Integration

**Document:** AIWA Security Scanning v1.0
**Date:** 2026-04-28
**Author:** SecurityEngineer (AIWA-31)
**Status:** Implemented
**Context:** AIWA-12 (Security Review) and AIWA-11 (Threat Model) findings implemented as automated CI/CD gates.

---

## 1. Overview

This document describes the automated security scanning integrated into the CI/CD pipeline, derived from the findings in [SECURITY-REVIEW.md](./SECURITY-REVIEW.md) and [THREAT-MODEL.md](./THREAT-MODEL.md). The goal is to fail builds on HIGH/CRITICAL security findings before code reaches production.

## 2. Scanning Tools

### 2.1 Dependency CVE Scanning

| Tool | Scope | Failure Threshold | Workflow |
|---|---|---|---|
| `npm audit` | Node.js (frontend) | HIGH/CRITICAL | code-review.yml → security-checks |
| Ruff | Python (backend) | HIGH/CRITICAL | code-review.yml → backend-checks |
| Semgrep (p/security-audit) | Multi-language SAST | HIGH/CRITICAL | code-review.yml → security-checks |

- **npm audit**: Run with `--audit-level=high` — fails on any HIGH or CRITICAL vulnerability in frontend dependencies.
- **Ruff**: Python linter catches deprecated imports and known insecure patterns.
- **Semgrep**: `p/security-audit` ruleset covers OWASP Top 10 patterns across TypeScript and Python.

### 2.2 Secrets Detection

| Tool | Scope | Failure Threshold | Workflow |
|---|---|---|---|
| `detect-secrets` | All source files | ANY | code-review.yml → security-checks |

- Prevents hardcoded API keys, tokens, passwords, and credentials from entering the codebase.
- Scans on every PR; any baseline secret triggers a failure.
- Baseline file: `.secrets.baseline` — known test/example secrets can be allowlisted.
- Run via: `detect-secrets scan --fail-on-any`

### 2.3 SAST Scanning

| Tool | Config | Scope | Workflow |
|---|---|---|---|
| Semgrep | `p/security-audit`, `p/secrets`, `p/typescript`, `p/python` | All source | code-review.yml → security-checks |

- Multi-language static analysis for common vulnerability patterns.
- Uses GitHub App inline scanning (returntocorp/semgrep-action) — results appear directly in the PR.
- Custom rules can be added in `.semgrep.rules/` directory.

## 3. CI/CD Integration

### 3.1 Pull Request Gate (code-review.yml)

The PR pipeline runs all security checks on every pull request. All security checks run in parallel under the `security-checks` job:

1. **Semgrep** — SAST + secrets patterns
2. **detect-secrets** — secrets scanning
3. **npm audit** — Node.js dependency CVEs

If any check fails, the PR is blocked from merging.

### 3.2 Production Deployment Gate (vercel-deploy.yml)

Production promotion gates include:

1. **npm audit** — dependency CVE scan on frontend dependencies
2. **Semgrep** — SAST scan (optional, add to `promote` job if needed)

These run as part of the preview stage and block production promotion if HIGH/CRITICAL issues are found.

## 4. Failure Actions

| Finding Level | CI Behavior | Notification |
|---|---|---|
| CRITICAL | Build fails; PR blocked | Semgrep/PR comment + email |
| HIGH | Build fails; PR blocked | Semgrep/PR comment |
| MEDIUM | Warning only; PR allowed | Semgrep/PR comment |
| LOW | Informational | No action |

## 5. Tooling Installation

### detect-secrets

```bash
pip install detect-secrets
detect-secrets scan --init  # Initialize baseline
detect-secrets scan --fail-on-any  # CI mode
```

### Semgrep

```bash
npm install -g semgrep
semgrep --config p/security-audit --config p/secrets .
```

### OWASP Dependency Check (planned)

For Java/Python dependency CVE scanning with a full CVE database:

```bash
# Add to backend-checks job when backend dependencies grow
docker run --rm -v $(pwd):/src owasp/dependency-check:latest \
  --project . --scan /src --failOnCVSS 7
```

## 6. Scanning Priority Targets

Based on the [SECURITY-REVIEW.md](./SECURITY-REVIEW.md), the following areas are highest priority for scanning:

1. **Node.js dependencies** — `frontend/package.json` → `npm audit --audit-level=high`
2. **Python dependencies** — `backend/requirements.txt` → `pip-audit` or `safety check`
3. **Secrets in source** — all files → `detect-secrets scan`
4. **SQL injection patterns** — Python/SQL files → Semgrep `p/security-audit`
5. **SSRF patterns** — URL-fetching code → Semgrep custom rules
6. **Hardcoded credentials** — all files → Semgrep `p/secrets`
7. **TypeScript XSS** — React components → Semgrep `p/typescript`

## 7. Monitoring & Alerting

Security scan results should be tracked over time:

- **GitHub Security Advisories** — enabled for the repository
- **Dependabot** — automated PRs for dependency updates
- **Semgrep Dashboard** — centralized view of findings across all branches
- **npm audit CI** — weekly automated audit via Dependabot or GitHub Actions schedule

## 8. Secrets Baseline Management

The `.secrets.baseline` file tracks known-allowed secrets (test credentials, example values). To add a new secret to the baseline:

```bash
# After reviewing and approving a false positive:
detect-secrets scan --update .secrets.baseline <file-containing-false-positive>
```

**Important:** Never add real production secrets to the baseline. The baseline is committed to the repository and should not contain actual credentials.

## 9. Known Limitations

- **Semgrep inline scan** requires GitHub App installation — currently uses `returntocorp/semgrep-action` which works without the app but may have rate limits.
- **OWASP Dependency Check** is not yet integrated — the Java/Python CVE scanning is pending until dependencies are formally declared.
- **DAST (dynamic scanning)** is not yet configured — should be added before production launch.
- **Container image scanning** (Trivy/Syft) should be added when Docker images are built in CI.

---

*Reviewed by: SecurityEngineer (AIWA-31)*
