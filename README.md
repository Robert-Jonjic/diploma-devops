# 📚 Books Catalog API

A lightweight, **Django + Django REST Framework** micro‑service that lets you create, search and manage a catalogue of books (with proper ISBN‑10/13 validation).
It ships as a Docker container, runs locally via *docker‑compose*, and can be promoted to Kubernetes with a custom Helm chart—fully automated by GitHub Actions, semantic‑versioned Docker images, and Argo CD GitOps.

---

## ✨ Features

* CRUD REST endpoints for `Book` resources, exposed under `/api/…`
* Health probe at `/api/` returning `{"status": "ok"}` (used for K8s readiness)
* Unique ISBN validation via **isbnlib**
* PostgreSQL backing store (local & prod)
* Pytest test‑suite with coverage for list/CRUD/health
* CI pipeline ⇢ semantic versioning ⇢ OCI image on GHCR ⇢ automatic production rollout with Argo CD

---

## 🏃‍♂️ Quick start (local development)

### 1. Clone & enter repo

```bash
$ git clone https://github.com/Robert-Jonjic/diploma-devops.git
$ cd diploma-devops
```

### 2. Option A – pure Python

```bash
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt
$ export DJANGO_SECRET_KEY="$(python - <<'PY' -c 'import secrets, string; print("".join(secrets.choice(string.ascii_letters+string.digits) for _ in range(50)))' PY)"
$ export DATABASE_URL="postgres://books:books@localhost:5432/books"
$ python manage.py migrate
$ python manage.py runserver 0.0.0.0:8000
```

### 3. Option B – Docker Compose (recommended)

```bash
$ docker compose up --build
```

> Runs **app** (port 8000) & **Postgres 17.5**; waits for DB, auto‑migrates, then serves.

### 4. Smoke tests

```bash
$ curl http://localhost:8000/api/               # → {"status":"ok"}
$ curl http://localhost:8000/api/books/         # → []
```

---

## 🔌 Environment variables

| Variable            | Default (compose) | Description                       |
| ------------------- | ----------------- | --------------------------------- |
| `DATABASE_NAME`     | `books`           | Postgres DB name                  |
| `DATABASE_USER`     | `books`           | Postgres user                     |
| `DATABASE_PASSWORD` | `books`           | Postgres password                 |
| `DATABASE_HOST`     | `db` (compose)    | DB host / service DNS             |
| `DEVELOPMENT_MODE`  | `false`           | Enables debug tweaks when `true`  |
| `DJANGO_SECRET_KEY` | –                 | **Required** for non‑compose runs |

---

## 🎯 API usage examples

<details>
<summary>List books</summary>

```bash
$ curl -s http://localhost:8000/api/books/ | jq
[]
```

</details>

<details>
<summary>Create a book</summary>

```bash
$ curl -s -X POST http://localhost:8000/api/books/ \
     -H 'Content-Type: application/json' \
     -d '{
           "title": "The Pragmatic Programmer",
           "author": "Andrew Hunt, David Thomas",
           "isbn": "9780135957059",
           "published_date": "1999-10-20",
           "description": "Classic software craftsmanship book."
         }' | jq
{
  "id": 1,
  "title": "The Pragmatic Programmer",
  "author": "Andrew Hunt, David Thomas",
  "isbn": "9780135957059",
  "published_date": "1999-10-20",
  "description": "Classic software craftsmanship book.",
  "created_at": "2025-08-01T12:00:00Z",
  "updated_at": "2025-08-01T12:00:00Z"
}
```

</details>

<details>
<summary>Update (PATCH) title</summary>

```bash
$ curl -X PATCH http://localhost:8000/api/books/1/ \
       -H 'Content-Type: application/json' \
       -d '{"title": "The Pragmatic Programmer (20th Anniversary)"}'
```

</details>

<details>
<summary>Delete</summary>

```bash
$ curl -X DELETE http://localhost:8000/api/books/1/ -v
# … HTTP/1.1 204 No Content
```

</details>

> A full OpenAPI schema can be generated via **drf‑spectacular**—run `python manage.py spectacular --file schema.yml` and import it into Swagger UI/Postman.

---

## 🤖 CI / CD pipeline (GitHub Actions)

```txt
Push/PR → test → migrations → makemigrations‑check
            \
             ➜ semantic‑release (⇢ CHANGELOG + tag vX.Y.Z)
                  \
                   ➜ build‑docker‑image   (ghcr.io/robert‑jonjic/devops-diploma-2025:vX.Y.Z)
                        \
                         ➜ deploy‑application (bump image.tag in envs/production/values.yaml)
                              ⇢ Argo CD auto‑syncs & rolls out
```

* **Tests** – `pytest` must pass.
* **Database checks** – applies migrations & asserts no pending ones.
* **Semantic‑release** – inspects *Conventional Commit* messages to bump *semver* and update `CHANGELOG.md`.
* **Docker build/push** – multi‑arch image pushed to **GHCR**, tagged with the release version.
* **GitOps deploy** – action edits the production `values.yaml`; Argo CD detects the change and performs a zero‑downtime `helm upgrade`.

---

## ☸️ Kubernetes & Helm

### 1. Spin up a local cluster (k3d)

```bash
$ k3d cluster create mycluster \
    --port "8081:80@loadbalancer" \
    --port "8443:443@loadbalancer" \
    --port "30000-30010:30000-30010@server:0"
$ kubectl get nodes
```

### 2. Provision Postgres

```bash
$ cat <<'YAML' > pg-values.yaml
auth:
  database: books
  username: books
  password: books
YAML
$ helm install books-database oci://registry-1.docker.io/bitnamicharts/postgresql -f pg-values.yaml
```

> Secret `books-database-postgresql` is created; our app chart consumes it.

### 3. Allow cluster to pull private images

```bash
$ kubectl create secret docker-registry ghcr-token \
    --docker-username=<YOUR_GH_USERNAME> \
    --docker-password=<PAT_WITH_READ_PACKAGES> \
    --docker-server=ghcr.io
```

### 4. Deploy the application via Helm

```bash
# First time
$ helm install books ./books-catalog-chart \
      --set image.tag=<version> \
      --set image.repository=ghcr.io/robert-jonjic/devops-diploma-2025 \
      --set replicaCount=2

# Upgrades (handled automatically by ArgoCD once GitOps is enabled)
$ helm upgrade books ./books-catalog-chart -f envs/production/values.yaml
```

`kubectl get deployments,pods,svc` should now show the API and Postgres running; the `/api/` health probe will mark pods *Ready*.

### 5. (Optional) Install Argo CD for GitOps

```bash
$ helm repo add argo https://argoproj.github.io/argo-helm && helm repo update
$ kubectl create namespace argocd
$ helm -n argocd install argocd argo/argo-cd -f infra/argocd-values.yaml
```

Then: expose at `http://localhost:8081/argocd`, log in with secret `argocd-initial-admin-secret`, connect this repo, set **Automatic Sync**, path `books-catalog-chart/`, and point to `envs/production/values.yaml`.

Argo now handles every release created by GitHub Actions.

---

## 🧪 Running the test‑suite

```bash
$ pytest                 # inside venv
# or
$ docker compose run --rm app pytest
```

---

## 📄 License

MIT © Robert Jonjić 2025
