---
title: FAQ
description: Setup diagnostics and managed tutorial file repair
---

This page collects setup checks and repair notes that are useful only when something goes wrong. In the usual path, follow the [Quick Start](../quick-start/).

## Check the setup state

Run `doctor` from the tutorial directory. `doctor` does not modify files; it checks required files, `.vscode/settings.json`, `.venv`, Python packages, and helper commands.

```bash
cd "$HOME/large1/Github/EMSES-tutorials"
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials doctor "$PWD"
```

`mpiemses3D`, `emu`, and `cpem` become available after installing MPIEMSES3D in Step 6. Warnings about them are expected right after Step 5.

## Repair managed tutorial files

First inspect the files that would be repaired.

```bash
cd "$HOME/large1/Github/EMSES-tutorials"
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials repair "$PWD" --dry-run
```

If the list looks right, restore the managed tutorial files.

```bash
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials repair "$PWD" --skip-install
```

By default, `repair` restores files such as `docs/`, `.mypython/`, `.vscode/`, `README*`, and `dshield*/job.sh`. It does not touch `dshield*/plasma.toml` or notebooks, because those are common places for personal edits.

Only add `--include-parameters` when you intentionally want to reset `plasma.toml` and archived legacy input files to the tutorial version.

```bash
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials repair "$PWD" --skip-install --include-parameters
```

Add `--include-notebooks` if you also want to restore notebooks. Changed files are backed up under `.emses-tutorials/backups/repair-*` before they are overwritten.

## Refresh all tutorial files

By default, `setup` keeps existing files. Use `--overwrite` only when you explicitly want to refresh deployed tutorial files from the current tutorial source.

```bash
cd "$HOME/large1/Github/EMSES-tutorials"
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials setup "$PWD" --overwrite --no-extensions
```

Because `--overwrite` replaces tutorial files, save any personal edits you want to keep before running it.

## Reinstall VS Code extensions

The Quick Start passes `--no-extensions` to `setup` so that extension installation stays explicit in the instructions. To reinstall the extensions manually, run:

```bash
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
code --install-extension tamasfe.even-better-toml
```

After installing the extensions, open the Command Palette with `Ctrl+Shift+P`, type `reload`, and run **Developer: Reload Window**.

## Files not expanded by setup / repair

Participant-facing `setup` and `repair` use an allowlist. They do not expand maintainer-only paths such as `.github/`, `site/`, `src/`, `pyproject.toml`, or `AGENTS.md`.
