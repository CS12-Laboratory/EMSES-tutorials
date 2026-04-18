---
title: Quick Start
description: Step-by-step setup for running dshield* on Kyoto University's camphor supercomputer
---

Follow the steps below to get the `dshield*` tutorials running on Kyoto University's *camphor* supercomputer.

## 1. Connect to camphor from VS Code

- Launch VS Code and install the **Remote-SSH** extension

  ![remote-ssh](../../../assets/imgs/1.png)
- Log in to *camphor*

  ![login](../../../assets/imgs/2.png)
- Open a TERMINAL

  ![terminal](../../../assets/imgs/3.png)

## 2. Prepare your workspace and Python environment

Run the substeps below in order.

### 2-1. Create a workspace under `/LARGE1` and symlink it from `~/large1`

```bash
mkdir -p /LARGE1/gr20001/$USER
ln -s /LARGE1/gr20001/$USER ~/large1
```

:::note
`/LARGE0` was the previous default and is still usable, but it has recently been filling up and occasionally cannot accept new output files, so we now recommend `/LARGE1` for new work. If you stick with `/LARGE0`, replace the paths above with `/LARGE0/gr20001/$USER` and `~/large0`.
:::

### 2-2. Create a Python 3.12 venv under `$HOME`

```bash
/usr/bin/python3.12 -m venv $HOME/.venv
```

### 2-3. Activate the venv

```bash
source $HOME/.venv/bin/activate
```

If you want the venv to be activated automatically on every login, append the line below to `~/.bashrc` (recommended for now so that batch jobs can also find `mypython` and other commands):

```bash
echo 'source $HOME/.venv/bin/activate' >> ~/.bashrc
```

:::note
Once you no longer need this venv, remove the line you appended above from `~/.bashrc`.
:::

### 2-4. Clone the repository

```bash
mkdir -p ~/large1/Github
cd ~/large1/Github
git clone https://github.com/CS12-Laboratory/EMSES-tutorials.git
```

### 2-5. Install the dependencies into the venv

```bash
cd ~/large1/Github/EMSES-tutorials
pip install -r requirements.txt
```

`requirements.txt` also pulls in the `MPIEMSES3D`-side helpers (`emu`, `inp2toml`, `mysbatch`, `latestjob`, ...), so they all land inside the venv.

### 2-6. Open the repository in VS Code

```bash
code --reuse-window ~/large1/Github/EMSES-tutorials
```

## 3. How to install MPIEMSES3D

The recommended path is to install via pip. It builds with OpenMP enabled and also pulls in `mpiemses3d-tools` (`emu`, `inp2toml`, `emses-cp`, `mysbatch`, `latestjob`, ...) as a dependency.

```bash
MPIEMSES3D_OPENMP=1 pip install git+https://github.com/CS12-Laboratory/MPIEMSES3D.git@v4.10.0
```

<details>
<summary>For developers who edit the code (build with make)</summary>

If you want to modify the source directly, clone the repository and build with `make`.

```bash
cd ~/large1/Github
git clone https://github.com/CS12-Laboratory/MPIEMSES3D.git
cd MPIEMSES3D
make
```

This path does not install the surrounding helpers (`emu` / `inp2toml` / `emses-cp` / `mysbatch` / `latestjob`, ...), so install `mpiemses3d-tools` separately with pip.

```bash
pip install mpiemses3d-tools
```

(When you install MPIEMSES3D itself via pip, this package is pulled in automatically as a dependency.)

</details>

## 4. Copy the executable into each case

```bash
cd ~/large1/Github/EMSES-tutorials
cp ~/large1/Github/MPIEMSES3D/bin/mpiemses3D dshield0/
cp ~/large1/Github/MPIEMSES3D/bin/mpiemses3D dshield1/
cp ~/large1/Github/MPIEMSES3D/bin/mpiemses3D dshield2/
```

`job.sh` uses `plasma.toml` as the only runtime input. Legacy `plasma.inp` / `plasma.preinp` files are kept under each case's `.old/` directory as archived references.

## 5. Run `emu apply` after editing `plasma.toml`

The `dshield*` tutorials use `plasma.toml` as the primary input file. If you edit `[meta.physical]` or `[meta.unit_conversion]`, apply the conversion before submitting the job.

```bash
cd ~/large1/Github/EMSES-tutorials/dshield1
emu apply plasma.toml --dry-run
emu apply plasma.toml
```

## 6. Run `dshield0`

```bash
cd ~/large1/Github/EMSES-tutorials/dshield0
mysbatch job.sh
```

In this repository, `mysbatch` is expected to use `[mpi].nodes` from `plasma.toml`. The legacy inputs remain only in `.old/` as reference files and are not part of the submission flow.

## 7. Monitor the job

```bash
qs
squeue
qgroup
latestjob
```

- Cancel a job: `scancel <job-id>`
- Standard output: `stdout.****.log`
- Standard error: `stderr.****.log`

## 8. Visualize the results

- After the batch run, `.mypython/plot.py` generates files such as `data/*.png` and `data/gif/*.gif`.
- For notebook-based visualization, open `dshield0/plot_example.ipynb`.

  Example: `phisp_2d_xy.png`

  ![plot](../../../assets/imgs/phisp_2d_xy.png)

### Set a Python interpreter for notebooks

You can reuse `~/.venv` created in Step 2.

1. Open `Python: Select Interpreter` in VS Code

   ![select-interpreter](../../../assets/imgs/select_interpreter.png)
2. Choose `Enter Interpreter Path`

   ![enter-interpreter](../../../assets/imgs/enter_interpreter_path.png)
3. Select `~/.venv/bin/python`

   ![input-interpreter](../../../assets/imgs/input_interpreter.png)

References:

- [emout](https://github.com/Nkzono99/emout)
- [Sample notebook for emout](https://nbviewer.org/github/Nkzono99/examples/blob/main/examples/emout/example.ipynb)

## 9. Try different conditions

- Increase `jobcon.nstep` in `dshield0/plasma.toml` to watch a longer evolution
- Run `dshield1` and `dshield2` and compare the differences
- When visualizing `ds0` with `emout`, temporarily set `[[species]].wp` to a nonzero value if needed

For the former `advance/` examples, see [`cookbook`](https://github.com/CS12-Laboratory/MPIEMSES3D/tree/main/cookbook) in the `MPIEMSES3D` repository.

## 10. Think about the physics

- `ds0`: a negative charge in vacuum
- `ds1`: plasma with density `10^7 /cm^3` and electron temperature `3 eV`
- `ds2`: the same setup as `ds1`, but with 1/16 density

Questions to check:

- How does the potential distribution change around the charged object?
- How do electrons and ions respond?
- What changes mainly when you vary density or temperature?

## References

- [Kyoto University supercomputer manual (restricted)](http://web.kudpc.kyoto-u.ac.jp/manual-new/ja)
- [Kobe University supercomputer manual](http://www.eccse.kobe-u.ac.jp/pi-computer/)
- [MPIEMSES3D Parameters](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Parameters.en.md)
- [MPIEMSES3D Customization](https://github.com/CS12-Laboratory/MPIEMSES3D/blob/main/docs/Customization.en.md)
