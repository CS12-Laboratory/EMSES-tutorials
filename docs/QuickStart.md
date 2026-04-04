Lang: [日本語](QuickStart.md) | [English](QuickStart_en.md)

# 初回チュートリアル

以下の手順で、まずは京大スパコン *camphor* 上で `dshield*` を動かせる状態にします。

## 1. VS Code から camphor に接続する

- VS Code を起動し、拡張機能 **Remote-SSH** をインストールする
  
  ![remote-ssh](../imgs/1.png)
- 京大スパコン *camphor* にログインする
  
  ![login](../imgs/2.png)
- TERMINAL を開く
  
  ![terminal](../imgs/3.png)

## 2. 作業領域と Python 環境を準備する

```bash
mkdir -p /LARGE0/gr20001/$USER
ln -s /LARGE0/gr20001/$USER ~/large0

grep -qxF 'module load intel-python' ~/.bashrc || echo 'module load intel-python' >> ~/.bashrc
grep -qxF 'export PATH="$PATH:$HOME/.local/bin"' ~/.bashrc || echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc

exec "$SHELL" -l

mkdir -p ~/large0/Github
cd ~/large0/Github
git clone https://github.com/CS12-Laboratory/EMSES-tutorials.git
cd EMSES-tutorials
pip install -r requirements.txt
code --reuse-window ~/large0/Github/EMSES-tutorials
```

## 3. MPIEMSES3D の導入方法

```bash
cd ~/large0/Github
git clone https://github.com/CS12-Laboratory/MPIEMSES3D.git
cd MPIEMSES3D
make
```

## 4. 実行ファイルを各ケースへ配置する

```bash
cd ~/large0/Github/EMSES-tutorials
cp ~/large0/Github/MPIEMSES3D/bin/mpiemses3D dshield0/
cp ~/large0/Github/MPIEMSES3D/bin/mpiemses3D dshield1/
cp ~/large0/Github/MPIEMSES3D/bin/mpiemses3D dshield2/
```

`job.sh` は `plasma.toml` のみを実行入力として使います。legacy な `plasma.inp` / `plasma.preinp` は各ケースの `.old/` 配下に参照用として置いてあります。

## 5. `plasma.toml` を編集したら `emu apply` する

`dshield*` は `plasma.toml` が標準入力です。`[meta.physical]` や `[meta.unit_conversion]` を変更した場合は、投入前に変換を反映してください。

```bash
cd ~/large0/Github/EMSES-tutorials/dshield1
emu apply plasma.toml --dry-run
emu apply plasma.toml
```

## 6. `dshield0` を実行する

```bash
cd ~/large0/Github/EMSES-tutorials/dshield0
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
  ![plot](../imgs/phisp_2d_xy.png)

### Notebook 用の Python interpreter を設定する

```bash
cd ~/large0
/usr/bin/python3.11 -m venv .venv
~/large0/.venv/bin/python -m pip install -r ~/large0/Github/EMSES-tutorials/requirements.txt
```

1. VS Code で `Python: Select Interpreter` を開く
   ![select-interpreter](../imgs/select_interpreter.png)
2. `Enter Interpreter Path` を選ぶ
   ![enter-interpreter](../imgs/enter_interpreter_path.png)
3. `~/large0/.venv/bin/python` もしくは `/opt/system/app/intelpython/2024.2.0/bin/python` を指定する
   ![input-interpreter](../imgs/input_interpreter.png)

参考:

- [emout](https://github.com/Nkzono99/emout)
- [emout のサンプル notebook](https://nbviewer.org/github/Nkzono99/examples/blob/main/examples/emout/example.ipynb)

## 9. 条件を変えて試す

- `dshield0/plasma.toml` の `jobcon.nstep` を増やして、より長い時間発展を見てみる
- `dshield1` / `dshield2` も実行して違いを比べる
- `ds0` を `emout` で可視化するときは、必要に応じて `[[species]]` の `wp` を一時的に非ゼロへ変更する

旧 `advance/` の例は、`MPIEMSES3D` 側の [`parameter_examples`](https://github.com/CS12-Laboratory/MPIEMSES3D/tree/main/parameter_examples) を参照してください。

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
