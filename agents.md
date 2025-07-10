Below is an updated `AGENTS.md` file tailored for our NAT SS project, reflecting the latest Apache Superset build and installation changes.

```markdown
# AGENTS.md

## Purpose
This file provides guidance to AI agents (e.g., OpenAI Codex) on navigating, building, testing, and contributing to our NAT SS project (National Analytical Tool).

## Project Overview
- **Name:** NAT SS (National Analytical Tool)
- **Description:** A customized fork of Apache Superset, branded as **NAT SS** and extended with organization-specific plugins and configurations.
- **Repository:** https://github.com/ariful19/nat_ss.git

## Project Structure
- `/superset/` – Flask-based Python backend and CLI entrypoint.
- `/superset-frontend/` – React + TypeScript UI assets.
- `/docker/` – `docker-compose.yml`, `docker-compose-non-dev.yml`, and `docker-compose-image-tag.yml` for various modes.
- `/tests/` – Unit tests (`tests/unit_tests/`) and integration tests (`tests/integration/`).

## Development Setup

### 1. Fork & Clone
```bash
# Fork on GitHub, then:
git clone git@github.com:ariful19/nat_ss.git
cd nat_ss
```

### 2. Docker Compose (Recommended)
Superset now recommends `docker compose` for an all-in-one development environment.

#### Option 1 – Interactive Development
```bash
docker compose up --build
```
- Mounts local code; rebuilds Python and JS layers if needed.
- Runs Superset backend, Celery worker, Node asset builder, Postgres, and Redis.
- UI served at `http://localhost:9000` by default.
- Disable in-container frontend builds by setting:
  ```bash
  export BUILD_SUPERSET_FRONTEND_IN_DOCKER=false
  ```
  Then in another shell:
  ```bash
  cd superset-frontend && npm ci && npm run dev-server
  ```

#### Option 2 – Immutable Images
```bash
docker compose -f docker-compose-non-dev.yml up
```
- Builds a static image from the local branch; code changes require rebuild.

#### Option 3 – Official Release
```bash
export TAG=latest-dev
docker compose -f docker-compose-image-tag.yml up
```
- Pulls a `-dev` suffix image (e.g. `5.0.0-dev`) from Docker Hub.

### 3. Local Python Environment (Optional)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/development.txt
pip install -e .
```
- Installs development requirements and editable Superset.

### 4. Frontend Dependencies
```bash
cd superset-frontend
# Node.js v20, npm v10 recommended via nvm
npm ci
cd ..
```

### 5. Superset Initialization
After initial install or database reset, run:
```bash
superset db upgrade        # Apply DB migrations
superset init              # Create roles, load defaults
superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@example.com \
  --password admin        # Create an admin user
```  
(Optional) Load example datasets:
```bash
superset load-examples
```

## Common Commands
- **Initialize DB:** `superset db upgrade`
- **Create Admin:** see `superset fab create-admin` above
- **Load Examples:** `superset load-examples`
- **Run Backend (Dev):**
  ```bash
  superset run -p 8088 --with-threads --reload --debugger
  ```
- **Build Frontend (Prod):**
  ```bash
  cd superset-frontend && npm run build
  ```
- **Dev Frontend Server:** `npm run dev-server`

## Coding Conventions
- **Python:** Black formatting (`black .`), PEP 8 standards.
- **TypeScript/JS:** ESLint & Prettier (`npm run lint`, `npm run format`).
- **Commits:** Conventional prefixes (`feat:`, `fix:`), include `NAT SS:` in PR titles.

## Testing Protocols
- **Unit Tests:** `pytest tests/unit_tests/`
- **Integration Tests:** `scripts/tests/run.sh`
- **Coverage:** ≥ 80% on new modules.

## Contribution Workflow
1. `git checkout -b feat/your-feature`
2. Implement, lint, and test.
3. Push branch and open PR against `main`.
4. Address CI feedback and squash/fix commits as needed.

## Environment Variables
- `SUPERSET_CONFIG_PATH` – Custom `superset_config.py`.
- `DATABASE_URL` – SQLAlchemy URI for metadata database.
- `BUILD_SUPERSET_FRONTEND_IN_DOCKER` – Disable in-container frontend builds.
- `SUPERSET_LOAD_EXAMPLES` – (`yes`/`no`) control example data loading.

## Known Gotchas
- Node 20 + npm 10 required; use nvm to manage versions.
- In low-memory environments, build frontend locally instead of in Docker.
- Windows: use WSL2 for `docker compose` compatibility.

## Contact
For support, join `#nat-ss` on Slack or file an issue on GitHub.
```
