# Halt — 2026-07-10  (catalog: xAlisher/logos-basecamp-modules)

## ▶ Resume this session
```bash
cd ~/basecamp/logos-modules-release && claude --resume 1e8dfb1b-c6d0-4a34-94ee-d7d6726332e9
```
Fallback: `claude --continue`. (Issues are DISABLED on this repo — tracked in `xAlisher/alisher-sherali` #20/#21.)

## Where we stopped
Stood up the branded catalog at **https://modules.alisher.xyz** (live, HTTPS enforced) and built a
Basecamp-style **landing page** there. Published `archive` + `archive_ui` @0.2.0 (signed) to the catalog.

## Current state
- `main` @ `69f870c` · plus an **orphan `gh-pages` branch** that ACTUALLY serves the site (see below).
- **Pages source = `gh-pages` branch / root** (legacy build). Serves `logos-repo.json` + `CNAME` (`modules.alisher.xyz`) + `.nojekyll` + `index.html`. HTTPS cert `approved`, enforced.
- Index (`index.json`): packages `archive`, `archive_ui`, `receiver_ui`, `radio_ui`, `radio_module` — all signed.
- PR #2 merged (CNAME + `logos-repo.json`; also fixed `indexUrl` which pointed at the wrong repo name `logos-modules-release` → `logos-basecamp-modules`).
- Landing-page **generator persisted to `site/`** (`gen_modules_page.py`, `page_template.html`, `index.html`) — was in the ephemeral session scratchpad.

## Next steps (in order)
1. **Prune 7 unpublished submodules** (user hasn't confirmed): `stash`, `beacon`, `keeper`, `cord`, `keycard`, `logos-zone-sequencer`, `radio` (redundant — radio ships from booth). Keep `ia`, `receiver`, `booth`. `git submodule deinit` + `git rm`, on a branch. Ask first — some may be staged to publish.
2. **Landing page**: user should verify the 3-bucket split (tested-on-0.2.x vs not) + Universal/Legacy tags + categories — all curated guesses. Edit `site/gen_modules_page.py` data model → regenerate → deploy to `gh-pages`.
3. Optional v2: serve `index.json` from the domain too (fully branded).

## Blockers
- Submodule prune needs the user's OK on which to keep.

## Context that's hard to re-derive
- **Pages MUST serve from the orphan `gh-pages` branch, NOT `main`.** `main` has 10 submodules → a root Pages build uploads the whole checked-out tree → errors forever. gh-pages has ONLY the served files.
- **To edit the landing page:** edit `site/gen_modules_page.py` (curated module data + buckets) or `site/page_template.html` (CSS/layout) → `python3 site/gen_modules_page.py` → copy `site/index.html` onto the `gh-pages` branch → push → `gh api -X POST repos/xAlisher/logos-basecamp-modules/pages/builds`. (QR needs the `/tmp/qrvenv` qrcode venv; regenerate the QR SVG to `/tmp/qr.svg` first.)
- **Cert stuck at `null`?** toggle the custom domain: `gh api -X PUT .../pages -f cname=""` then `-f cname=modules.alisher.xyz`. A "cert not valid" browser error right after = client cache/HSTS (verify with `curl -w %{ssl_verify_result}` + incognito).
- **Publishing to the catalog** (per module): CI `Release <submodule>` ships only the core (multi-variant, incl. darwin) — sign it (§7-SIGN, BC 0.2.1+ rejects unsigned) + rebuild index. The `*_ui` is published **manually** (single-variant signed) — see basecamp-skills `catalog-publish-module-and-ui`.
- **DNS:** `CNAME modules → xalisher.github.io` (Namecheap).
- Excluded from the page by request: Shop, Back Office (not ready), Zone Sequencer (fork of vpavlin — already a collaborator there).
