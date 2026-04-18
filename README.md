Lang: [日本語](README.md) | [English](README_en.md)

# [EMSES-tutorials](https://cs12-laboratory.github.io/EMSES-tutorials/)

本リポジトリは、電磁粒子コード [MPIEMSES3D / EMSES](https://github.com/CS12-Laboratory/MPIEMSES3D) を使い始めるためのチュートリアル集です。

ドキュメントサイト（GitHub Pages）: <https://cs12-laboratory.github.io/EMSES-tutorials/>

## 初回チュートリアル

- 公開サイト: [初回チュートリアル](https://cs12-laboratory.github.io/EMSES-tutorials/quick-start/) / [Quick Start (English)](https://cs12-laboratory.github.io/EMSES-tutorials/en/quick-start/)
- リポジトリ内 Markdown: [docs/QuickStart.md](docs/QuickStart.md) / [docs/QuickStart_en.md](docs/QuickStart_en.md)

## パラメータと入力ファイル

- [MPIEMSES3D のパラメータ仕様](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.md)
- [legacy な `plasma.inp` / `plasma.preinp` から `plasma.toml` への移行](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.md)
- [MPIEMSES3D の TOML / `emu` ガイド](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.md)

このリポジトリの `dshield*` では `plasma.toml` を標準入力として使います。`[meta.physical]` を編集した場合は、投入前に `emu apply plasma.toml` を実行してください。legacy な `plasma.inp` / `plasma.preinp` は各ケースの `.old/` ディレクトリへ参照用として隔離してあります。

## 補助ツール

`pip install -r requirements.txt` で、可視化に使う Python パッケージに加えて `MPIEMSES3D` 関連ツール `emu` / `inp2toml` / `emses-cp` などの補助コマンドも導入されます。

## 上級例

旧 `advance/` に置いていた上級例は、`MPIEMSES3D` 側の [`parameter_examples`](https://github.com/CS12-Laboratory/MPIEMSES3D/tree/main/parameter_examples) に移行しました。
