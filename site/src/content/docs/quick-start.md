---
title: 初回チュートリアル
description: 京大スパコン camphor 上で dshield* を個人環境から動かすまでの手順
---

このページでは、京大スパコン *camphor* 上で `EMSES-tutorials` を各自の作業領域に展開し、最初の `dshield0` ケースを投入して結果を見るところまで進めます。

作業ディレクトリ、Python 環境、展開済み教材ディレクトリは各自で持つ前提にしています。

## このページのゴール

- VS Code Remote-SSH で *camphor* に接続する
- `/LARGE1/gr20001/$USER` に個人用の作業領域を作る
- `uv` / `uvx` を入れ、`emses-tutorials setup` で教材ファイルを展開する
- Python venv、解析ツール、`MPIEMSES3D` をインストールする
- `dshield0` を `mysbatch` で実行し、ログと図を確認する

全体の流れは次の通りです。

```text
uvx ... emses-tutorials setup で教材を展開
  -> plasma.toml を確認・編集
  -> cpem で mpiemses3D 実行ファイルをケースへ配置
  -> job.sh 内の emu apply / lint / inspect で入力を確認
  -> mysbatch job.sh で計算ノードへ投入
  -> stdout/stderr と data/ の図を確認
```

## 0. 始める前に

手元に以下があることを確認してください。

- 京大スパコンのアカウントと *camphor* への SSH 接続情報
- VS Code と **Remote - SSH** 拡張機能
- `CS12-Laboratory/MPIEMSES3D` への GitHub アクセス権
- SSH 秘密鍵と、設定している場合はそのパスフレーズ

`MPIEMSES3D` は private repository なので、Step 6 のインストール前に GitHub 認証が必要になることがあります。

## 1. VS Code から camphor に接続する

VS Code を起動し、拡張機能 **Remote - SSH** をインストールします。

![remote-ssh](../../assets/imgs/1.png)

京大スパコン *camphor* にログインします。

![login](../../assets/imgs/2.png)

接続できたら、remote window の TERMINAL を開きます。

![terminal](../../assets/imgs/3.png)

:::tip
接続のたびに SSH パスフレーズを聞かれて煩わしい場合は、[`ssh-agent` でパスフレーズ入力を自動化する](../tips/ssh-agent/) を参照してください。Windows では管理者 PowerShell が必要です。
:::

## 2. 個人用の作業領域と PATH を準備する

このチュートリアルでは、各自が自分の `/LARGE1/gr20001/$USER` を使います。

```bash
mkdir -p /LARGE1/gr20001/$USER
if [ ! -e "$HOME/large1" ] && [ ! -L "$HOME/large1" ]; then
  ln -s /LARGE1/gr20001/$USER "$HOME/large1"
fi
mkdir -p "$HOME/large1/Github" "$HOME/.local/bin"
export PATH="$HOME/.local/bin:$PATH"
ls -ld "$HOME/large1" "$HOME/large1/Github"
```

:::note
以前は `/LARGE0` を使っていました。`/LARGE0` も引き続き利用可能ですが、最近ストレージが逼迫していて出力ファイルを書き込めないことがあるため、新規には `/LARGE1` を推奨します。`/LARGE0` を使う場合は、上記のパスを `/LARGE0/gr20001/$USER` / `~/large0` に読み替えてください。
:::

## 3. uv と GitHub 認証を準備する

### 3-1. uv をインストールする

`uvx` でセットアップコマンドを実行し、同じ `uv` で Python パッケージも入れます。

```bash
curl -LsSf https://astral.sh/uv/install.sh | \
  env UV_INSTALL_DIR="$HOME/.local/bin" UV_NO_MODIFY_PATH=1 sh
export PATH="$HOME/.local/bin:$PATH"
hash -r
command -v uv
command -v uvx
uvx --version
```

### 3-2. MPIEMSES3D への GitHub アクセスを確認する

まず、private repository を読めるか確認します。成功した場合、このコマンドは何も表示せずに終了します。

```bash
git ls-remote https://github.com/CS12-Laboratory/MPIEMSES3D.git >/dev/null
```

認証を求められる、または失敗する場合は GitHub CLI でログインします。

<details>
<summary>GitHub CLI で認証する場合</summary>

`gh` がまだ入っていない場合は、最新 release をユーザー領域にインストールします。

```bash
GH_VERSION=$(
  curl -fsSL https://api.github.com/repos/cli/cli/releases/latest |
  sed -n 's/.*"tag_name": "v\([^"]*\)".*/\1/p' |
  head -n 1
)
test -n "$GH_VERSION"

tmpdir=$(mktemp -d)
curl -fsSL \
  "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz" \
  -o "$tmpdir/gh.tar.gz"
tar -xzf "$tmpdir/gh.tar.gz" -C "$tmpdir"
install -m 0755 "$tmpdir/gh_${GH_VERSION}_linux_amd64/bin/gh" "$HOME/.local/bin/gh"
rm -rf "$tmpdir"
gh --version
```

GitHub にログインし、Git の認証にも反映します。

```bash
gh auth login --web --git-protocol https
gh auth setup-git
gh auth status
git ls-remote https://github.com/CS12-Laboratory/MPIEMSES3D.git >/dev/null
```

最後の `git ls-remote` が失敗する場合は、GitHub 側で `CS12-Laboratory/MPIEMSES3D` へのアクセス権が付いているか確認してください。

</details>

## 4. 教材ディレクトリを作って VS Code で開く

`setup` で中身を展開する先のディレクトリを先に作り、VS Code で開きます。

```bash
mkdir -p "$HOME/large1/Github/EMSES-tutorials"
code --reuse-window "$HOME/large1/Github/EMSES-tutorials"
```

以降のコマンドは、開いた VS Code remote window の TERMINAL で実行します。

## 5. セットアップコマンドで教材を展開する

`git clone` は手で実行せず、`uvx` 経由の `emses-tutorials setup` で教材ファイルとディレクトリを展開します。セットアップコマンドは `docs/`、`dshield*/`、`imgs/`、`.mypython/`、`.vscode/` などを作成し、教材ディレクトリ直下の `.venv/` に `requirements.txt` もインストールします。

`code` コマンドが使える場合は、VS Code の Python / Jupyter / TOML 拡張機能もインストールします。拡張機能の導入をスキップしたい場合は `--no-extensions` を付けてください。

```bash
cd "$HOME/large1/Github/EMSES-tutorials"
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials setup "$PWD"
```

既存ファイルがある場合、セットアップコマンドはデフォルトでは上書きせずに残します。教材ファイルを明示的に更新したい場合だけ `--overwrite` を付けて再実行してください。

```bash
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials setup "$PWD" --overwrite
```

この手順では、`.venv` の有効化のために `~/.bashrc` は変更しません。

`setup` 後に、このリポジトリの `.vscode/settings.json` が `${workspaceFolder}/.venv/bin/python` を Python interpreter として指定します。VS Code の window を reload し、Python 拡張機能が入った状態で新しい TERMINAL を開くと、通常は `.venv` が自動で有効化されます。

新しい TERMINAL で次を確認してください。

```bash
command -v python
python -c 'import sys; print(sys.executable)'
```

表示される Python が `.../EMSES-tutorials/.venv/bin/python` でない場合は、VS Code の window を reload し、`Python: Select Interpreter` で `.venv/bin/python` を選んでから新しい TERMINAL を開き直してください。

セットアップ状態をまとめて確認したい場合は `doctor` を使います。

```bash
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials doctor "$PWD"
```

教材ファイルを戻したい場合は `repair` を使います。まず `--dry-run` で対象ファイルを確認してください。通常の `repair` は、編集することが多い `plasma.toml` と notebook は上書きしません。

```bash
uvx --no-cache \
  --from "git+https://github.com/CS12-Laboratory/EMSES-tutorials.git@main" \
  emses-tutorials repair "$PWD" --dry-run
```

## 6. MPIEMSES3D をインストールする

通常は pip からインストールします。OpenMP 有効でビルドし、`mpiemses3d-tools` 由来の `emu` / `inp2toml` / `emses-cp` / `cpem` も一緒に入ります。

```bash
cd "$HOME/large1/Github/EMSES-tutorials"
MPIEMSES3D_OPENMP=1 python -m pip install \
  "git+https://github.com/CS12-Laboratory/MPIEMSES3D.git@v4.16.6"
```

インストール後、コマンドが見えることを確認します。

```bash
command -v python
command -v mysbatch
command -v emu
command -v cpem
mpiemses3D --version
```

<details>
<summary>開発・コード編集を行う人向け（make でビルドする場合）</summary>

`MPIEMSES3D` 本体を編集する場合は、リポジトリを clone して `make` でビルドします。

```bash
cd "$HOME/large1/Github"
git clone https://github.com/CS12-Laboratory/MPIEMSES3D.git
cd MPIEMSES3D
make OPENMP=1
python -m pip install mpiemses3d-tools==4.16.6
```

この方法では、各ケースに置く実行ファイルとして `MPIEMSES3D/bin/mpiemses3D` を使います。`emu` / `inp2toml` / `emses-cp` / `cpem` は `mpiemses3d-tools` から入ります。

</details>

## 7. 実行ファイルを各ケースへ配置する

`job.sh` はケースディレクトリ内の `./mpiemses3D` を実行します。pip で入れた実行ファイルを `cpem` で各ケースにコピーします。

```bash
cd "$HOME/large1/Github/EMSES-tutorials"
cpem dshield0/
cpem dshield1/
cpem dshield2/
ls -l dshield0/mpiemses3D dshield1/mpiemses3D dshield2/mpiemses3D
```

`job.sh` は `plasma.toml` だけを実行入力として使います。legacy な `plasma.inp` / `plasma.preinp` は、各ケースの `.old/` 配下に参照用として置いてあります。

## 8. dshield0 を実行する

まずは最短の確認として `dshield0` を投入します。

```bash
cd "$HOME/large1/Github/EMSES-tutorials/dshield0"
qgroup
emu apply plasma.toml --dry-run
mysbatch job.sh
```

`qgroup` では、自分のアカウントから使える resource group を確認します。`job.sh` の `#SBATCH -p ...` に書かれている group が使えない場合は、担当者に確認してください。

ログインノードでは `bash job.sh` や `srun ./mpiemses3D ...` を直接実行しないでください。`mysbatch job.sh` が計算ノードへ投入します。

このリポジトリの `job.sh` は、主に次の処理を行います。

1. Camphor の Intel / Intel MPI module を読み込む
2. 教材ディレクトリ直下の `.venv` を有効化する
3. `plasma.toml` と `./mpiemses3D` があることを確認する
4. `emu apply plasma.toml` で物理単位メタデータを反映する
5. `emu lint --mpi-size 112 plasma.toml` で入力を検査する
6. `emu inspect plasma.toml | tee inspect.log` で入力サマリを保存する
7. 古い `*_0000.h5` を削除する
8. `srun ./mpiemses3D plasma.toml` を実行する
9. `.mypython/plot.py` により簡易図を生成する

:::note
`emu apply plasma.toml --dry-run` は、投入前に変換内容を確認したいときのプレビューです。実際の反映と検査は `job.sh` の中でもう一度実行されます。
:::

## 9. ジョブとログを確認する

```bash
qs
squeue
qgroup
latestjob
```

- ジョブを止める: `scancel <job-id>`
- 標準出力: `stdout.****.log`
- 標準エラー: `stderr.****.log`

ログを見る例:

```bash
less stdout.*.log
less stderr.*.log
```

再実行すると同じケースディレクトリに新しいログや出力が書かれます。残したい結果がある場合は、別名のディレクトリへコピーしてから再投入してください。

## 10. 可視化する

バッチ実行後は `.mypython/plot.py` により `data/*.png` や `data/gif/*.gif` が生成されます。

Notebook で確認する場合は、`dshield0/plot_example.ipynb` を開いてください。

例: `phisp_2d_xy.png`

![plot](../../assets/imgs/phisp_2d_xy.png)

### Notebook 用の Python interpreter を設定する

Step 5 で作ったローカル `.venv` をそのまま使えます。

1. VS Code で `Python: Select Interpreter` を開く

   ![select-interpreter](../../assets/imgs/select_interpreter.png)
2. `Enter Interpreter Path` を選ぶ

   ![enter-interpreter](../../assets/imgs/enter_interpreter_path.png)
3. `.venv/bin/python` を指定する

   ![input-interpreter](../../assets/imgs/input_interpreter.png)

参考:

- [emout](https://github.com/Nkzono99/emout)
- [emout のサンプル notebook](https://nbviewer.org/github/Nkzono99/examples/blob/main/examples/emout/example.ipynb)

## 11. 条件を変えて試す

最初の実行が通ったら、次のように条件を変えて比較します。

- `dshield1` / `dshield2` も実行して、真空・高密度・低密度の違いを見る
- `dshield0/plasma.toml` の `jobcon.nstep` を増やして、より長い時間発展を見る
- `[meta.physical]` の密度、温度、固定電位などを変え、`emu apply` 後の値を確認する
- `ds0` を `emout` で可視化するときは、必要に応じて `[[species]]` の `wp` を一時的に非ゼロへ変更する

`plasma.toml` を編集した後の基本形は次の通りです。

```bash
emu apply plasma.toml --dry-run
mysbatch job.sh
```

## 12. 結果を考える

| ケース | 物理設定 |
| --- | --- |
| `dshield0` | 真空中の負電荷 |
| `dshield1` | 密度 `10^7 /cm^3`、電子温度 `3 eV` のプラズマ |
| `dshield2` | `dshield1` の 1/16 の密度 |

確認したい点:

- 負電荷まわりの電位分布はどう変わるか
- 電子とイオンの振る舞いはどう変わるか
- 密度や温度を変えると何が支配的に変わるか

旧 `advance/` の例は、`MPIEMSES3D` 側の [`cookbook`](https://github.com/CS12-Laboratory/MPIEMSES3D/tree/main/cookbook) を参照してください。

## よくあるつまずき

- `uvx` が見つからない: `export PATH="$HOME/.local/bin:$PATH"` を実行し、`uv` のインストールが成功しているか確認してください。
- `git ls-remote` や `pip install git+https://...MPIEMSES3D...` が失敗する: GitHub 認証、または private repository へのアクセス権を確認してください。
- `command -v emu` が空になる: VS Code の window を reload し、Python interpreter に `.venv/bin/python` を選んでから新しい TERMINAL を開いてください。Step 6 の pip install が成功しているかも確認してください。
- `mysbatch` が見つからない: 新しい VS Code TERMINAL で `.venv` が有効化されているか確認し、必要なら `uvx ... emses-tutorials setup ...` を再実行してください。
- `./mpiemses3D` がないと言われる: 教材ディレクトリ root で `cpem dshield0/` などを再実行してください。
- resource group のエラーで投入できない: `qgroup` と `job.sh` の `#SBATCH -p ...` を確認し、使える group を担当者に確認してください。

## 参考資料

- [京大スパコン利用マニュアル（要認証）](http://web.kudpc.kyoto-u.ac.jp/manual-new/ja)
- [神大スパコン利用マニュアル](http://www.eccse.kobe-u.ac.jp/pi-computer/)

MPIEMSES3D 本体リポジトリは private なので、以下の GitHub リンクを開くにはアクセス権が必要です。ローカルに clone 済みの場合は `MPIEMSES3D/docs/` 以下にも同じドキュメントがあります。

- 入力ファイルを編集する:
  - [入力パラメータリファレンス](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.md) - `plasma.toml` / `plasma.inp` の各パラメータ、単位系、namelist の詳細
  - [TOML 新形式 `format_version = 2`](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/FormatV2.md) - `[[species]]` や `[[ptcond.objects]]` などの構造化 TOML の書き方
  - [`plasma.toml` カスタマイズガイド](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.md) - `[meta.physical]`、`emu apply`、Python でのケース生成
- 出力を確認・解析する:
  - [出力ファイルリファレンス](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/OutputFiles.md) - `data/` 配下のテキスト診断、HDF5、snapshot、`emout` での読み方
  - [解析ガイド](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/agent-analysis-guide.md) - `emout` / Python 解析、SI 単位変換、典型的な解析ワークフロー
- 仕組みを詳しく追う:
  - [アルゴリズム仕様](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Algorithms_ja.md) - PIC、FDTD、Poisson solver、Boris pusher、表面相互作用
  - [アーキテクチャ](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/ARCHITECTURE.md) - コード構成、1 ステップのデータフロー、MPI 同期ポイント
  - [cookbook](https://github.com/CS12-Laboratory/MPIEMSES3D/tree/main/cookbook) - 入力例集と旧 `advance/` の上級例
