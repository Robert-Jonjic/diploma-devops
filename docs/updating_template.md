# Updating from the upstream template — **always via a PR**

These instructions let you pull code from the public template repository
[`cct-devops-diploma-2025-template`](https://github.com/estebangarcia/cct-devops-diploma-2025-template)
while guaranteeing that:

* **Only your commits** appear in `main` (we squash‑merge the template).
* **You never push directly to `main` from your local machine** — instead you
  open a Pull Request (PR) from a feature branch and use **Squash & Merge** in
  GitHub.

The workflow works for **any future template branch** (`class‑4`, `class‑5`, …).
Set the variable `BRANCH` each time you sync.

---

## 0  One‑time remote (per workstation)

```bash
# Run once on each computer you use
git remote add template \
  https://github.com/estebangarcia/cct-devops-diploma-2025-template.git
```

---

## 1  Fetch the template repo

```bash
git fetch template
```

---

## 2  Create two local branches

```bash
# Template branch to import this time
BRANCH=class-4               # ← change for class‑5, class‑6, …

# 2.1  Tracking branch that *exactly* mirrors the template
track_branch="template-${BRANCH}-$(date +%Y%m%d)"
git checkout -b "$track_branch" template/$BRANCH

# 2.2  PR branch based off the latest main
pr_branch="sync-${BRANCH}-$(date +%Y%m%d)"
git checkout -b "$pr_branch" main
```

---

## 3  Bring the template code in (squash‑merge)

```bash
# Stage *all* template changes but no commits from Esteban
git merge --squash --allow-unrelated-histories "$track_branch"

# Resolve any conflicts wholesale
git checkout --theirs -- . && git add .

# Record ONE commit authored by you
git commit -m "Sync template/$BRANCH $(date +%Y-%m-%d)"
```

---

## 4  Test locally

```bash
source .venv/bin/activate            # or poetry/pipenv shell
pip install -r requirements.txt       # grab new deps
pytest -q                             # all green? ✔️
```

---

## 5  Push the PR branch (never push main!)

```bash
git push -u origin "$pr_branch"
```

1. Open the GitHub UI and click **Compare & pull request**.
2. Target branch = **main**.
3. Wait for CI; review; click **Squash & Merge**.
4. Delete the PR branch in GitHub.

> *CI* (`.github/workflows/test.yml`) builds, tests, and (on `main` only)
> publishes the Docker image.

---

## 6  Tag the sync after the PR is merged

```bash
git checkout main
git pull --ff-only origin main        # get the squash commit from GitHub

git tag template-sync-$(date +%Y-%m-%d)
git push origin --tags
```

*You are still not pushing code to `main` here — only adding an annotated tag.*

---

## 7  Clean up local branches

```bash
git branch -d "$track_branch" "$pr_branch"
```

---

## Quick reference (copy‑paste)

```bash
BRANCH=class-4                     # adjust each release
track="template-${BRANCH}-$(date +%Y%m%d)"
pr="sync-${BRANCH}-$(date +%Y%m%d)"

# fetch & branch
git fetch template
git checkout -b "$track" template/$BRANCH
git checkout -b "$pr" main

git merge --squash --allow-unrelated-histories "$track"
git checkout --theirs -- . && git add .
git commit -m "Sync template/$BRANCH $(date +%Y-%m-%d)"

source .venv/bin/activate && pip install -r requirements.txt && pytest -q

git push -u origin "$pr"      # open PR → Squash & Merge

git checkout main && git pull --ff-only origin main
git tag template-sync-$(date +%Y-%m-%d) && git push origin --tags

git branch -d "$track" "$pr"
```

> **Automate**: wrap the quick reference in `scripts/sync_template.sh <class>` so
> the entire procedure becomes `./scripts/sync_template.sh class-4`. 🚀
