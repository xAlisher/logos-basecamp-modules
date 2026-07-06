# booth (radio_ui + radio_module) — manual catalog publishing

Booth is a **two-modules-in-one-repo** submodule (`radio_ui` + `radio_module` under
`submodules/booth-basecamp/`). The stock `logos-modules-release-action` build workflow
**cannot** publish it: its checkout step runs `git submodule update --init -- "$MODULE_PATH"`,
which requires `MODULE_PATH` to be a registered submodule — but booth's modules live in
**subdirs** of the submodule (`submodules/booth-basecamp/radio_ui`), not submodule roots.
`pathspec … did not match` → fail. (Also `radio_ui/flake.nix` uses `path:../radio_module`,
so the two must stay in one submodule.)

## How booth is published to this catalog (manual)

The rebuild-index workflow does a **full rescan of every release's `.lgx`** — it does not care
how a release was created. So publish booth by attaching the pre-built `.lgx` directly:

```bash
# build+sign locally in booth-basecamp (per module), then:
gh release create radio_module-v<ver> --repo xAlisher/logos-basecamp-modules --target main \
  --title "radio_module v<ver>" radio_module-<ver>-linux-amd64.lgx
gh release create radio_ui-v<ver>     --repo xAlisher/logos-basecamp-modules --target main \
  --title "radio_ui v<ver>"     radio_ui-<ver>-linux-amd64.lgx
gh workflow run "Rebuild index" --repo xAlisher/logos-basecamp-modules
# bump submodules/booth-basecamp pointer + commit so the catalog records the source commit
```

Booth catalog builds are **linux-amd64 only** (mediamtx/tor; darwin can't build on Linux).

## Proper fix (tracked)

See the automation-gap issue: either **fork the release action** to add a `build_subdir`
input (separate from the submodule `module_path`), or **split booth** into two single-module
repos. Until then, booth is published by the manual steps above.
