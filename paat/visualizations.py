import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
import seaborn as sns

from .features import calculate_enmo

COLOR = {'Non Wear Time': "grey", 'Time in bed': "blue", 'SB': "green", 'LPA': "yellow", 'MVPA': "red"}


def visualize(data, show_date=False, title=None, file_path=None):

    data["ENMO"] = calculate_enmo(data).copy()
    data = data.resample("1min").apply({"X": "mean", "Y": "mean", "Z": "mean", "ENMO": "mean", "Activity": lambda x: x.value_counts().idxmax()})

    n_days = len(data.groupby(data.index.day))
    ymax = data["ENMO"].max() * 1.05
    min_per_day = 1440

    fig = plt.figure(figsize=(8.27, 11.69)) #figsize=(10, n_days * 3))
    axes = fig.subplots(n_days, 1, sharex=True)
    plt.subplots_adjust(hspace=.3)

    if title:
        fig.suptitle(title, fontsize=14)

    for ii, (_, day) in enumerate(data.groupby(data.index.day)):

        offset = (day.index[0] - pd.Timestamp(day.index[0].date())).total_seconds() // 60
        day["Time"] = np.arange(offset, offset + len(day))

        ax = axes[ii]

        if show_date:
            ax.set_title(day.index[0].strftime('%A, %d.%m.%Y'), fontsize=12)

        ax = sns.lineplot(x="Time", y="ENMO", data=day, color="black", linewidth=.75, ax=ax)
        ax.set_ylabel("ENMO", fontsize=10)
        ax.set_ylim((0, ymax))
        ax.set_xlim((0, min_per_day))

        ymin, ymax = ax.get_ylim()
        height = ymax - ymin

        # Add background
        for _, row in day.iterrows():
            ax.add_patch(Rectangle((row["Time"], ymin), 1, height, alpha=.1, facecolor=COLOR[row["Activity"]]))

        ticks, labels = list(zip(*[(tick, f"{tick // 60:0>2}:{tick % 60:0>2}") for tick in range(min_per_day) if (tick + 60) % 120 == 0]))
        ax.set_xticks(ticks)
        ax.set_xticklabels("")
        ax.set_xlabel("")

    ax.set_xticklabels(labels)
    ax.set_xlabel("Time", fontsize=10)

    # Add legend to last plot
    #ax = axes[-1]
    handles = [Patch(color=value, label=key, alpha=.1) for key, value in COLOR.items()]
    ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -.9 * ymax), fancybox=False, shadow=False, ncol=5)
    #ax.set_axis_off()

    if file_path:
        plt.savefig(file_path, dpi=300)
    else:
        plt.show()
