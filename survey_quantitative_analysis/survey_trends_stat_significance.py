import os

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns

import numpy as np
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests

# Set the font of the general labels to 7.
# Note: This generally works for my *CL papers,
# for which the default caption font size is 10.
font = {"size": 8}
matplotlib.rc("font", **font)

arabizi_perception = {
    "Algeria": [2, 14, 5, 1, 0],
    "Egypt": [6, 22, 5, 0, 0],
    "Lebanon": [1, 4, 2, 6, 2],
    "Morocco": [2, 12, 4, 7, 2],
    "Tunisia": [1, 13, 9, 14, 4],
}

arabizi_usage = {
    "Algeria": [2, 1, 1, 7, 6, 2, 5],
    "Egypt": [8, 10, 6, 2, 4, 3, 0],
    "Lebanon": [1, 0, 0, 6, 4, 1, 4],
    "Morocco": [3, 1, 4, 9, 1, 5, 4],
    "Tunisia": [9, 0, 3, 14, 5, 5, 6],
}

COUNTRIES = sorted(arabizi_usage.keys())

cmap = plt.get_cmap("Reds")
cmap.set_under("#D21F3C")
cmap.set_over("white")

for variable, plot_title in zip(
    [arabizi_perception, arabizi_usage], ["perception", "usage"]
):
    p_values = []
    mask = []
    for c1 in COUNTRIES:
        p_values.append([])
        mask.append([])
        for c2 in COUNTRIES:
            if c1 == c2:
                p_values[-1].append(1)
                mask[-1].append(True)
                continue
            table = [variable[c1], variable[c2]]
            p_value = fisher_exact(table).pvalue
            p_values[-1].append(round(p_value, 3))
            mask[-1].append(False)

    p_values = np.array(p_values)
    pvals = []
    for i in range(len(COUNTRIES)):
        for j in range(len(COUNTRIES)):
            p_values[i][j] = p_values[j][i]
            if i < j:
                pvals.append(p_values[i][j])

    assert len(pvals) == 10

    # FDR BH
    rejected, p_adjusted, alphacSidak, alphacBonf = multipletests(
        pvals, method="fdr_bh"
    )

    v_i = 0
    for i in range(len(COUNTRIES)):
        for j in range(len(COUNTRIES)):
            p_values[i][j] = p_values[j][i]
            if i < j:
                p_values[i][j] = round(p_adjusted[v_i], 3)
                p_values[j][i] = round(p_adjusted[v_i], 3)
                v_i += 1

    assert v_i == len(pvals)

    print(pvals)
    print("Rejected:", rejected)
    print("Adjusted P-Values:", p_adjusted)
    print("Alpha-C Sidak:", alphacSidak)
    print("Alpha-C Bonferroni:", alphacBonf)
    print("Significant comparisons after FDR correction:", rejected.sum())

    plt.figure(figsize=(6.3 / 2, 6.3 / 2.5))
    sns.heatmap(
        p_values,
        mask=np.array(mask),
        annot=True,
        cmap=cmap,
        vmin=0.05 - 1e-5,
        vmax=0.05,
        cbar=False,
        square=True,
        xticklabels=COUNTRIES,
        yticklabels=COUNTRIES,
        linewidths=0.01,
        linecolor="black",
    )
    plt.gca().set_facecolor("grey")
    plt.tight_layout()
    os.makedirs("paper_plots", exist_ok=True)
    print("Generating " + f"'paper_plots/{plot_title}_p_value.pdf'")
    plt.savefig(f"paper_plots/{plot_title}_p_value.pdf", bbox_inches="tight")
