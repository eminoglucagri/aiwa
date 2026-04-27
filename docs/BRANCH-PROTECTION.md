# Branch Protection & PR Requirements — AIWA-9

**Issue:** AIWA-9
**Status:** Ready to execute — all prerequisites and plan documented, awaiting credentials from board/CEO

**Date:** 2026-04-28
**Updated:** 2026-04-28 (second heartbeat — still awaiting credentials)

## Objective

Configure GitHub branch protection on `main` to require PR reviews and disable direct pushes. Verify the PR workflow works with a test branch.

## Prerequisites

- GitHub PAT with `repo` scope
- Target repository name and owner/org
- Repository initialized (AIWA-8)

## Execution Plan

Once the above prerequisites are met, execute the following via GitHub REST API (or `gh` CLI):

### Step 1 — Enable branch protection on `main`

```bash
# Requires: GH_TOKEN env var or --header "Authorization: Bearer $GH_TOKEN"
curl -X PUT \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/{owner}/{repo}/branches/main/protection \
  -d '{
    "required_status_checks": null,
    "enforce_admins": true,
    "required_pull_request_reviews": null,
    "restrictions": null,
    "required_linear_history": false,
    "allow_force_pushes": false,
    "allow_deletions": false
  }'
```

Key settings:
- `allow_force_pushes: false` — blocks force-pushes to `main`
- `allow_deletions: false` — prevents branch deletion
- `enforce_admins: true` — protection applies even to admins

### Step 2 — Require PR reviews

```bash
curl -X PUT \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/{owner}/{repo}/branches/main/protection/required_pull_request_reviews \
  -d '{
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1,
    "bypass_pull_request_allowances": null
  }'
```

Key settings:
- `required_approving_review_count: 1` — at least 1 approval required
- `dismiss_stale_reviews: true` — stale approval dismissed when new commits pushed

### Step 3 — Verify with test branch

```bash
# Create test branch
git checkout -b test/protection-verification

# Add a trivial file
echo "# Verification test" > verification.txt
git add verification.txt
git commit -m "test: verification commit for branch protection"

# Try to push directly to main (should fail)
git push origin main || echo "Direct push blocked — branch protection active"

# Push test branch and create PR
git push origin test/protection-verification
gh pr create --title "test: branch protection verification" --body "Verifying PR workflow"
```

### Step 4 — Merge and cleanup

After PR approval and merge, delete the test branch:
```bash
gh pr merge --admin --delete-branch
git checkout main
git pull
```

## Current Status

- [x] Local git repo initialized with all project docs (2 commits)
- [ ] GitHub repo `AIWebGelitirmeOtomasyonPlatformu/AIWebDevelopmentAutomationPlatform` does not exist — **AIWA-8 must be completed first**
- [ ] Branch protection not yet configured (waiting on repo + PAT)
- [ ] PR workflow not yet verified

## Verification Checklist

- [ ] GitHub repo created (AIWA-8 done)
- [ ] Local git pushed to GitHub remote
- [ ] Branch protection enabled on `main`
- [ ] Force-push blocked
- [ ] 1+ PR review required
- [ ] Stale reviews dismissed on new commits
- [ ] Direct push to `main` rejected
- [ ] PR merge workflow confirmed working
- [ ] Test branch cleaned up

## Blocker

Cannot execute until GitHub credentials are provided AND the repository is initialized (AIWA-8).

**Confirmed:** Repository `AIWebGelitirmeOtomasyonPlatformu/AIWebDevelopmentAutomationPlatform` does not exist yet (GitHub API returned 404). AIWA-8 (Initialize GitHub repository) must be completed first.

**Required from board/CEO:**
1. GitHub Personal Access Token (PAT) with `repo` scope
2. Confirmation that AIWA-8 is done and the repo is created
3. (If repo name differs) the actual repository name

## Notes

- If using GitHub organization, ensure branch protection is not blocked by branch protection rules at the organization level
- If repository already has branch protection configured, Step 1 may return 422 — verify existing rules match requirements