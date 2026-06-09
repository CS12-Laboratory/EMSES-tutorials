---
title: FAQ
description: セットアップ診断と教材ファイル修復の補足
---

初回手順を進めていて状態確認や修復が必要になったときの補足です。通常は [初回チュートリアル](../quick-start/) だけで進められます。

## セットアップ状態をまとめて確認したい

教材ディレクトリで `doctor` を実行します。`doctor` はファイルを変更せず、必要なファイル、`.vscode/settings.json`、`.venv`、Python パッケージ、補助コマンドの状態を確認します。

```bash
cd "$HOME/large1/Github/EMSES-tutorials"
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials doctor "$PWD"
```

`mpiemses3D` / `emu` / `cpem` は Step 6 の MPIEMSES3D インストール後に見えるようになります。Step 5 直後に警告が出る場合がありますが、その時点ではまだ正常です。

## 教材ファイルだけ修復したい

まず `--dry-run` で修復対象を確認します。

```bash
cd "$HOME/large1/Github/EMSES-tutorials"
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials repair "$PWD" --dry-run
```

問題なければ、教材の管理ファイルを復元します。

```bash
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials repair "$PWD" --skip-install
```

通常の `repair` は、`docs/`、`.mypython/`、`.vscode/`、`README*`、`dshield*/job.sh` などを復元します。各自で編集しやすい `dshield*/plasma.toml` と notebook は、デフォルトでは触りません。

`plasma.toml` や legacy 入力ファイルも教材版に戻したい場合だけ、次のように明示します。

```bash
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials repair "$PWD" --skip-install --include-parameters
```

notebook も戻したい場合は `--include-notebooks` を付けます。変更済みファイルは、上書き前に `.emses-tutorials/backups/repair-*` へ退避されます。

## 教材ファイルをまとめて更新したい

`setup` は既存ファイルをデフォルトでは残します。教材ファイルを明示的に最新版へ更新したい場合だけ、`--overwrite` を付けて再実行します。

```bash
cd "$HOME/large1/Github/EMSES-tutorials"
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials setup "$PWD" --overwrite --no-extensions
```

`--overwrite` は教材ファイルを上書きするため、手元で編集した内容を残したい場合は事前に別名で保存してください。

## VS Code 拡張機能を入れ直したい

QuickStart では、拡張機能のインストールを手順として明示するために `setup` へ `--no-extensions` を付けています。入れ直したい場合は次を実行し、最後に VS Code window を reload します。

```bash
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
code --install-extension tamasfe.even-better-toml
```

拡張機能のインストール後、Command Palette を `Ctrl+Shift+P` で開き、`reload` と入力して **Developer: Reload Window** を実行します。

## setup / repair で展開されないもの

参加者向けの `setup` / `repair` は allowlist 方式です。`.github/`、`site/`、`src/`、`pyproject.toml`、`AGENTS.md` など、教材実行に不要なメンテナンス用ファイルは展開しません。
