# Updating the project from the upstream template

This repository (`diploma-devops`) periodically synchronises with the public template repository [`cct-devops-diploma-2025-template`](https://github.com/estebangarcia/cct-devops-diploma-2025-template) on the **class-2** branch.  Follow the steps below each time you want to bring the latest template changes into your own code‑base.

---

## 0  One‑time set‑up (already done)

```bash
# Add the template repo as a secondary remote
git remote add template \
  https://github.com/estebangarcia/cct-devops-diploma-2025-template.git
```

---

## 1  Fetch the latest template history

```bash
git fetch template
```

---

## 2  Create a throw‑away update branch

```bash
# Name includes the date so multiple syncs stay unique
BR=template-class-2-$(date +%Y%m%d)

git checkout -b "$BR" template/class-2
```

---

## 3  Merge the template into **main**

### 3.1 If this is the **first** merge (no common ancestor)

```bash
git checkout main
git pull --ff-only origin main

git merge --allow-unrelated-histories --no-ff "$BR" \
  -m "Merge template/class-2 $(date +%Y-%m-%d)"
```

### 3.2 For **subsequent** merges

```bash
git checkout main
git pull --ff-only origin main

git merge --no-ff "$BR" \
  -m "Sync template/class-2 $(date +%Y-%m-%d)"
```

---

## 4  Resolve conflicts by **taking the template version wholesale**

```bash
# Accept the incoming (template) side for every conflicted file
git checkout --theirs -- .

git add .               # stages the conflict resolutions
git commit --no-edit    # completes the merge commit
```

> **GUI alternative** – launch `code .`, open the **Source Control** view, and click **Accept Incoming** for each file under *MERGE CHANGES*.

---

## 5  Refresh your environment & run tests

```bash
# Activate your virtual‑env first
source .venv/bin/activate           # or `poetry shell`, `pipenv shell`, …

pip install -r requirements.txt      # install new/updated packages

pytest -q                            # all tests should pass
```

---

## 6  Push and tag the sync point

```bash
git push origin main

git tag template-sync-$(date +%Y-%m-%d)

git push origin --tags
```

---

## 7  Clean up the temporary branch

```bash
git branch -d "$BR"   # safe to delete locally – can recreate any time
```

---

### Notes

* **Compiled artefacts** (`*.pyc`, `__pycache__/`) are ignored via `.gitignore`. If any slip through, run:

  ```bash
  git ls-files -z -- '*.py[cod]' | xargs -0 git rm --cached --
  git commit -m "Remove Python byte‑code files"
  ```
* Continuous Integration is configured in `.github/workflows/test.yml` and will run automatically on every push, ensuring the template update hasn’t broken your build.

Happy syncing! \:rocket:
