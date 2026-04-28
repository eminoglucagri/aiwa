# Security Scanning Pipeline — AIWA-31

**Document:** AIWA Security Scanning Pipeline v1.0
**Date:** 2026-04-28
**Author:** SecurityEngineer (AIWA-31)
**Status:** Complete
**Related:** `docs/SECURITY-REVIEW.md`, `docs/THREAT-MODEL.md`

---

## 1. Overview

This document describes the automated security scanning pipeline integrated into AIWA's CI/CD system via GitHub Actions. The pipeline provides defense-in-depth across multiple security domains and is designed to catch vulnerabilities before they reach production.

**Key principle:** Build fails on HIGH/CRITICAL findings. No exceptions for unmitigated vulnerabilities.

### 1.1 Threat Model Alignment

The scanning pipeline directly addresses the following HIGH-risk threats from `docs/THREAT-MODEL.md`:

| Threat | Countermeasure |
|---|---|
| Agent tampers with build/test results | SAST + dependency scanning; reproducible outputs |
| Generated code exposes secrets | detect-secrets pre-commit + CI scan |
| Vulnerable third-party dependencies | npm audit, pip-audit, OWASP Dependency Check |
| Secret exposure in artifacts | detect-secrets CI gate on every PR |

### 1.2 Security Review Alignment

The pipeline implements Phase 1 and Phase 2 recommendations from `docs/SECURITY-REVIEW.md`:

- A06 (Vulnerable & Outdated Components): `npm audit`, `pip-audit`, OWASP Dependency Check, Trivy
- A08 (Software & Data Integrity): SAST (Semgrep), artifact scanning via Trivy
- Secrets exposure: detect-secrets in CI

---

## 2. Scanning Tools

### 2.1 Tool Inventory

| Tool | Purpose | Scope | Failure Threshold |
|---|---|---|---|
| **npm audit** | Dependency CVE scanning (Node.js) | `frontend/package.json` | HIGH, CRITICAL |
| **pip-audit** | Dependency CVE scanning (Python) | `backend/requirements.txt` | HIGH, CRITICAL |
| **OWASP Dependency-Check** | SBOM-based CVE scanning + CVE database lookup | `frontend`, `backend` | CVSS ≥ 7 (HIGH/CRITICAL) |
| **Semgrep** | SAST — static application security testing | All source files | HIGH, CRITICAL |
| **detect-secrets** | Secrets detection in code | Entire repository | ANY finding |
| **Trivy** | Container + filesystem vulnerability scanning | Full repo scan | HIGH, CRITICAL |
| **Outdated dependency check** | Flag stale packages with newer major versions | `frontend`, `backend` | Informational only |

### 2.2 Semgrep Rulesets

Semgrep runs with the following rulesets for SAST coverage:

```
p/security-audit    # General security audit rules
p/secrets           # Hardcoded credential patterns
p/typescript        # TypeScript-specific security rules
p/python            # Python-specific security rules
p/react             # React/JSX security rules
p/flask             # Flask-specific patterns (backend API)
p/aws-exploitation  # AWS-specific exploitation patterns
p/sql-injection     # SQL injection detection
p/owasp-top10        # OWASP Top 10 coverage
```

### 2.3 detect-secrets Plugins

The baseline enables 23 secret detectors including:
AWS keys, Azure storage keys, GCP credentials, GitHub/GitLab tokens, Stripe/PayPal API keys, Slack/Discord webhooks, JWTs, private keys, npm/PyPI tokens, and generic high-entropy strings.

---

## 3. Workflow Architecture

### 3.1 PR Pipeline (`code-review.yml`)

Runs on every pull request to `main`. All security jobs are **blocking** — a PR cannot merge if any fail.

```
pull_request → security-checks (parallel with frontend-checks, backend-checks)
                         ├── Semgrep SAST (upload SARIF → GitHub Security)
                         ├── detect-secrets (fail on ANY finding)
                         ├── npm audit --audit-level=high
                         ├── pip-audit --fail-on=high --fail-on=critical
                         └── Trivy scan (CRITICAL/HIGH, SARIF output)
```

### 3.2 Deep-Scan Pipeline (`security-scan.yml`)

Runs on schedule and on-demand. Does **not** block merges — designed for visibility and alerting.

**Triggers:**
- Every Monday at 06:00 UTC (catch newly-disclosed CVEs)
- Manual dispatch via `workflow_dispatch`
- Every push to `main` (defense-in-depth)

```
scheduled / dispatch / push → [parallel jobs]
                                    ├── Dependency CVE audit (npm + pip-audit, 2x)
                                    ├── OWASP Dependency-Check (frontend + backend, 2x SARIF)
                                    ├── Semgrep SAST (extended rulesets)
                                    ├── detect-secrets (full repo scan)
                                    ├── Outdated dependencies check
                                    └── Security scan summary (GitHub Step Summary)
```

### 3.3 SARIF Integration

Results from Semgrep and Trivy are uploaded as SARIF to GitHub's Security tab:

- **Code Scanning** tab: Semgrep SAST findings
- **Security tab**: Trivy + npm audit results
- **Actions run log**: Full scan output for audit trail

---

## 4. Failure & Escalation Policy

### 4.1 Blocking Failures (PR pipeline)

| Finding | Action |
|---|---|
| **ANY secret detected** | PR blocked immediately |
| **npm audit HIGH/CRITICAL** | PR blocked |
| **pip-audit HIGH/CRITICAL** | PR blocked |
| **Semgrep HIGH/CRITICAL** | PR blocked |
| **Trivy CRITICAL/HIGH** | PR blocked |

### 4.2 Handling False Positives

When a scan flags a false positive (e.g., a test fixture, a legitimate example value):

1. **For detect-secrets:** Add the line to `.secrets.baseline` using:
   ```bash
   detect-secrets scan --baseline .secrets.baseline .
   git add .secrets.baseline
   git commit -m "chore: update secrets baseline (false positive review)"
   ```
2. **For Semgrep:** Suppress with a inline comment if the code is intentionally safe:
   ```javascript
   // nosemgrep: typescript.lang.security.audit.detected-object-accidental-assignment
   ```
3. **For npm audit / pip-audit:** If the vulnerability is in a devDependency with no exploit path, acknowledge it and track it as technical debt.

### 4.3 Vulnerability Triage SLA

| Severity | Triage Within | Fix Within |
|---|---|---|
| CRITICAL | 24 hours | 7 days |
| HIGH | 7 days | 30 days |
| MEDIUM | 30 days | 90 days |
| LOW | 90 days | Next sprint |

---

## 5. CI/CD Integration Details

### 5.1 GitHub Secrets Required

| Secret | Purpose |
|---|---|
| `VERCEL_TOKEN` | Deployment pipeline |
| `VERCEL_ORG_ID` | Deployment pipeline |
| `VERCEL_PROJECT_ID` | Deployment pipeline |
| `ANTHROPIC_API_KEY` | AI code review |
| `TEST_EMAIL` | E2E smoke tests |
| `TEST_PASSWORD` | E2E smoke tests |
| `GITHUB_TOKEN` | Auto-provided; used for posting comments |

No additional secrets are required for the security scanning pipeline — all tools (Semgrep, Trivy, pip-audit, detect-secrets, npm audit) are open source and run without API keys.

### 5.2 Runner Requirements

- OS: `ubuntu-latest` (Ubuntu 22.04 LTS)
- Node.js: 20.x (via `actions/setup-node@v4` with caching)
- Python: 3.12 (via `actions/setup-python@v5`)
- Disk: ~2 GB free for OWASP Dependency Check database downloads
- Network: Outbound HTTPS for CVE database updates

### 5.3 Concurrency

- **code-review.yml**: Cancels in-progress runs on new pushes (preserves latest)
- **security-scan.yml**: Does not cancel in-progress runs (deep scans generate artifacts)

---

## 6. Maintenance

### 6.1 Keeping the Baseline Updated

Run detect-secrets after adding any new test fixtures or example files:

```bash
pip install detect-secrets
detect-secrets scan --baseline .secrets.baseline .
git diff .secrets.baseline  # Review changes
git add .secrets.baseline
```

### 6.2 Updating OWASP Dependency-Check Database

The OWASP Dependency Check action downloads the NVD CVE database on first run (~1 GB). The database is cached by the action. To force a database update:

```yaml
# In security-scan.yml, add to the owasp-dep-check job:
skipNewer: false  # Override: re-download even if cached
```

### 6.3 Adding New Dependencies

When adding a new dependency:

1. Add to `frontend/package.json` or `backend/requirements.txt`
2. Ensure `npm ci` / `pip install` succeeds in CI
3. The next PR scan will automatically audit the new dependency
4. For high-risk dependencies (cryptographic libraries, parsers, network clients), request a manual security review before merging

---

## 7. Quick Reference

### Running scans locally

```bash
# Secrets detection
pip install detect-secrets
detect-secrets scan --baseline .secrets.baseline .
detect-secrets audit .

# Node.js vulnerability scan
cd frontend && npm audit --audit-level=high

# Python vulnerability scan
pip install pip-audit
cd backend && pip-audit --requirement=requirements.txt

# SAST
pip install semgrep
semgrep ci --config=p/security-audit,p/secrets,p/typescript,p/python,p/react,p/flask
```

### Viewing results

- **PR security findings:** GitHub PR → Checks tab → Security & Static Analysis
- **Security tab → Code Scanning:** Semgrep SARIF results
- **Actions run log:** Full verbose output for all tools

---

## 8. Future Enhancements (post-AIWA-31)

- **SBOM generation and attestation** (AIWA-40): Publish signed SBOMs for production deployments
- **DAST (dynamic scanning)**: Add OWASP ZAP or Burp Suite scanning for the deployed preview URL
- **Container image scanning**: Add Trivy image scanning when Docker images are built in CI
- **Dependency review action**: Enable GitHub's Dependency Review on every PR

---

*References: STRIDE Threat Model (AIWA-11), Security Review (AIWA-12), OWASP Top 10 2021*

