# Simple Flask + MySQL (docker-compose) and CI/CD — minimal

This repo is a minimal assignment-ready scaffold that includes:

- `docker-compose.yml` — runs a MySQL (`db`) and a Flask app (`web`) on the same network.
- `web/` — Flask app, `Dockerfile`, `requirements.txt`.
- `mysql/conf.d/my.cnf` — small MySQL config to avoid the pid-file advisory.
- `Jenkinsfile` — minimal pipeline to build, smoke-test, and push the image to Docker Hub.

Run locally

1. Build and start both services:

```powershell
docker-compose up --build
```

2. Verify:
- Open http://localhost:5000 — the Flask app will report whether it connected to MySQL.
- Confirm both containers are on the same network:

```powershell
docker-compose ps
docker network ls
docker network inspect app-network
```

CI/CD (GitHub + Jenkins) — essentials

1. Push this repo to GitHub.
2. Create a Jenkins Pipeline job that uses this repo (or use a multibranch pipeline).
3. Add Docker Hub credentials to Jenkins and set the credentials id used in the `Jenkinsfile` (`dockerhub-creds` by default).
4. Ensure the Jenkins agent can run Docker CLI (no local MySQL required on Jenkins).

Notes

- Replace `yourdockerhubusername/flask-app` in `Jenkinsfile` with your Docker Hub repo name.
- The MySQL env vars in `docker-compose.yml` are: `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE` (`appdb`), `MYSQL_USER` (`appuser`), `MYSQL_PASSWORD` (`apppassword`).
- The MySQL advisory you saw is informational; `mysql/conf.d/my.cnf` has been added to avoid it.

If you want, I can:
- Replace placeholders in `Jenkinsfile` with your Docker Hub repo and credentials id.
- Add a simple unit test and a pipeline test stage.