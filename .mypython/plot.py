import math
from argparse import ArgumentParser
from collections.abc import Callable
from pathlib import Path
from typing import List

import emout
import matplotlib.pyplot as plt
from emout.core.units import ndp_unit, none_unit, t_unit, wpit_unit


def tutorial_time_unit(out: emout.Emout):
    """Use wpi*t when available, and plain t for wp=0 cases such as dshield0."""
    if len(out.inp.wp) < 2 or out.inp.wp[1] == 0:
        return t_unit(out)
    return wpit_unit(out)


def tutorial_ndp_unit(out: emout.Emout):
    """Use raw grid density when wp=0 prevents conversion to /cc."""
    if not out.inp.wp or out.inp.wp[0] == 0:
        return none_unit(out)
    return ndp_unit(out)


emout.Emout.name2unit["t"] = tutorial_time_unit
emout.Emout.name2unit["nd[1-9]\\d*p"] = tutorial_ndp_unit


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
        nplots = 0
        for name in names:
            vals = get_diagnostic(data, name)
            if vals is None:
                continue

            # 1d plot
            nplots += save_plot(
                f"{name}_1d_x",
                lambda vals=vals, name=name: vals[args.istep, z_center, y_center, :].plot(
                    savefilename=datadir/f"{name}_1d_x.png"
                ),
            )
            nplots += save_plot(
                f"{name}_1d_y",
                lambda vals=vals, name=name: vals[args.istep, z_center, :, x_center].plot(
                    savefilename=datadir/f"{name}_1d_y.png"
                ),
            )
            nplots += save_plot(
                f"{name}_1d_z",
                lambda vals=vals, name=name: vals[args.istep, :, y_center, x_center].plot(
                    savefilename=datadir/f"{name}_1d_z.png"
                ),
            )

            # 2d map plot
            nplots += save_plot(
                f"{name}_2d_xy",
                lambda vals=vals, name=name: vals[args.istep, z_center, :, :].plot(
                    mode="cmap+cont", savefilename=datadir/f"{name}_2d_xy.png"
                ),
            )
            nplots += save_plot(
                f"{name}_2d_zx",
                lambda vals=vals, name=name: vals[args.istep, :, y_center, :].plot(
                    mode="cmap+cont", savefilename=datadir/f"{name}_2d_zx.png"
                ),
            )
            nplots += save_plot(
                f"{name}_2d_yz",
                lambda vals=vals, name=name: vals[args.istep, :, :, x_center].plot(
                    mode="cmap+cont", savefilename=datadir/f"{name}_2d_yz.png"
                ),
            )

            # 1d Animation plot
            tstep = max(1, math.ceil((data.inp.nstep // data.inp.ifdiag) / 10))
            tslice = slice(None, None, tstep)
            # vals[tslice, z_center, y_center, :].gifplot(
            #     action="save", filename=datadir/"gif"/f"{name}_1d_x.gif"
            # )
            # vals[tslice, z_center, :, x_center].gifplot(
            #     action="save", filename=datadir/"gif"/f"{name}_1d_y.gif"
            # )
            # vals[tslice, :, y_center, x_center].gifplot(
            #     action="save", filename=datadir/"gif"/f"{name}_1d_z.gif"
            # )

            # 2d map plot
            nplots += save_plot(
                f"{name}_2d_xy.gif",
                lambda vals=vals, name=name: vals[tslice, z_center, :, :].gifplot(
                    action="save", mode="cmap+cont", filename=datadir/"gif"/f"{name}_2d_xy.gif"
                ),
            )
            # vals[tslice, :, y_center, :].gifplot(
            #     action="save", mode="cmap+cont", filename=datadir/"gif"/f"{name}_2d_zx.gif"
            # )
            # vals[tslice, :, :, x_center].gifplot(
            #     action="save", mode="cmap+cont", filename=datadir/"gif"/f"{name}_2d_yz.gif"
            # )
        if nplots == 0:
            raise RuntimeError(f"no plots were generated for {data.directory}")
        print(f"generated {nplots} plot files under {datadir}")


def get_diagnostic(data: emout.Emout, name: str):
    try:
        return getattr(data, name)
    except Exception as exc:  # noqa: BLE001 - keep post-processing best-effort.
        print(f"[WARN] skip {name}: {exc}")
        return None


def save_plot(label: str, plotter: Callable[[], object]) -> int:
    try:
        plotter()
    except Exception as exc:  # noqa: BLE001 - one bad diagnostic should not stop all plots.
        print(f"[WARN] failed to plot {label}: {exc}")
        return 0
    return 1


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
