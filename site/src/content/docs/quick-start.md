---
title: 初回チュートリアル
description: 京大スパコン camphor 上で dshield* を動かすまでの手順
---

以下の手順で、まずは京大スパコン *camphor* 上で `dshield*` を動かせる状態にします。

## 1. VS Code から camphor に接続する

- VS Code を起動し、拡張機能 **Remote-SSH** をインストールする

  ![remote-ssh](../../assets/imgs/1.png)
- 京大スパコン *camphor* にログインする

  ![login](../../assets/imgs/2.png)
- TERMINAL を開く

  ![terminal](../../assets/imgs/3.png)

:::tip
接続のたびに SSH パスフレーズを聞かれて煩わしい場合は、[`ssh-agent` でパスフレーズ入力を自動化する](./tips/ssh-agent/) を参照してください（Windows は管理者 PowerShell が必要）。
:::

## 2. 作業領域と Python 環境を準備する

以下のサブステップを上から順に実行してください。

### 2-1. `/LARGE1` 上に作業ディレクトリを作り、`~/large1` からシンボリックリンクを張る

```bash
mkdir -p /LARGE1/gr20001/$USER
ln -s /LARGE1/gr20001/$USER ~/large1
```

:::note
以前は `/LARGE0` を使っていました。`/LARGE0` も引き続き利用可能ですが、最近ストレージが逼迫していて出力ファイルを書き込めないことがたまにあるため、新規には `/LARGE1` を推奨します。`/LARGE0` を使う場合は上記のパスを `/LARGE0/gr20001/$USER` / `~/large0` に読み替えてください。
:::

### 2-2. `$HOME` に Python 3.12 の venv を作る

```bash
/usr/bin/python3.12 -m venv $HOME/.venv
```

### 2-3. venv をその場で有効化する

```bash
source $HOME/.venv/bin/activate
```

ログインのたびに自動で有効化したい場合は `~/.bashrc` にも追記しておきます（ジョブから `mypython` などを呼べるようにするためにも、当面は追記しておくのを推奨）。

```bash
echo 'source $HOME/.venv/bin/activate' >> ~/.bashrc
```

:::note
この venv が不要になったら、上で追記した行を `~/.bashrc` から削除してください。
:::

### 2-4. リポジトリを clone する

```bash
mkdir -p ~/large1/Github
cd ~/large1/Github
git clone https://github.com/CS12-Laboratory/EMSES-tutorials.git
```

### 2-5. 依存パッケージを venv に入れる

```bash
cd ~/large1/Github/EMSES-tutorials
pip install -r requirements.txt
```

`requirements.txt` には可視化・解析用の Python パッケージ（`emout` / `camptools` / `mypython` など）が入っています。ジョブ投入系のコマンド（`mysbatch` / `latestjob` など）は `camptools` 由来でここで入ります。`MPIEMSES3D` 本体（`mpiemses3D`）と入力変換系のコマンド（`emu` / `inp2toml` / `emses-cp`）は次の Step 3 で `mpiemses3d-tools` ごと入ります。

### 2-6. VS Code でリポジトリを開く

```bash
code --reuse-window ~/large1/Github/EMSES-tutorials
```

## 3. MPIEMSES3D の導入方法

推奨は pip からのインストールです。ただ、今回は下の開発・コード編集を行う人向けの`make OPENMP=1`でビルドするようにしてください。OpenMP 有効でビルドされ、`mpiemses3d-tools`（`emu` / `inp2toml` / `emses-cp`）も依存として一緒に入ります。

```bash
MPIEMSES3D_OPENMP=1 pip install git+https://github.com/CS12-Laboratory/MPIEMSES3D.git@v4.10.0
```

<details>
<summary>開発・コード編集を行う人向け（make でビルドする場合）</summary>

ソースを直接いじる開発用途では、リポジトリを clone して `make` でビルドします。

```bash
cd ~/large1/Github
git clone https://github.com/CS12-Laboratory/MPIEMSES3D.git
cd MPIEMSES3D
make OPENMP=1
```

この方法では `emu` / `inp2toml` / `emses-cp` などの周辺ツールは入らないので、別途 `mpiemses3d-tools` を pip で入れてください。

```bash
pip install mpiemses3d-tools
```

（pip 経由で MPIEMSES3D 本体を入れた場合は、こちらも依存として自動でインストールされます。）

</details>

## 4. 実行ファイルを各ケースへ配置する

```bash
cd ~/large1/Github/EMSES-tutorials
cp ~/large1/Github/MPIEMSES3D/bin/mpiemses3D dshield0/
cp ~/large1/Github/MPIEMSES3D/bin/mpiemses3D dshield1/
cp ~/large1/Github/MPIEMSES3D/bin/mpiemses3D dshield2/
```

`job.sh` は `plasma.toml` のみを実行入力として使います。legacy な `plasma.inp` / `plasma.preinp` は各ケースの `.old/` 配下に参照用として置いてあります。

## 5. `plasma.toml` を編集したら `emu apply` する

`dshield*` は `plasma.toml` が標準入力です。`[meta.physical]` や `[meta.unit_conversion]` を変更した場合は、投入前に変換を反映してください。

```bash
cd ~/large1/Github/EMSES-tutorials/dshield1
emu apply plasma.toml --dry-run
emu apply plasma.toml
```

## 6. `dshield0` を実行する

```bash
cd ~/large1/Github/EMSES-tutorials/dshield0
mysbatch job.sh
```

このリポジトリでは `mysbatch` は `plasma.toml` の `[mpi].nodes` を使う前提です。legacy な入力は `.old/` に残しているだけで、投入には使いません。

## 7. ジョブを確認する

```bash
qs
squeue
qgroup
latestjob
```

- ジョブを止める: `scancel <job-id>`
- 標準出力: `stdout.****.log`
- 標準エラー: `stderr.****.log`

## 8. 可視化する

- バッチ実行後は `.mypython/plot.py` により `data/*.png` や `data/gif/*.gif` が生成されます。
- Notebook で見る場合は `dshield0/plot_example.ipynb` を開いてください。

  例: `phisp_2d_xy.png`

  ![plot](../../assets/imgs/phisp_2d_xy.png)

### Notebook 用の Python interpreter を設定する

ステップ 2 で作った `~/.venv` をそのまま使えます。

1. VS Code で `Python: Select Interpreter` を開く

   ![select-interpreter](../../assets/imgs/select_interpreter.png)
2. `Enter Interpreter Path` を選ぶ

   ![enter-interpreter](../../assets/imgs/enter_interpreter_path.png)
3. `~/.venv/bin/python` を指定する

   ![input-interpreter](../../assets/imgs/input_interpreter.png)

参考:

- [emout](https://github.com/Nkzono99/emout)
- [emout のサンプル notebook](https://nbviewer.org/github/Nkzono99/examples/blob/main/examples/emout/example.ipynb)

## 9. 条件を変えて試す

- `dshield0/plasma.toml` の `jobcon.nstep` を増やして、より長い時間発展を見てみる
- `dshield1` / `dshield2` も実行して違いを比べる
- `ds0` を `emout` で可視化するときは、必要に応じて `[[species]]` の `wp` を一時的に非ゼロへ変更する

旧 `advance/` の例は、`MPIEMSES3D` 側の [`cookbook`](https://github.com/CS12-Laboratory/MPIEMSES3D/tree/main/cookbook) を参照してください。

## 10. 結果を考える

- `ds0`: 真空中の負電荷
- `ds1`: 密度 `10^7 /cm^3`、電子温度 `3 eV` のプラズマ
- `ds2`: `ds1` の 1/16 の密度

確認したい点:

- 負電荷まわりの電位分布はどう変わるか
- 電子とイオンの振る舞いはどう変わるか
- 密度や温度を変えると何が支配的に変わるか

## 参考資料

- [京大スパコン利用マニュアル（要認証）](http://web.kudpc.kyoto-u.ac.jp/manual-new/ja)
- [神大スパコン利用マニュアル](http://www.eccse.kobe-u.ac.jp/pi-computer/)
- [MPIEMSES3D Parameters](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.md)
- [MPIEMSES3D Customization](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.md)
