# Arcana: instructions for Claude Code

You are working in the Arcana repo on behalf of a developer (the collaborator). The project owner and sole administrator is **Mehdi**. The collaborator can push code; Mehdi controls the servers, Coolify, DNS, secrets and GitHub settings. Read this whole file before doing anything that touches git, the Dockerfile, environment variables or deployment.

## 1. How this project is deployed

```
collaborator's laptop --git push--> GitHub (Mehdi-kbz/Arcana, branch main)
                                        |
                                  webhook (automatic)
                                        v
                    Coolify (https://coolify.khabex.com, runs on Mehdi's main VPS)
                                        |
                                  SSH + docker build
                                        v
                      AWS EC2 server  -->  https://arcana.khabex.com
```

- **Pushing to `main` deploys to production automatically.** There is no staging environment and no manual approval step. A deploy takes about 1-2 minutes.
- The app is built from the `Dockerfile` in the repo root and runs as a container on the **AWS EC2 server**. The code does not run on your machine in production and does not run on Mehdi's main VPS.
- Coolify only orchestrates. It pulls the repo, builds the image on the EC2, starts the new container, waits for it to be ready, then removes the old one (rolling update). If the new container fails, the old one keeps serving.
- Live URL: https://arcana.khabex.com (HTTPS certificate is automatic).

## 2. Hard requirements for the app

Every change must keep these true, or the deploy will break or the site will show a 503:

1. **Listen on `0.0.0.0:3000`.** Not `localhost` or `127.0.0.1`, not another port. Read it from the `PORT` env var with a default of `3000`.
2. **`GET /` must return HTTP 200.** Coolify's healthcheck calls `curl http://localhost:3000/` inside the container. If `/` redirects, errors, or needs auth, the container is marked unhealthy.
3. **`curl` must stay installed in the Docker image** (the Dockerfile has an `apt-get install curl` line). Coolify's healthcheck needs it. Do not remove it. If you change the base image, make sure curl exists.
4. **The process must stay in the foreground** (`CMD` runs the server directly, no daemonizing, no `&`). If the process exits, the container exits and the site goes down.
5. **Keep `Dockerfile` at the repo root** and keep `EXPOSE 3000`.
6. **Never commit secrets** (API keys, passwords, tokens, `.pem` files, `.env`). `.gitignore` already excludes `.env*` except `.env.example`.

## 3. Git workflow

- Do not commit directly to `main` unless the collaborator explicitly says the change is ready for production. Work on a branch:
  ```
  git checkout -b short-descriptive-name
  git add <files>
  git commit -m "Clear message"
  git push -u origin short-descriptive-name
  ```
  Then open a pull request into `main`. **Merging the PR is what deploys.**
- Before pushing to or merging into `main`, make sure the app starts locally and `GET /` returns 200.
- Commit small, focused changes with clear messages. Never force-push to `main`.
- Authentication: the collaborator uses their own GitHub account (VS Code sign-in or `gh auth login`). Never ask for, store, or use anyone else's token, and never put a token in a remote URL or file in the repo.
- To undo a bad deploy: `git revert <commit>` and push. The revert redeploys the previous behavior.

## 4. Verifying a deploy

You cannot see the Coolify dashboard. After a push to `main`, wait about 2 minutes, then check from the terminal:

```
curl -s -i https://arcana.khabex.com/ | head -5
```

- `HTTP/2 200` and the expected body means the deploy worked.
- `503 Service Unavailable` means the app is not running or unhealthy (build failed, crashed, wrong port, or `/` not returning 200).
- Old content still served after several minutes means the build probably failed and the old container is still running.

If anything other than 200 persists for more than ~5 minutes after a push, do **not** keep pushing blind fixes. Check the app locally for obvious causes (section 2), and if you cannot find one, follow section 6 and tell Mehdi.

## 5. Environment variables and secrets

- Production environment variables live in Coolify (app -> Environment Variables), **not** in the repo.
- If the code needs a new variable, add its **name only** (no real value) to `.env.example`, read it from the environment in code with a sensible failure message if missing, and then tell Mehdi (section 6) which variable to add and what it is for.
- Never hardcode a value "just to test" and push it.

## 6. When you need Mehdi: say exactly this

You do not have access to the servers, Coolify, DNS, or GitHub repo settings, and you must not try to get it (no SSH, no asking for the `.pem` key or Coolify credentials). When one of the situations below comes up, stop and **tell the collaborator to message Mehdi**, using this form so the request is actionable:

> **Tell Mehdi that** <what is needed>, <why>, and <exact details>.

Situations that need Mehdi, with example wording:

| Situation | What to say |
|---|---|
| New or changed environment variable | "Tell Mehdi that Coolify needs the env var `DATABASE_URL` for the arcana app (value: ask the collaborator / not in the repo), then a redeploy." |
| Deploy failed or site returns 503 for more than ~5 min | "Tell Mehdi that the deploy of commit `<sha>` is failing (arcana.khabex.com returns 503). Please check Deployment Logs and Runtime Logs for the arcana app in Coolify and send us the last ~30 lines." |
| Need a database, Redis or persistent storage | "Tell Mehdi that arcana needs a `<Postgres/Redis/volume>`; please create it in Coolify on the AWS server and send the connection string/mount path." |
| Need a new domain or subdomain | "Tell Mehdi that we need `<name>.khabex.com` pointed to the AWS server (A record to the EC2 IP) and added as a domain to the arcana app in Coolify." |
| Need a different port, build command, base image rule, or healthcheck path | "Tell Mehdi that the Coolify setting `<setting>` for arcana must be changed to `<value>` because `<reason>`." |
| Need to roll back and `git revert` is not enough, or restart/redeploy manually | "Tell Mehdi that arcana needs a manual redeploy/restart from Coolify." |
| Out of memory during build (log shows `Killed` or exit code 137) | "Tell Mehdi that the arcana build ran out of memory on the AWS server; it needs swap added or a larger instance." |
| Need to add a collaborator, change repo settings, branch protection, or webhooks | "Tell Mehdi that `<GitHub username>` needs access / that `<setting>` must change on the Mehdi-kbz/Arcana repo." |
| Anything involving SSH keys, certificates, Coolify accounts, AWS console | "Tell Mehdi that `<request>`." Do not attempt it yourself. |

Always include: what you need, why, the exact values or names, and the commit SHA or error text when relevant. Keep it short enough to paste into a message.

## 7. Things you must not do

- Do not try to SSH into any server, install Docker/Coolify, or touch AWS, DNS or GitHub settings.
- Do not ask for, print, or commit credentials, `.pem` keys, tokens or `.env` contents.
- Do not change the listening port, remove curl from the image, or break `GET /` without telling Mehdi first.
- Do not force-push, rewrite `main` history, or delete branches you did not create.
- Do not push large binaries or build artifacts (`node_modules`, `.venv`, `__pycache__`, data dumps).

## 8. Current state of the repo

- `app.py`: placeholder server that answers "Arcana is live" on port 3000. Replace it with the real application; keep the rules in section 2.
- `Dockerfile`: `python:3.12-slim` with curl installed. If the real app uses another stack (for example Node), update the Dockerfile accordingly and keep curl, port 3000, and a foreground process.
- `README.md`: short human-facing workflow summary.
- `.env.example`: names of environment variables the app reads (no values).
