from io import BytesIO
import os 
import string

import pandas as pd 
import numpy as np
import paat
import seaborn as sns
import matplotlib.pyplot as plt 
from matplotlib.patches import Rectangle, Patch
import matplotlib.dates as mdates
from matplotlib.colors import to_rgba
from PIL import Image


out_path_week = "data/example_week.csv.tar.gz"
out_path_day = "data/example_day.csv.tar.gz"

# Load produced files
agg, sample_freq = pd.read_csv(out_path_week, compression='gzip'), 100
agg["Timestamp"] = pd.to_datetime(agg["Timestamp"])
agg = agg.set_index("Timestamp")

day = pd.read_csv(out_path_day, compression='gzip')
day["Timestamp"] = pd.to_datetime(day["Timestamp"])
day = day.set_index("Timestamp")

# Caclulcate daily stats
agg["Fraction"] = 1
week = (agg.groupby([agg.index.date, "Activity"])["Fraction"].sum() / (24 * 60 * 60)).reset_index(level=1)

avg = week.groupby("Activity").mean()
avg = avg / avg.sum()
avg = avg.reset_index()
avg.index = ["Ø"] * len(avg)
week = pd.concat([week, avg])

COLOR = {
    'Non Wear Time': "grey",
    'Time in bed': "blue",
    'SB': "green",
    'LPA': "yellow",
    'MVPA': "red"
}

label_fontsize = 14
tick_fontsize = 13
legend_fontsize = 12

plot_presentation_plots = False 

if plot_presentation_plots:
    plot_without_TiB = [False, True]
else:
    plot_without_TiB = [False]

for without_TiB in plot_without_TiB:
    if without_TiB:
        COLOR = {key: value for key, value in COLOR.items() if key != "Time in bed"}
        day.loc[day["Activity"] == "Time in bed", "Activity"] = "SB"
        week.loc[week["Activity"] == "Time in bed", "Activity"] = "SB"
        week = week.groupby([week.index, "Activity"]).sum().reset_index(level=1)
        suffix = "_wo_TiB"
    else:
        suffix = ""

    if plot_presentation_plots:
        subplots = range(4)
    else:
        subplots = [3]

    for ii in subplots:

        fig = plt.figure(figsize=(12,5))
        gs = fig.add_gridspec(2,2,width_ratios=[2,1])
        axes = [
            fig.add_subplot(gs[0,0]),
            fig.add_subplot(gs[1,0]),
            fig.add_subplot(gs[:,1])
        ]
        # fig.set_facecolor(to_rgba('white', alpha=0))

        ax = axes[0]
        ax.text(-0.1, 1.025, " ", transform=ax.transAxes, 
            size=20, weight='bold')

        ax = axes[1]
        ymin, ymax = ax.get_ylim()
        handles = [Patch(color=value, label=key, alpha=.4) for key, value in COLOR.items()]
        legend = ax.legend(
            handles=handles,
            loc='upper center',
            bbox_to_anchor=(0.8, -.35 * ymax),
            fancybox=False,
            shadow=False,
            ncol=5,
            fontsize=legend_fontsize
        )
        legend.set_visible(False)
        ax.text(0.8, -.55 * ymax, " ", transform=ax.transAxes, 
                size=20, weight='bold') 


        """
        Plot 1
        """
        ax = axes[0]
        ax = sns.lineplot(data=day[['X', 'Y', 'Z']], ax=ax, legend=True)
        ax.set_ylabel("Acceleration [g]", fontsize=label_fontsize)
        ax.legend(fontsize=legend_fontsize, loc="lower right")
        ax.tick_params(labelsize=tick_fontsize)
        #ax.set_title("Example Day")
        #ax.set_xticks([])
        ax.set_facecolor("white")


        """
        Plot 2
        """
        if ii >= 1:
            ax = axes[1]
            ax = sns.lineplot(data=day['ENMO'], ax=ax, legend=True)
            ax.set_ylabel("ENMO [g]", fontsize=label_fontsize)
            fig.align_ylabels(axes[:1])
            
            if ii >= 2:
                # Add background
                ymin, ymax = ax.get_ylim()
                height = ymax - ymin
                for jj, row in day.iterrows():
                    ax.add_patch(
                        Rectangle(
                            (jj, ymin),
                            pd.Timedelta("1s"),
                            height,
                            alpha=.3,
                            facecolor=COLOR[row["Activity"]]
                        )
                    )
                legend.set_visible(True)

            ax.sharex(axes[0])
            ax.set_facecolor("white")
        else:
            axes[1].axis('off')
            

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.set_xlabel("Time", fontsize=label_fontsize)
        ax.tick_params(labelsize=tick_fontsize)


        """
        Plot 3
        """
        if ii >= 3:
            ax = axes[2]

            weight_count = week.reset_index().pivot(index="index", columns="Activity", values="Fraction")
            weight_count = weight_count.reindex(columns=COLOR.keys()).fillna(0)
            weight_count = weight_count[COLOR.keys()]
            weight_count = weight_count.reset_index(drop=True)
            weight_count.index = [str(xx) for xx in range(len(weight_count) - 1)] + ["Ø"]
            #weight_count = weight_count.cumsum(axis=1)

            bottom = np.zeros(len(weight_count))
            for column in weight_count:
                p = ax.bar(weight_count.index, weight_count[column], width=.6, color=COLOR[column], bottom=bottom, alpha=.5)
                bottom += weight_count[column]

            #ax.set_title("Daily Summaries")
            ax.set_xlabel("Day", fontsize=label_fontsize)
            ax.set_ylabel("Fraction of the day", fontsize=label_fontsize)
            ax.set_ylim(0,1)
            ax.grid(axis="y")
            ax.set_facecolor("white")
            ax.tick_params(labelsize=tick_fontsize)
            fig.align_xlabels(axes[1:])
        else:
            axes[2].axis('off')


        fig.align_ylabels(axes[:2])
        plt.tight_layout()
        plt.subplots_adjust(wspace=.2, hspace=0)

        if plot_presentation_plots:
            plt.savefig(
                f'img/paat_presentation_{ii}{suffix}.png', 
                dpi=600)

        if (ii == 3) & (not without_TiB):
            ax = axes[0]
            ax.text(-0.0975, 1.025, "A", transform=ax.transAxes, 
                    size=20, weight='bold')
            ax = axes[2]
            ax.text(-0.193, 1.025, "B", transform=ax.transAxes, 
                    size=20, weight='bold')
                    
            plt.savefig(
                'img/paper_fig1.png', 
                dpi=600)

            plot = BytesIO()
            plt.savefig(
                plot, 
                format='png', 
            )

            png = Image.open(plot)

            # (3) save as TIFF
            png.save('img/paper_fig1.tiff')
            plot.close()
