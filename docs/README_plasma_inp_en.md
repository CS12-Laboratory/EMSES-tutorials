Lang: [日本語](README_plasma_inp.md) | [English](README_plasma_inp_en.md)

# Legacy `plasma.inp`

`EMSES-tutorials` now treats `plasma.toml` as the recommended input format. Legacy inputs are archived as `.old/plasma.inp` / `.old/plasma.preinp` in each case, and new edits should be made in `plasma.toml`.

## Read This First

- [`plasma.toml` guide](README_plasma_toml_en.md)
- Official `MPIEMSES3D` parameter reference:
  https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.en.md
- `meta.physical` and `emu` guide:
  https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.en.md

## Converting from Legacy Inputs

Use `inp2toml` from `MPIEMSES3D` to convert the archived `.old/plasma.inp` into a `format_version = 2` `plasma.toml`.

```bash
PYTHONPATH=~/large0/Github/MPIEMSES3D \
python -m mpiemses3d_tools.inp2toml .old/plasma.inp --format-version 2 -o plasma.toml
```

If you previously relied on `.old/plasma.preinp` for physical-unit input and unit conversion, the recommended replacement is `[meta.physical]` in `plasma.toml` together with `emu apply`.
