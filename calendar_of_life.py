import bisect
import datetime
import os
from collections import defaultdict
from typing import Optional

import imageio
import matplotlib.pyplot as plt
import numpy as np
from apng import APNG
from pygifsicle import optimize


def create_calendar(
    dark_mode: bool = True,
    fname: str = "calendar-of-life-dark.png",
    current_week_alpha: Optional[float] = None,
    show: bool = True,
):
    if dark_mode:
        plt.style.use("dark_background")
        face = "k"
        edge = "w"
    else:
        plt.rcParams.update(plt.rcParamsDefault)
        face = "w"
        edge = "k"

    h, w = 13, 9
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_axis_off()
    fig.suptitle("Calendar of life", y=0.89)
    birthday = datetime.date(1990, 12, 28)
    today = datetime.date.today()
    life = [
        ("born", birthday, None),
        ("early childhood", birthday + datetime.timedelta(days=4 * 365), "C0"),
        ("school", datetime.date(2003, 8, 18), "C1"),
        ("high school", datetime.date(2009, 9, 1), "C2"),
        ("university", datetime.date(2015, 8, 1), "C3"),
        ("travel", datetime.date(2016, 2, 1), "C8"),
        ("phd", datetime.date(2020, 2, 1), "C6"),
        ("work", today, "C4"),
    ]

    stages = [key for key, _, _ in life]
    weeks_of_life = [round((date - birthday).days / 7) for _, date, _ in life]
    weeks_of_life_past = np.cumsum(np.diff(weeks_of_life))

    data = defaultdict(list)
    colors = {stage: color for stage, _, color in life[1:]}
    colors["future"] = face
    week_num = 0
    weeks = np.linspace(0, h, 52)
    years = np.linspace(w, 0, 80)
    for i, year in enumerate(years):
        for week in weeks:
            week_num += 1
            index = bisect.bisect_left(weeks_of_life_past, week_num) + 1
            if index == len(weeks_of_life_past) + 1:
                stage = "future"
            else:
                stage = stages[index]
            data[stage].append((week, year))

    for k, v in data.items():
        ax.scatter(*zip(*v), edgecolors=edge, facecolor=colors[k], label=k)

    if current_week_alpha is not None:
        current_week = data["future"].pop(0)
        ax.scatter(
            *current_week,
            edgecolors=edge,
            facecolor="white",
            label="now",
            alpha=current_week_alpha,
        )

    for i, year in enumerate(years):
        if i % 10 == 0 and i > 0:
            ax.text(
                -0.2,
                year,
                f"{i}y",
                horizontalalignment="right",
                verticalalignment="center",
                fontsize=9,
            )

    plt.legend()
    plt.savefig(fname, dpi=300)
    if show:
        plt.show()


def main():
    create_calendar(dark_mode=True, fname="calendar-of-life-dark.png", show=False)
    create_calendar(dark_mode=False, fname="calendar-of-life.png", show=False)

    # Create animation
    alphas = np.linspace(0, 1, 6)
    fnames = []
    for alpha in alphas:
        fname = f"alpha-{alpha}.png"
        create_calendar(
            dark_mode=True, current_week_alpha=alpha, fname=fname, show=False
        )
        fnames.append(fname)
    fnames += fnames[::-1]

    ## Saving images
    fname_animated = "calendar-of-life-dark-animated"
    # Save animated png
    im = APNG()
    for fname in fnames:
        im.append_file(fname, delay=50)
    im.save(f"{fname_animated}.png")

    # Save gif
    images = [imageio.imread(fname) for fname in fnames]
    imageio.mimsave(f"{fname_animated}.gif", images)
    optimize(f"{fname_animated}.gif")

    # Cleanup
    for fname in fnames[: len(alphas)]:
        os.unlink(fname)


if __name__ == "__main__":
    main()
