Lang: [日本語](README.md) | [English](README_en.md)

# [EMSES-tutorials](https://cs12-laboratory.github.io/EMSES-tutorials/)

This repository provides tutorials for getting started with [MPIEMSES3D / EMSES](https://github.com/CS12-Laboratory/MPIEMSES3D).

Documentation site (GitHub Pages): <https://cs12-laboratory.github.io/EMSES-tutorials/>

## Quick Start

- Published site: [Quick Start](https://cs12-laboratory.github.io/EMSES-tutorials/en/quick-start/) / [初回チュートリアル (Japanese)](https://cs12-laboratory.github.io/EMSES-tutorials/quick-start/)
- In-repo Markdown: [docs/QuickStart_en.md](docs/QuickStart_en.md) / [docs/QuickStart.md](docs/QuickStart.md)

## Parameters and Input Files

- [MPIEMSES3D parameter reference](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.en.md)
- [Migration from legacy `plasma.inp` / `plasma.preinp` to `plasma.toml`](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.en.md)
- [MPIEMSES3D TOML / `emu` guide](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.en.md)

The `dshield*` cases in this repository use `plasma.toml` as the primary input file. If you edit `[meta.physical]`, run `emu apply plasma.toml` before submitting the job. Legacy `plasma.inp` / `plasma.preinp` files are archived under each case's `.old/` directory for reference only.

## Helper Tools

The first setup uses `uvx ... emses-tutorials setup` to expand the tutorial files and install visualization / analysis packages plus job helpers such as `mysbatch` and `latestjob` into the tutorial-local `.venv/`. Install `MPIEMSES3D` itself and helper commands such as `emu`, `inp2toml`, `emses-cp`, and `cpem` into the same `.venv/` by following the [Quick Start](docs/QuickStart_en.md).

## Advanced Examples

The advanced examples formerly stored under `advance/` have moved to [`cookbook`](https://github.com/CS12-Laboratory/MPIEMSES3D/tree/main/cookbook) in the `MPIEMSES3D` repository.
