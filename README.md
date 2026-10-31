# Arcana

Live at https://arcana.khabex.com

## Workflow

1. Clone the repo: `git clone https://github.com/Mehdi-kbz/Arcana`
2. Make changes and run the app locally (`python app.py`, listens on port 3000).
3. Commit and push directly to `main` (the only branch; no other branches, no pull requests): `git pull --rebase origin main && git push origin main`
4. The push triggers an automatic production deploy via Coolify (about 1-2 minutes).

See `CLAUDE.md` for deployment details and rules.
