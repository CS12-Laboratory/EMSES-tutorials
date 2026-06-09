Lang: [日本語](README.md) | [English](README_en.md)

# [EMSES-tutorials](https://cs12-laboratory.github.io/EMSES-tutorials/)

本リポジトリは、電磁粒子コード [MPIEMSES3D / EMSES](https://github.com/CS12-Laboratory/MPIEMSES3D) を使い始めるためのチュートリアル集です。

ドキュメントサイト（GitHub Pages）: <https://cs12-laboratory.github.io/EMSES-tutorials/>

## 初回チュートリアル

- 公開サイト: [初回チュートリアル](https://cs12-laboratory.github.io/EMSES-tutorials/quick-start/) / [Quick Start (English)](https://cs12-laboratory.github.io/EMSES-tutorials/en/quick-start/)
- リポジトリ内 Markdown: [docs/QuickStart.md](docs/QuickStart.md) / [docs/QuickStart_en.md](docs/QuickStart_en.md)
- 補足: [FAQ](docs/FAQ.md) / [FAQ (English)](docs/FAQ_en.md)

## パラメータと入力ファイル

- [MPIEMSES3D のパラメータ仕様](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.md)
- [legacy な `plasma.inp` / `plasma.preinp` から `plasma.toml` への移行](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.md)
- [MPIEMSES3D の TOML / `emu` ガイド](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.md)

このリポジトリの `dshield*` では `plasma.toml` を標準入力として使います。`job.sh` は投入時に `emu apply` / `emu lint` / `emu inspect` を実行してから `mpiemses3D` を起動します。legacy な `plasma.inp` / `plasma.preinp` は各ケースの `.old/` ディレクトリへ参照用として隔離してあります。

## 補助ツール

初回セットアップでは `uvx ... emses-tutorials setup` で教材ファイルを展開し、教材ディレクトリ直下の `.venv/` に可視化・解析パッケージと `mysbatch` / `latestjob` などのジョブ補助コマンドを導入します。`MPIEMSES3D` 本体と `emu` / `inp2toml` / `emses-cp` は、[初回チュートリアル](docs/QuickStart.md) の手順で同じ `.venv/` に別途インストールします。

## 上級例

旧 `advance/` に置いていた上級例は、`MPIEMSES3D` 側の [`cookbook`](https://github.com/CS12-Laboratory/MPIEMSES3D/tree/main/cookbook) に移行しました。
