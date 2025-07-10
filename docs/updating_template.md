# Updating the project from the upstream template (generic workflow)

This repository (`diploma-devops`) periodically synchronises with the public template [`cct-devops-diploma-2025-template`](https://github.com/estebangarcia/cct-devops-diploma-2025-template). The instructions below work for **any future template branch** (e.g., `class‑4`, `class‑5`, …) while still ensuring that **only your commits** appear in history.

Replace **`<CLASS_BRANCH>`** with the branch you are importing each time (`class-4`, `class-5`, etc.). A single environment variable (`BRANCH`) keeps the commands copy‑paste friendly.

---

## 0  One‑time remote (already done on each workstation)

```bash
# Run once per machine
git remote add template \
  https://github.com/estebangarcia/cct-devops-diploma-2025-template.git
```

---

## 1  Fetch the template

```bash
git fetch template
```

---

## 2  Create a throw‑away branch tracking the desired template branch

```bash
# Define the template branch you want to import
BRANCH=class-4          # ← change to class‑5, class‑6, … next time

# Unique local branch name keeps multiple syncs distinct
BR=template-${BRANCH}-$(date +%Y%m%d)

git checkout -b "$BR" template/$BRANCH
```

---

## 3  Squash‑merge into **main** (keeps history clean)

```bash
git checkout main
git pull --ff-only origin main   # ensure local main is current

git merge --squash --allow-unrelated-histories "$BR"   # stage all template changes
```

### 3.1  If conflicts appear

```bash
# Accept the template version for every conflicted file
git checkout --theirs -- .

git add .               # stage resolutions
```

Now record a single commit authored by you:

```bash
git commit -m "Sync template/$BRANCH $(date +%Y-%m-%d)"
```

---

## 4  Refresh environment & test

```bash
source .venv/bin/activate           # or poetry/pipenv shell
pip install -r requirements.txt     # pulls any new dependencies
pytest -q                           # all tests should pass
```

---

## 5  Push & tag

```bash
git push origin main

git tag template-sync-$(date +%Y-%m-%d)
git push origin --tags
```

---

## 6  Clean up the throw‑away branch

```bash
git branch -d "$BR"      # delete local temp branch
```

---

### Quick reference (copy‑paste)

```bash
# 1  Fetch
git fetch template

# 2  Prepare variables
BRANCH=class-4                # adjust each release
auto_branch="template-${BRANCH}-$(date +%Y%m%d)"

git checkout -b "$auto_branch" template/$BRANCH

# 3  Squash‑merge
git checkout main
git pull --ff-only origin main
git merge --squash --allow-unrelated-histories "$auto_branch"

# Resolve conflicts wholesale
git checkout --theirs -- . && git add .

git commit -m "Sync template/$BRANCH $(date +%Y-%m-%d)"

# 4  Install deps & test
source .venv/bin/activate && pip install -r requirements.txt && pytest -q

# 5  Push & tag
git push origin main && \
  git tag template-sync-$(date +%Y-%m-%d) && git push origin --tags

# 6  Clean up
git branch -d "$auto_branch"
```

> **Tip:** If you frequently sync, consider wrapping the quick reference in a shell script (e.g., `scripts/sync_template.sh BRANCH`) so the only argument you supply is the new class branch.
