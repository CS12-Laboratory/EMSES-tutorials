# AGENTS.md

This repository contains tutorial materials for running MPIEMSES3D / EMSES
cases on Kyoto University's camphor supercomputer.

## Repository Shape

- `docs/` contains the repository Markdown documentation.
- `site/src/content/docs/` contains the Starlight site copy of the main docs.
- `dshield0/`, `dshield1/`, and `dshield2/` are tutorial cases.
- `src/emses_tutorials/` contains the lightweight `emses-tutorials` setup CLI.
- `requirements.txt` is installed into the tutorial-local `.venv/` by the
  setup helper for visualization, analysis, and job helper commands.

## Documentation Rules

- Keep Japanese and English QuickStart / FAQ pages in sync:
  - `docs/QuickStart.md`
  - `docs/QuickStart_en.md`
  - `docs/FAQ.md`
  - `docs/FAQ_en.md`
  - `site/src/content/docs/quick-start.md`
  - `site/src/content/docs/en/quick-start.md`
  - `site/src/content/docs/faq.md`
  - `site/src/content/docs/en/faq.md`
- Keep this repository focused on its own individual tutorial workflow.
- If setup steps change, update both the repository docs and the site docs.
- The site pages need Starlight admonition syntax (`:::note`, `:::tip`), while
  the repository Markdown uses blockquotes (`> NOTE:`, `> TIP:`).

## Setup CLI

- The participant-facing setup command is:

  ```bash
  uvx --no-cache \
    --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
    emses-tutorials setup "$HOME/large1/Github/EMSES-tutorials"
  ```

- Keep the CLI small and standard-library-only where possible.
- The setup CLI expands tutorial files from the GitHub archive. It should not
  require participants to clone this repository manually.
- Keep participant expansion and repair allowlisted. Do not deploy maintainer
  paths such as `.github/`, `site/`, `src/`, `pyproject.toml`, or `AGENTS.md`.
- The setup CLI should create/use the tutorial-local `.venv/`; do not activate
  it by editing `~/.bashrc`.
- Existing participant files are kept by default; overwrite behavior should
  require an explicit flag such as `--overwrite`.
- `doctor` should diagnose local setup without modifying files. `repair`
  should restore only managed tutorial files by default and require explicit
  flags before touching `plasma.toml` or notebooks.

## Generated Files

Do not commit generated outputs or dependency directories:

- `site/node_modules/`
- `site/dist/`
- `site/.astro/`
- `build/`
- `*.egg-info/`
- `__pycache__/`
- simulation outputs such as `*.h5`, `*.xdmf`, `*.log`, and generated plots

The repository uses an allowlist-style `.gitignore`; add explicit exceptions
when introducing new source files.

## Validation

After changing docs or the site, run:

```bash
cd site
npm run build
```

After changing the setup CLI, run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/emses_tutorials/cli.py
uvx --no-cache --from . emses-tutorials --help
uvx --no-cache --from . emses-tutorials doctor --help
uvx --no-cache --from . emses-tutorials repair --help
```

For a non-mutating setup smoke test, use `--skip-install` and
`--no-extensions` against a temporary directory.
