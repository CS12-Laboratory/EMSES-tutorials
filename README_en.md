Lang: [日本語](README.md) | [English](README_en.md)

# [EMSES-tutorials](https://cs12-laboratory.github.io/EMSES-tutorials/)

This repository provides tutorials for getting started with [MPIEMSES3D / EMSES](https://github.com/CS12-Laboratory/MPIEMSES3D).

## Quick Start

- [Quick Start Tutorial](docs/QuickStart_en.md)
- [初回チュートリアル (Japanese)](docs/QuickStart.md)

## Parameters and Input Files

- [MPIEMSES3D parameter reference](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.en.md)
- [Migration from legacy `plasma.inp` / `plasma.preinp` to `plasma.toml`](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.en.md)
- [MPIEMSES3D TOML / `emu` guide](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.en.md)

The `dshield*` cases in this repository use `plasma.toml` as the primary input file. If you edit `[meta.physical]`, run `emu apply plasma.toml` before submitting the job. Legacy `plasma.inp` / `plasma.preinp` files are archived under each case's `.old/` directory for reference only.

## Helper Tools

`pip install -r requirements.txt` installs the visualization packages as well as `MPIEMSES3D` helper commands such as `emu`, `inp2toml`, and `emses-cp`.

## Advanced Examples

The advanced examples formerly stored under `advance/` have moved to [`parameter_examples`](https://github.com/CS12-Laboratory/MPIEMSES3D/tree/main/parameter_examples) in the `MPIEMSES3D` repository.
