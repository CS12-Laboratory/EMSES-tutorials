Lang: [日本語](README_plasma_toml.md) | [English](README_plasma_toml_en.md)

# EMSES Parameter File: `plasma.toml`

`EMSES-tutorials` has moved to `plasma.toml` as the primary input format. Legacy `plasma.inp` / `plasma.preinp` files are archived under each case's `.old/` directory, and future edits are expected to start from `plasma.toml`.

## Basic Policy

- The values read directly by the simulator live in `plasma.toml`, such as `[[species]]`, `[plasma]`, `[tmgrid]`, `[ptcond]`, and `[mpi]`.
- Physical-unit inputs should be written in `[meta.physical]`, then converted into normalized simulation values with `emu apply plasma.toml` when needed.
- The old `!!key dx=[...],to_c=[...]` header is now represented by `[meta.unit_conversion]`.

## Typical Structure

```toml
[meta]
format_version = 2

[meta.unit_conversion]
dx = 0.001
to_c = 1000.0

[meta.physical]
density_m3 = 1.0e13
particles_per_cell = 50

[[meta.physical.species]]
label = "electron"
mass_ratio = 1.0
qm_sign = -1
temperature_eV = 3.0
drift_velocity_m_s = 0.0

[[species]]
wp = 0.595073797771703
qm = -1.0
npin = 103219200
path = 2.422984430556998
peth = 2.422984430556998
```

## Editing Workflow for These Tutorials

1. Open `dshield*/plasma.toml`.
2. Edit `[meta.physical]` when you want to change physical conditions.
3. Run `emu apply plasma.toml` after editing.
4. Submit the case with `mysbatch job.sh` or `sbatch job.sh`.

In this repository, `job.sh` uses only `plasma.toml` as the runtime input. The `.old/` files are kept only for reference.

If `emu` is not on your `PATH`, you can invoke it from the `MPIEMSES3D` development repository like this:

```bash
PYTHONPATH=~/large1/Github/MPIEMSES3D \
python -m mpiemses3d_tools.cli.emses_unit apply plasma.toml
```

## References

- Full `MPIEMSES3D` parameter reference: https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.en.md
- New `plasma.toml` format: https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/FormatV2.en.md
- `meta.physical` and `emu` usage: https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.en.md
