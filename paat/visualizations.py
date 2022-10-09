import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
import seaborn as sns

from .features import calculate_enmo

COLOR = {'Non Wear Time': "white", 'Time in bed': "blue", 'SB': "green", 'LPA': "yellow", 'MVPA': "red"}


def visualize(data, show_date=False, file_path=None):

    data["ENMO"] = calculate_enmo(data).copy()
    data = data.resample("1min").apply({"X": "mean", "Y": "mean", "Z": "mean", "ENMO": "mean", "Activity": lambda x: x.value_counts().idxmax()})

    n_days = len(data.groupby(data.index.day))
    ymax = data["ENMO"].max() * 1.05

    fig = plt.figure(figsize=(10, n_days * 2))
    axes = fig.subplots(n_days, 1)

    for ii, (_, day) in enumerate(data.groupby(data.index.day)):

        day["Time"] = np.arange(len(day))

        ax = axes[ii]

        ax = sns.lineplot(x="Time", y="ENMO", data=day, color="black", linewidth=.75, ax=ax)
        ax.set_ylabel("ENMO", fontsize=14)

        ticks, labels = list(zip(*[(tick, f"{tick // 60:0>2}:{tick % 60:0>2}") for tick in day["Time"] if (tick + 60) % 120 == 0]))
        ax.set_xticks(ticks)

        ax.set_ylim((0, ymax))

        if show_date:
            ax.set_title(day.index[0].strftime('%d.%m.%Y'))

        ymin, ymax = ax.get_ylim()
        height = ymax - ymin

        for _, row in day.iterrows():
            ax.add_patch(Rectangle((row["Time"], ymin), 1, height, alpha=.1, facecolor=COLOR[row["Activity"]]))

        if ii == n_days - 1:
            ax.set_xticklabels(labels)
            ax.set_xlabel("Time", fontsize=14)

            fig.subplots_adjust(bottom=0.5, wspace=0.33)
            handles = [Patch(color=value, label=key, alpha=.1) for key, value in COLOR.items()]
            ax.legend(handles=handles, loc='upper center',
                      bbox_to_anchor=(0.5, -0.4), fancybox=False, shadow=False, ncol=5)
        else:
            ax.set_xticklabels("")
            ax.set_xlabel("")

    plt.tight_layout()

    if file_path:
        plt.savefig(file_path)
    else:
        plt.show()
