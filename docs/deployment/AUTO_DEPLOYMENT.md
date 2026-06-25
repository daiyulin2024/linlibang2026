# Long-Term Automatic Deployment

This project is the cleaned Phase 7 React/Vite version of Linlibang. It is prepared to deploy from the repository root to Cloudflare Pages.

## Recommended Deployment Path

Use Cloudflare Pages Git integration as the long-term deployment path.

- Production URL: `https://linlibang2026.pages.dev/`
- Admin URL: `https://linlibang2026.pages.dev/admin`
- Cloudflare Pages project: `linlibang2026`
- GitHub repository from the handoff: `https://github.com/daiyulin2024/linlibang2026`
- Production branch: `main`
- Root directory: leave blank or use `/`
- Framework preset: `Vite`
- Build command: `npm run build`
- Build output directory: `dist`

Cloudflare Pages should have these environment variables configured in the dashboard:

```env
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
VITE_ADMIN_PASSWORD=...
```

Do not commit `.env.local` or real Supabase credentials.

## Why Git Integration

Cloudflare Pages can deploy by Git integration or by Direct Upload. For long-term work, Git integration is preferred because every push to the configured branch can trigger a new build and deployment, while pull requests and branches can get preview deployments. Wrangler Direct Upload remains useful only as a manual fallback.

## Manual Fallback Deployment

If Git integration is unavailable, build and deploy manually:

```powershell
npm install
npm run build
npx wrangler pages deploy dist --project-name linlibang2026 --commit-dirty=true
```

## Local Validation Before Push

Run this before pushing code changes:

```powershell
npm install
npm run build
```

The repository also includes `.github/workflows/build-check.yml`, which runs `npm ci` and `npm run build` on pushes to `main` and on pull requests.

## Database Files

Current Supabase schema and retained incremental SQL files are kept under `docs/database/`. If a future code change needs a database field or seed-data change, add a new incremental SQL file there instead of editing production data directly from the frontend code.

## Files That Should Stay Out of Git

These are intentionally ignored:

- `node_modules/`
- `dist/`
- `.env.local`
- `.env.*.local`

## Current Migration Note

The old project placed the Vite app under:

```text
phases/phase_7_react_web
```

This cleaned `ddl` project places the Vite app at the repository root, so Cloudflare Pages root directory should be blank or `/`, not the old phase path.
