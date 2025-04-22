import math
from argparse import ArgumentParser
from pathlib import Path
from typing import List

import emout
import matplotlib.pyplot as plt
import numpy as np
from emout.utils import Group

# t軸をwpi*tで規格化(use_si=Trueのとき)
emout.Emout.name2unit["t"] = emout.data.wpit_unit


def parse_args():
    parser = ArgumentParser()

    parser.add_argument("dirs", nargs="*")
    parser.add_argument("--fontsize", "-fs", type=int, default=14)
    parser.add_argument("--zmin", type=int, default=-1)
    parser.add_argument("--zmax", type=int, default=-1)
    parser.add_argument("--comparable", "-c", action="store_true")
    parser.add_argument("--istep", "-i", type=int, default=-1)
    parser.add_argument("--append", "-ap", action="store_true")
    parser.add_argument("--datadir", "-d", default="data")
    parser.add_argument("--sort", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    plt.rcParams["font.size"] = args.fontsize
    plt.tight_layout()

    dirs = search_dirs(args.dirs)
    if args.sort:
        dirs = sorted(dirs)

    if args.append:
        append_directories = []
        if len(dirs) >= 2:
            append_directories = dirs[1:]
        data = emout.Emout(dirs[0], append_directories=append_directories)
        datas = [data]
    else:
        datas = [emout.Emout(d) for d in dirs]
    for data in datas:
        data: emout.Emout
        datadir = (data.directory / args.datadir)
        datadir.mkdir(exist_ok=True)
        (datadir/"gif").mkdir(exist_ok=True)
        
        names = (
            [f"nd{i}p" for i in range(1, data.inp.nspec + 1)]
            + [f"j{i}x" for i in range(1, data.inp.nspec + 1)]
            + [f"j{i}y" for i in range(1, data.inp.nspec + 1)]
            + [f"j{i}z" for i in range(1, data.inp.nspec + 1)]
            + ["phisp", "rho", "rhobk", "ex", "ey", "ez", "bx", "by", "bz"]
        )
        x_center = int(data.inp.nx // 2)
        y_center = int(data.inp.ny // 2)
        z_center = int(data.inp.nz // 2)
        for name in names:
            vals = getattr(data, name)

            # 1d plot
            vals[args.istep, z_center, y_center, :].plot(
                savefilename=datadir/f"{name}_1d_x.png"
            )
            vals[args.istep, z_center, :, x_center].plot(
                savefilename=datadir/f"{name}_1d_y.png"
            )
            vals[args.istep, :, y_center, x_center].plot(
                savefilename=datadir/f"{name}_1d_z.png"
            )

            # 2d map plot
            vals[args.istep, z_center, :, :].plot(
                mode="cmap+cont", savefilename=datadir/f"{name}_2d_xy.png"
            )
            vals[args.istep, :, y_center, :].plot(
                mode="cmap+cont", savefilename=datadir/f"{name}_2d_zx.png"
            )
            vals[args.istep, :, :, x_center].plot(
                mode="cmap+cont", savefilename=datadir/f"{name}_2d_yz.png"
            )

            # 1d Animation plot
            tslice = slice(None, None, math.ceil((data.inp.nstep//data.inp.ifdiag)/10))
            vals[tslice, z_center, y_center, :].gifplot(
                action="save", filename=datadir/"gif"/f"{name}_1d_x.gif"
            )
            vals[tslice, z_center, :, x_center].gifplot(
                action="save", filename=datadir/"gif"/f"{name}_1d_y.gif"
            )
            vals[tslice, :, y_center, x_center].gifplot(
                action="save", filename=datadir/"gif"/f"{name}_1d_z.gif"
            )

            # 2d map plot
            vals[tslice, z_center, :, :].gifplot(
                action="save", mode="cmap+cont", filename=datadir/"gif"/f"{name}_2d_xy.gif"
            )
            vals[tslice, :, y_center, :].gifplot(
                action="save", mode="cmap+cont", filename=datadir/"gif"/f"{name}_2d_zx.gif"
            )
            vals[tslice, :, :, x_center].gifplot(
                action="save", mode="cmap+cont", filename=datadir/"gif"/f"{name}_2d_yz.gif"
            )


def search_dirs(patterns):
    dirs: List[Path] = []
    for d in patterns:
        if Path(d) == Path("./"):
            dirs.append(Path("./"))
            continue
        dirs += Path("./").glob(d)

    for d in dirs:
        print("found:", d.resolve())

    return list(filter(lambda d: d.is_dir() and d.exists(), dirs))


if __name__ == "__main__":
    main()
