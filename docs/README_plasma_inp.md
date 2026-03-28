# Legacy `plasma.inp`

`EMSES-tutorials` では `plasma.toml` を推奨形式に切り替えました。`plasma.inp` は後方互換のために一部残っていますが、新規編集は `plasma.toml` を使ってください。

## まず見るべきもの

- [`plasma.toml` の説明](README_plasma_toml.md)
- `MPIEMSES3D` の公式パラメータ仕様:
  https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.md
- `meta.physical` と `emu` の説明:
  https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.md

## legacy からの変換

`MPIEMSES3D` の `inp2toml` を使えば、`plasma.inp` を `format_version = 2` の `plasma.toml` へ変換できます。

```bash
PYTHONPATH=~/large0/Github/MPIEMSES3D \
python -m mpiemses3d_tools.inp2toml plasma.inp --format-version 2 -o plasma.toml
```

`plasma.preinp` に置いていた物理量ベースの入力は、`plasma.toml` の `[meta.physical]` と `emu apply` に移すのが現在の推奨です。
