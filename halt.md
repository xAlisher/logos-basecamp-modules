# Halt — 2026-06-10

## Where we stopped

Catalog epic complete and retro done. All 6 modules are live at
`https://github.com/xAlisher/logos-basecamp-modules` with `index.json` generated.
Session ended after retro — extracted 3 skills, wrote `docs/PROJECT_KNOWLEDGE.md`,
pushed both `basecamp-skills` and `logos-modules-release`. No work in flight.

## Current state

- Branch: `main`
- Last commit: `cc5acc5 docs: add PROJECT_KNOWLEDGE — catalog setup pitfalls and module inventory`
- Build status: all 6 module releases passing (zone-sequencer v0.1.0, stash v0.1.0, logos_cord v1.0.0, logos_beacon v1.0.0, keycard v1.0.0, keeper v0.1.0)
- Open review: none
- Dirty: `submodules/keycard-basecamp` shows `m` (submodule at committed pointer, no staged change — safe to ignore)

## Next steps (in order)

1. **Update all 6 module READMEs** — replace the lgpm manual-install wall with the one-liner:
   ```bash
   lgpd repo add https://raw.githubusercontent.com/xAlisher/logos-basecamp-modules/main/logos-repo.json
   lgpd install keeper
   ```
   Repos: keeper-basecamp, beacon-basecamp, cord-basecamp, stash-basecamp, keycard-basecamp, logos-zone-sequencer-module

2. **Verify explorer indexing lag** — dispatch the fresh-agent prompt (already drafted) to check if testnet explorer is genuinely lagging behind canonical chain. Draft at `~/infra/upstream-issues/explorer-indexing-lag.md` if it exists.

3. **Confirm `office-of-film` ×2 inscriptions** — two inscriptions were in `finalizing` state at session end. Launch Basecamp, open keeper, confirm they reached `confirmed` (blockHeaderId fallback fix was deployed). Re-inscribe `in-camera-jpeg` from keeper UI if it never went through.

4. **File upstream explorer lag issue** — after verification, open a GitHub issue on the testnet explorer repo with the lag evidence.

## Blockers

- `office-of-film` ×2 confirmation requires running Basecamp and waiting for blockchain sync — needs Alisher at the machine.
- Explorer lag verification: sneg node was on a forked chain at last check — need to confirm whether that's still true before filing upstream.

## Context that's hard to re-derive

- `metadata.json dependencies` silently drives SDK codegen — listing non-platform modules (`logos_cord`, `logos_beacon`) causes `logo_cord_api.h: No such file or directory` at build time. Reverted all such deps to `[]`. Runtime deps live in `manifest.json` instead (handled by lgpd). Documented in `docs/PROJECT_KNOWLEDGE.md` and skill `metadata-json-deps-sdk-codegen`.

- `stash` has hand-written `src/generated/storage_module_api.cpp` — removing `storage_module` from its `metadata.json` was intentional (would produce duplicate `StorageModule::*` symbols). Do not re-add it.

- `keycard` submodule must use `xAlisher/keycard-qt` fork (commit `7f53e19`), not `status-im/keycard-qt`. The SW=6D00 fix commit `2e3669e7` was Alisher's local-only commit, never pushed to status-im.

- `zone-sequencer` is Linux x86_64 only. The release workflow passes `variants: linux-amd64` explicitly. arm64 and darwin builds are expected to fail — the overall CI run may show "failure" but the GitHub Release is still created.

- `logos-package` pin is `a2eec3694558d49fcc4abcbacb0b23c24380ade9` — the commit that introduced content hashes in `lgx add`. Do not downgrade this pin.

- Install one-liner for testing:
  ```bash
  lgpd repo add https://raw.githubusercontent.com/xAlisher/logos-basecamp-modules/main/logos-repo.json && lgpd install keeper
  ```
