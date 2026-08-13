# Halt — 2026-08-06  (catalog: xAlisher/logos-basecamp-modules)

## ▶ Resume this session
```bash
cd /home/alisher/basecamp/logos-modules-release && claude --resume 2b7b9ceb-bd9c-408c-b980-eb4a27c74b34
```
`/home/alisher/basecamp/logos-modules-release` · session 2b7b9ceb-bd9c-408c-b980-eb4a27c74b34. Fallback: `cd /home/alisher/basecamp/logos-modules-release && claude --continue`.
(Multi-repo session — primary work was `~/basecamp/refs/logos-blockchain-ui` + this catalog + `~/logos-node-dashboard`. Prior 2026-07-10 halt archived to `docs/halt-archive/`; its open "prune 7 unpublished submodules" item is still unaddressed.)

## Where we stopped
**Everything shipped — this is a clean checkpoint, not a mid-task pause.** blockchain_ui v0.2.1
(Basecamp v0.2.3 + 0.2.1-testnet compat) released to the fork AND the catalog as a **signed
multivariant**; node-dashboard v0.1.3 cut; both READMEs updated; modules.alisher.xyz card + `index.json`
serve the proper signed 0.2.1; retro extracted 2 skills + 1 protocol. No edit in flight.

## Current state
- Branch: `main` (catalog) — pushed; fork on `compat/0.2.1-on-v0.2.1-base` (tag `v0.2.1` = `9754d23`).
- Last commit (catalog): `d96fff4` retro: broken-submodule fresh-clone workaround + no-CI *_ui republish.
- Build status: **verified** — fork CI green (3 arches); signed `.lgx` installs WITHOUT
  `--allow-unsigned`; linux-amd64 variant watched sync to **Online** on the 0.2.1 testnet.
- Releases: fork `v0.2.1` (signed multivariant) · catalog `blockchain_ui-v0.2.1` (signed, in index.json) ·
  node-dashboard `v0.1.3`.
- Open review: none.
- Note: local `submodules/keycard-basecamp` shows ` m` (pre-existing dirty content, NOT ours — leave it).

## Next steps (in order) — all OPTIONAL follow-ups
1. **Fix the broken local catalog submodule**: `git submodule deinit -f submodules/logos-blockchain-ui
   && git submodule update --init submodules/logos-blockchain-ui` (its `.git` is a tangled catalog clone;
   see PROJECT_KNOWLEDGE + fieldcraft `git-submodule-remote-safety`).
2. **Verify darwin-arm64 / linux-arm64 variants render** — built + signed but not runtime-tested (need a
   Mac / arm64 device). 🧫 wetware.
3. **Upstream the #29 fix** — consider a PR of the sandbox→backend-QRO liveness fix to
   `logos-blockchain/logos-blockchain-ui` (currently only on our fork).
4. **Optional**: flip catalog `_release-module.yml` to `signing_mode: inline` so catalog CI signs
   (today `none` → manual §7b-SIGN); and/or add signing to the fork's `release.yml` (it re-emits
   unsigned per-arch on any future tag push).

## Blockers
- none.

## Context that's hard to re-derive
- **Rebuild the signed multivariant** (scratch copy is gone): `nix build .#lgx-portable` per-arch →
  `lgx merge` (nix-store `lgx` 0.1.0) → sign with `~/.config/logos-signing/lgx_signer` +
  `keys/xAlisher.jwk` (off-stick fast path; DID is in `logos-repo.json` trustedSigners).
  LD_LIBRARY_PATH needs AppImage `usr/lib` (from `--appimage-extract`) + nix `libsodium.so.26`.
- **#29 fix** = v0.2.3 ui_qml sandbox blocks QML `XMLHttpRequest`; route node liveness via backend QRO
  `getCryptarchiaInfo()` (`result.success` = up/down). Skill: `ui-qml-sandbox-route-local-api-via-backend`.
- **Two-chains gotcha** (0.2.1 testnet): new chain genesis `1785920400000` (2026-08-05 09:00 UTC, live);
  retired pre-fork genesis `1782808200000` is halted-but-still-peer-served + longer → a fresh node doing
  peer discovery can adopt the dead chain (logos-blockchain#3265, closed). Our nodes are on the new chain.
- The hardfork-watch "STILL OLD" alert was a **false transient** during the node-down-for-reinstall
  window (watcher conflates "node down" with "old chain"); auto-corrected next tick.
- Fork's `release.yml` had an artifact name/pattern bug (fixed in `9754d23`): release job downloaded
  `logos-module-*` but build uploaded `logos-blokchain-ui-*`; now both `logos-blockchain-ui-*`.
