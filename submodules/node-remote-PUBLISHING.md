# node-remote (node_remote + node_remote_ui) — manual catalog publishing

Node Remote is a **two-modules-in-one-repo** submodule, the same shape as booth. Its modules
live in **subdirs** of the submodule:

```
submodules/node-remote/node-remote-bc/node_remote      # core C++ module
submodules/node-remote/node-remote-bc/node_remote_ui   # QML pane
submodules/node-remote/node-remote-android             # the Android app (not a catalog module)
```

The stock `logos-modules-release-action` build workflow **cannot** publish it, for exactly the
reason booth cannot: its checkout step runs `git submodule update --init -- "$MODULE_PATH"`,
which requires `MODULE_PATH` to be a **registered submodule**. A subdir of one fails with
`pathspec … did not match`. See `booth-basecamp-PUBLISHING.md` — same gap, same workaround.

The two modules also ship as a matched pair: they share a pairing protocol and a wire format
with the Android app, all three carry the SAME version, and they have broken in the field when
they skewed. Publish them together or not at all.

## How node-remote is published to this catalog (manual)

`rebuild-index` does a **full rescan of every release's `.lgx`**, reading each manifest — it
does not care how a release was created. So attach the pre-built, signed `.lgx` directly:

```bash
# In ~/basecamp/modules/node-remote, build both halves:
#   cd node-remote-bc/node_remote    && nix build .#packages.x86_64-linux.lgx-portable
#   cd node-remote-bc/node_remote_ui && nix build .#packages.x86_64-linux.lgx-portable
# Copy each to its release filename, chmod u+w, and SIGN it (see the lgx_signing memory) —
# signing mutates the .lgx in place, so it must come after the build and before upload.

gh release create node_remote-v<ver> --repo xAlisher/logos-basecamp-modules --target main \
  --title "node_remote v<ver>" node_remote-<ver>.lgx
gh release create node_remote_ui-v<ver> --repo xAlisher/logos-basecamp-modules --target main \
  --title "node_remote_ui v<ver>" node_remote_ui-<ver>.lgx
gh workflow run "Rebuild index" --repo xAlisher/logos-basecamp-modules

# Then bump the submodule pointer so the catalog records the source commit:
git -C submodules/node-remote checkout v<ver>
git add submodules/node-remote && git commit -m "chore: bump node-remote pin to v<ver>" && git push
```

## SIGN, or Basecamp will not install it

Basecamp 0.2.1+ rejects unsigned packages — the in-app Package Manager passes no
`--allow-unsigned`, so an unsigned catalog `.lgx` fails with **"no candidate matches <pkg>"**.
Verify before uploading: `lgx_signer verify <lgx>` must report `signature_valid: yes` and
`signer_name: xAlisher`.

This bites the CI path too (`_release-module.yml` builds `signing_mode: none`), which is why
anything published through the workflow must be downloaded, signed, re-uploaded `--clobber`,
and re-indexed. Publishing manually as above sidesteps that, because the artifact is signed
before it is ever uploaded.

## Platform coverage

Catalog builds are **linux-amd64 only** — `node_remote` bundles `tor`, and darwin cannot be
built on Linux. A darwin variant needs a Mac (wetware). The GitHub release on
`xAlisher/node-remote` carries the same linux-amd64 artifacts.

## Proper fix (tracked)

Same as booth: either **fork the release action** to accept a `build_subdir` input, or split
the repo. Splitting is the wrong trade here — the two modules and the app are versioned and
tested as one unit, and separating them is how the field skew happened in the first place.
