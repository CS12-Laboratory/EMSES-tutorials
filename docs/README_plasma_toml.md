Lang: [日本語](README_plasma_toml.md) | [English](README_plasma_toml_en.md)

# EMSES Parameter File: `plasma.toml`

`EMSES-tutorials` では、入力ファイルの標準を `plasma.toml` に移行しました。legacy な `plasma.inp` / `plasma.preinp` は各ケースの `.old/` 配下へ archive してあり、今後の編集は `plasma.toml` を起点にする想定です。

## 基本方針

- シミュレーションで直接読まれる値は `plasma.toml` の `[[species]]`, `[plasma]`, `[tmgrid]`, `[ptcond]`, `[mpi]` などに入っています。
- 物理単位ベースの入力は `[meta.physical]` に書き、必要に応じて `emu apply plasma.toml` で正規化値へ反映します。
- 旧 `!!key dx=[...],to_c=[...]` は `[meta.unit_conversion]` に移っています。

## 典型的な構造

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

## チュートリアルでの編集手順

1. `dshield*/plasma.toml` を開く。
2. 物理条件を変えるときは `[meta.physical]` を編集する。
3. 変更後に `emu apply plasma.toml` を実行する。
4. `mysbatch job.sh` または `sbatch job.sh` で投入する。

このリポジトリの `job.sh` は `plasma.toml` のみを実行入力として使います。`.old/` は参照用です。

`emu` を PATH に入れていない場合は、`MPIEMSES3D` の開発リポジトリを使って次のように実行できます。

```bash
PYTHONPATH=~/large1/Github/MPIEMSES3D \
python -m mpiemses3d_tools.cli.emses_unit apply plasma.toml
```

## 参考

- `MPIEMSES3D` パラメータ全体: https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.md
- `plasma.toml` の新形式: https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/FormatV2.md
- `meta.physical` と `emu` の使い方: https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.md
