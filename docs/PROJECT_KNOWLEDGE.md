# Project Knowledge — logos-modules-release (xAlisher/logos-basecamp-modules)

Package catalog for all 6 Logos Basecamp modules, published at
`https://github.com/xAlisher/logos-basecamp-modules`.

## Architecture

Two-file catalog format:
- `logos-repo.json` — identity card (name, indexUrl)
- `index.json` — auto-generated aggregate (uploaded as GitHub Release asset by `rebuild-index.yml`)

Users install via:
```bash
lgpd repo add https://raw.githubusercontent.com/xAlisher/logos-basecamp-modules/main/logos-repo.json
lgpd install keeper
```

## Module Inventory

| Module | Version | Variants | Notes |
|--------|---------|---------|-------|
| liblogos_zone_sequencer_module | v0.1.0 | linux-amd64 only | Rust + circuits; x86_64-only |
| stash | v0.1.0 | all | — |
| logos_cord | v1.0.0 | all | — |
| logos_beacon | v1.0.0 | all | — |
| keycard | v1.0.0 | all | xAlisher/keycard-qt fork for SW=6D00 fix |
| keeper | v0.1.0 | all | — |

## Critical Pitfalls

### metadata.json `dependencies` drives SDK codegen — do NOT list non-platform modules

`metadata.json` dependencies are consumed by `mkLogosModule` to generate `logos_sdk.h`,
which includes `#include "<module>_api.h"` for each dep. Platform modules ship their
headers in the SDK; custom modules do not. Listing `logos_cord` or `logos_beacon` here
causes `logos_cord_api.h: No such file or directory` at build time.

**Rule:** Only list platform-provided modules (e.g. `delivery_module`, `storage_module`)
in `metadata.json dependencies`. For typed IPC to your own modules, use `flake.nix`
inputs instead.

**Exception:** `stash` had `storage_module` in deps AND a hand-written
`src/generated/storage_module_api.cpp`. Auto-codegen created a duplicate → linker
conflict. Removed `storage_module` from `metadata.json` since stash has manual
StorageModule bindings.

### zone-sequencer requires custom flake.nix (not mkLogosModule)

Zone-sequencer is not built with `mkLogosModule` — it's a custom Rust FFI build.
Its release workflow passes `variants: linux-amd64` explicitly to the release action
(arm64/darwin will never build).

The `flake.nix` must:
1. Export `lgx-portable = lgx;` alias (release action requires `lgx-portable` attribute)
2. Build BOTH `linux-amd64` and `linux-amd64-dev` variants in the LGX
3. Pin `logos-package` at `a2eec369` or later (content hashes required by `lgx verify`)
4. Copy LGX as a file: `cp zone-sequencer.lgx $out` NOT `mkdir $out && cp ... $out/zone-sequencer.lgx`
5. Run `lgx verify` AFTER `patchManifest` (not before)

### patchManifest must filter without renaming

The `patchManifest` Python script must filter `manifest["main"]` to `built_variants`
without stripping the `-dev` suffix. If keys in the manifest don't match actual
variant directory names, `lgx verify` fails with "Missing content hashes in manifest".

```python
built_variants = {'linux-amd64', 'linux-amd64-dev'}
manifest["main"] = {k: v for k, v in manifest["main"].items() if k in built_variants}
```

### logos-package pin must support content hashes

Pin `logos-package` at commit `a2eec369` or later. Earlier pins produce LGX files
without content hashes; newer `lgx verify` (used in CI) requires them.

Update pin:
```bash
# In flake.nix: logos-package.url = "github:logos-co/logos-package/a2eec3694558d49fcc4abcbacb0b23c24380ade9"
nix flake lock --update-input logos-package
```

### keycard-qt submodule requires xAlisher fork

`status-im/keycard-qt` commit `2e3669e7` (Alisher's SW=6D00 fix) was a local commit
never pushed publicly. The submodule must point to `xAlisher/keycard-qt` which has the
fix at commit `7f53e19` as a publicly accessible commit.

## Runtime Dependencies

Modules declare `dependencies` in `manifest.json` for runtime resolution by `lgpd`.
These are NOT the same as `metadata.json dependencies`:

| Module | Declared deps |
|--------|--------------|
| keeper | logos_cord, logos_beacon, stash, logos_keycard |
| beacon | stash, logos_keycard, liblogos_zone_sequencer_module |
| cord | liblogos_zone_sequencer_module |
| zone-sequencer | (none) |
| keycard, stash | (none) |

Note: `metadata.json` deps cannot list non-platform modules (see above). Runtime deps
in `manifest.json` are correct and handled by lgpd at install time.

## Release Workflow

```bash
# Release all modules
gh workflow run "Release all modules" --repo xAlisher/logos-basecamp-modules

# Release single module
gh workflow run "Release keeper-basecamp" --repo xAlisher/logos-basecamp-modules
```

Each release action builds the LGX, publishes a GitHub Release, then `rebuild-index.yml`
regenerates `index.json` and uploads it as the `index` release asset.
