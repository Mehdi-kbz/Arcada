# Arcana

## Deployment (read this first)

- Pushing to `main` deploys to production automatically: GitHub webhook -> Coolify -> build on the AWS server -> https://arcana.khabex.com. There is no staging environment.
- Prefer working on a branch and merging to `main` via pull request, so only finished work reaches production.
- A deploy takes 1-2 minutes. After pushing, check https://arcana.khabex.com. Build and runtime logs are in Coolify (https://coolify.khabex.com); ask the project owner for access if you need them.
- The container is built from `Dockerfile`. The app must listen on `0.0.0.0:3000`. Coolify's healthcheck calls `curl` against `/` on port 3000, so keep `curl` installed in the image and keep `/` returning HTTP 200.

## Secrets and config

- Never commit secrets or `.env` files. Production environment variables are set in Coolify (app -> Environment Variables), not in the repo. Ask the project owner to add or change them.
- Document every variable the app reads in `.env.example` (names only, no real values).

## Layout

- `app.py`: placeholder web server (replace with the real app).
- `Dockerfile`: production image.
