import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np

# Set the font of the general labels to 7.
# Note: This generally works for my *CL papers,
# for which the default caption font size is 10.
font = {"size": 7}
matplotlib.rc("font", **font)
# plt.rc('text', usetex=True)  # Comment out if LaTeX is not installed

# Remove some of the sides of the plot's frame
matplotlib.rcParams["axes.spines.left"] = True
matplotlib.rcParams["axes.spines.right"] = False
matplotlib.rcParams["axes.spines.top"] = False
matplotlib.rcParams["axes.spines.bottom"] = True

DARK_MODE = False
BACKGROUND_COLOR = "#1E1332" if DARK_MODE else "white"
FONT_COLOR = "white" if DARK_MODE else "black"

PURPLE_COLOR = "#762a83"
ORANGE_COLOR = "#ff4d00"
PLOT_COLOR = PURPLE_COLOR if not DARK_MODE else ORANGE_COLOR
matplotlib.rcParams["axes.facecolor"] = BACKGROUND_COLOR

# Load the PuOr colormap
puor_cmap = cm.get_cmap("PuOr")


def generate_perception_hist(
    sub_df, label, use_log_scale=False, ax=None, show_legend=True
):
    stats = sub_df["Arabizi perception"].value_counts().to_dict()

    if not ax:
        plt.figure(figsize=(6.3 / 2, 1))
        ax = plt.gca()

    levels = [
        "should never be used.",
        "is useful/needed in very limited contexts.",
        "is as useful for typing as the Arabic script.",
        "is more preferable for typing than the Arabic script.",
        "is the only way I use for typing Arabic words.",
    ]
    levels_labels = ["never\n", "\nlimit.", "same\n", "\nmore", "only\n"]

    if show_legend:
        levels = levels + ["N\A"]
        levels_labels = levels_labels + [""]

    ticks = [_ for _ in range(len(levels))]

    age_groups = ["<18-24", "25-34", "35-44", "45-54", "55+"] + ["Prefer not to say"]

    bottom = np.array([0 for _ in range(len(levels))])

    for i, age_group in enumerate(age_groups):
        if age_group == "<18-24":
            age_group_levels = np.array(
                [
                    sub_df[
                        (sub_df["Age group"].isin(["Under 18", "18-24"]))
                        & (sub_df["Arabizi perception"] == level)
                    ].shape[0]
                    for level in levels
                ]
            )
        elif age_group == "55+":
            age_group_levels = np.array(
                [
                    sub_df[
                        (sub_df["Age group"].isin(["55-64", "65+"]))
                        & (sub_df["Arabizi perception"] == level)
                    ].shape[0]
                    for level in levels
                ]
            )
        else:
            age_group_levels = np.array(
                [
                    sub_df[
                        (sub_df["Age group"] == age_group)
                        & (sub_df["Arabizi perception"] == level)
                    ].shape[0]
                    for level in levels
                ]
            )

        bars = ax.bar(
            x=ticks,
            height=age_group_levels,
            bottom=bottom,
            color=puor_cmap(i / (len(age_groups) - 1)),
            log=use_log_scale,
            label=f"{age_group}: {sum(age_group_levels) if sum(age_group_levels) else '-'}",
        )

        # Update the bottom values for the following group
        bottom = bottom + age_group_levels

    for bar, height in zip(bars, bottom):
        if height == 0:
            continue

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.5,
            f"{height}",
            color=FONT_COLOR,
            fontsize=6,
            ha="center",
        )

    if show_legend:
        ax.plot(ticks[:-1], bottom[:-1], "grey", "--", alpha=0.4)
    else:
        ax.plot(ticks, bottom, "grey", "--", alpha=0.4)

    ax.set_xticks(ticks, levels_labels, rotation=0, fontsize=6)
    y_labels = ax.get_yticks()
    ax.set_yticks(y_labels, [int(l) for l in ax.get_yticks()], fontsize=7)

    ax.set_ylabel("Num. resp.", color=FONT_COLOR, fontsize=7)

    if show_legend:
        legend_cells = ax.legend(
            frameon=False,
            title=f"{label} ({sum(bottom)})",
            title_fontsize=7,
            loc="right",
            bbox_to_anchor=(1.25, 0.6),
            # loc="best",
            handlelength=1,
            handleheight=1,
            fontsize=5.5,
        )
    else:
        ax.set_title(f"{label} ({sum(bottom)})", fontsize=6, y=1.1)

    plt.setp(ax.get_xticklines()[-1], visible=False)

    return ax


def generate_usage_hist(sub_df, label, use_log_scale=False, ax=None, show_legend=False):
    column_name = (
        "Usage of Arabizi now compared to year of starting to use mobile phones"
    )
    stats = sub_df[column_name].value_counts().to_dict()

    if not ax:
        plt.figure(figsize=(6.3 / 2, 1))
        ax = plt.gca()

    levels = [
        "Never used it",
        "I stopped using Arabizi",
        "Much less now compared to when I started texting",
        "About the same",
        "Somewhat less now compared to when I started texting",
        "Somewhat more now compared to when I started texting",
        "Much more now compared to when I started texting",
    ]

    levels_labels = ["never\n", "\nstop", "<<\n", "\n<", "same\n", "\n>", ">>\n"]
    ticks = [_ for _ in range(len(levels))]

    heights = [stats.get(l, 0) for l in levels]

    bars1 = ax.bar(
        x=ticks[:2], height=heights[:2], color=puor_cmap(0), log=use_log_scale
    )
    bars2 = ax.bar(
        x=ticks[2:4], height=heights[2:4], color=puor_cmap(0.25), log=use_log_scale
    )
    bars3 = ax.bar(
        x=[ticks[4]], height=[heights[4]], color=puor_cmap(0.55), log=use_log_scale
    )
    bars4 = ax.bar(
        x=ticks[5:], height=heights[5:], color=puor_cmap(0.9), log=use_log_scale
    )

    for bar in bars1 + bars2 + bars3 + bars4:
        if bar.get_height() == 0:
            continue

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{bar.get_height()}",
            color=FONT_COLOR,
            fontsize=6,
            ha="center",
        )

    ax.set_xticks(ticks, levels_labels, rotation=0, fontsize=6)
    y_labels = ax.get_yticks()
    ax.set_yticks([y_labels[0]], [[int(l) for l in ax.get_yticks()][0]], fontsize=7)

    ax.set_ylabel("Num. resp.", color=FONT_COLOR, fontsize=7)

    if show_legend:
        legend_cells = ax.legend(
            frameon=False,
            title=f"{label} ({sum(heights)})",
            title_fontsize=7,
            loc="right",
            bbox_to_anchor=(1.25, 0.6),
            # loc="best",
            handlelength=1,
            handleheight=1,
            fontsize=5.5,
        )
    else:
        ax.set_title(f"{label} ({sum(heights)})", fontsize=6, y=1.1)

    return ax


def generate_response_script_hist(sub_df, label, question_script, ax=None):

    assert question_script in ["Arabizi", "Arabic script"]
    sub_df = sub_df.copy(deep=True)
    sub_df[f"Script used on responding to {question_script}"] = sub_df[
        f"Script used on responding to {question_script}"
    ].apply(
        lambda r: (
            r if r == "Arabizi" else ("Arabic" if r == "Arabic script" else "Others")
        )
    )

    stats = (
        sub_df[
            ["Arabizi perception", f"Script used on responding to {question_script}"]
        ]
        .value_counts()
        .to_dict()
    )

    total_responses = sum(stats.values())

    if not ax:
        plt.figure(figsize=(6.3 / 2, 1))
        ax = plt.gca()

    levels = [
        "should never be used.",
        "is useful/needed in very limited contexts.",
        "is as useful for typing as the Arabic script.",
        "is more preferable for typing than the Arabic script.",
        "is the only way I use for typing Arabic words.",
        "N\A",
    ]

    levels_labels = ["never\n", "\nlimit.", "same\n", "\nmore", "only\n", ""]
    ticks = [_ for _ in range(len(levels))]
    print(ticks)

    for level_index, (level, level_label) in enumerate(zip(levels, levels_labels)):
        for i, (script, color) in enumerate(
            zip(
                ["Arabizi", "Arabic", "Others"],
                [puor_cmap(0.9), puor_cmap(0.25), puor_cmap(0.65)],
            )
        ):
            height = stats.get((level, script), 0)

            bar = ax.bar(
                ticks[levels.index(level)] + 0.1 + (i / 4),
                width=(1 / 4),
                height=height,
                align="edge",
                color=color,
                label=script if level == levels[0] else "",
            )[0]

            if bar.get_height():
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 1,
                    f"{bar.get_height()}",
                    color=FONT_COLOR,
                    fontsize=6,
                    ha="center",
                )

        if level != "N\A":
            ax.plot(
                [level_index + 1, level_index + 1],
                [0, max(stats.values())],
                color="k",
                linestyle="--",
                linewidth=0.5,
                alpha=0.5,
            )

    ax.set_xticks([t + 0.5 for t in ticks])
    ax.set_xticklabels(levels_labels)
    ax.set_ylabel("Num. resp.")
    ax.legend(
        title=f"{label} ({total_responses})",
        frameon=False,
        title_fontsize=7,
        loc="right",
        bbox_to_anchor=(1.25, 0.6),
        handlelength=1,
        handleheight=1,
        fontsize=5.5,
    )

    return ax
