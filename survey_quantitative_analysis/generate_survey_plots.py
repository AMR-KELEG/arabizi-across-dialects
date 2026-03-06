import os
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", None)

import matplotlib.pyplot as plt
from survey_plots_utils import (
    generate_perception_hist,
    generate_usage_hist,
    generate_response_script_hist,
)

os.makedirs("paper_plots", exist_ok=True)
PLOT_HEIGHT = 1

df = pd.read_csv("../data/parsed_survey_responses.csv")

# Median response time
print("Median response time:", (df["Duration (in seconds)"] / 60).median(), "minutes")


# Findings:
# (1) Skewness of the diagrams
# (2) Skewness toward younger generations (< 35)
# (3) "Never" more common in Egypt than other countries
# (4) Impact of usage of Arabizi on perception?

countries_list = "Algerian, Egyptian, Lebanese, Moroccan, Tunisian, Sudanese, Palestinian, Qatari, Saudi, Syrian, Gulf, Iraqi, Jordanian".split(
    ", "
)

for countries in [countries_list[:5], countries_list[5:10], countries_list[10:]]:
    countries = countries[:5]

    cols = len(countries)
    rows = len(countries) // cols + int(len(countries) % cols != 0)
    fig, axes = plt.subplots(
        ncols=cols, nrows=rows, figsize=(6.3, 1.1 * rows), sharey=True
    )

    for country, ax in zip(countries, axes.flatten()):
        generate_perception_hist(
            df[df["Dialect (Country)"] == country],
            label=country,
            ax=ax,
            show_legend=False,
        )

    fig.tight_layout()
    if countries[0] == "Algerian":
        fig.savefig("paper_plots/perception_hist_single_row.pdf", bbox_inches="tight")
    elif countries[0] == "Sudanese":
        fig.savefig(
            "paper_plots/perception_hist_single_row_others.pdf", bbox_inches="tight"
        )
    else:
        fig.savefig(
            "paper_plots/perception_hist_single_row_others2.pdf", bbox_inches="tight"
        )


# Add a new category for those who never used Arabizi in the usage pattern column
df.loc[
    df["Used Arabizi"] == "No",
    "Usage of Arabizi now compared to year of starting to use mobile phones",
] = "Never used it"

df[df["Used Arabizi"] == "No"].groupby(["Dialect (Country)"]).apply(
    lambda gdf: gdf["Arabizi perception"].value_counts()
).reset_index()

# # Findings:
# # (1) People who stopped using Arabizi are more common in Egypt
# # (2) Usage difference between Egypt and Algeria, despite similarity in perception of Arabizi

for countries in [countries_list[:5], countries_list[5:10], countries_list[10:]]:
    cols = len(countries)
    rows = len(countries) // cols + int(len(countries) % cols != 0)
    fig, axes = plt.subplots(
        ncols=cols, nrows=rows, figsize=(6.3, 1.1 * rows), sharey=True
    )

    for country, ax in zip(countries, axes.flatten()):
        generate_usage_hist(
            df[df["Dialect (Country)"] == country], label=country, ax=ax
        )

    fig.tight_layout()
    if countries[0] == "Algerian":
        fig.savefig("paper_plots/usage_hist_single_row.pdf", bbox_inches="tight")
    elif countries[0] == "Sudanese":
        fig.savefig("paper_plots/usage_hist_single_row_others.pdf", bbox_inches="tight")
    else:
        fig.savefig(
            "paper_plots/usage_hist_single_row_others2.pdf", bbox_inches="tight"
        )


for countries in [countries_list[:5], countries_list[5:10], countries_list[10:]]:
    cols = 3
    rows = len(countries) // cols + int(len(countries) % cols != 0)
    fig, axes = plt.subplots(
        ncols=cols, nrows=rows, figsize=(6.3, 0.9 * rows), sharey=True
    )

    for country, ax in zip(
        countries,
        [axes.flatten()[i] for i in [0, 1, 3, 4, 5] if i < len(axes.flatten())],
    ):
        generate_response_script_hist(
            df[df["Dialect (Country)"] == country],
            question_script="Arabizi",
            label=country,
            ax=ax,
        )

    axes.flatten()[2].set_axis_off()

    fig.tight_layout()
    if countries[0] == "Algerian":
        fig.savefig(
            "paper_plots/response_Arabizi_hist_single_row.pdf", bbox_inches="tight"
        )
    elif countries[0] == "Sudanese":
        fig.savefig(
            "paper_plots/response_Arabizi_hist_single_row_others.pdf",
            bbox_inches="tight",
        )
    else:
        fig.savefig(
            "paper_plots/response_Arabizi_hist_single_row_others2.pdf",
            bbox_inches="tight",
        )


for countries in [countries_list[:5], countries_list[5:10], countries_list[10:]]:
    cols = 3
    rows = len(countries) // cols + int(len(countries) % cols != 0)
    fig, axes = plt.subplots(
        ncols=cols, nrows=rows, figsize=(6.3, 0.9 * rows), sharey=True
    )

    for country, ax in zip(
        countries,
        [axes.flatten()[i] for i in [0, 1, 3, 4, 5] if i < len(axes.flatten())],
    ):
        generate_response_script_hist(
            df[df["Dialect (Country)"] == country],
            question_script="Arabic script",
            label=country,
            ax=ax,
        )

    axes.flatten()[2].set_axis_off()

    fig.tight_layout()
    if countries[0] == "Algerian":
        fig.savefig(
            "paper_plots/response_Arabic_hist_single_row.pdf", bbox_inches="tight"
        )
    elif countries[0] == "Sudanese":
        fig.savefig(
            "paper_plots/response_Arabic_hist_single_row_others.pdf",
            bbox_inches="tight",
        )
    else:
        fig.savefig(
            "paper_plots/response_Arabic_hist_single_row_others2.pdf",
            bbox_inches="tight",
        )
