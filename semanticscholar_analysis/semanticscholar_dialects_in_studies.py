import re
import requests
import pandas as pd
from collections import Counter


def main():
    ##################### Part I - Query the papers' titles and abstracts #####################

    # Specify the search term
    query = 'Arabizi|Arabish|Arabisi|"Franco Arabic"|"Franco Arab"'

    # Define the API endpoint URL
    url = "http://api.semanticscholar.org/graph/v1/paper/search/bulk"

    # Define the query parameters
    query_params = {
        "query": query,
        "fields": "title,url,publicationTypes,publicationDate,abstract,venue,fieldsOfStudy",
        "year": "",
    }

    response = requests.get(url, params=query_params).json()
    df = pd.DataFrame(response["data"])

    varieties = [
        "Egypt",
        "Leban",
        "Palestin",
        "Syria",
        "Jordan",
        "Sudan",
        "Saudi",
        "Oman",
        "Qatar",
        "Bahrain",
        "Yemen",
        "Maghreb",
        "Libya",
        "Tunisia",
        "Moroc",
        "Tunisia",
        "Algeria",
        "Mauritan",
    ]

    df["countries"] = df.apply(
        lambda row: sorted(
            set(
                [
                    v
                    for v in varieties
                    if re.findall(
                        rf"\b{v.lower()}",
                        str(row["abstract"]).lower() + " " + str(row["title"]).lower(),
                    )
                ]
            )
        ),
        axis=1,
    )

    # Note: 3 is a magic number based on inspecting the maximum number of countries mentioned in an abstract
    for i in range(0, 3):
        df[f"country_{i}"] = df["countries"].apply(lambda l: l[i] if len(l) > i else "")

    df[
        [
            "country_0",
            "country_1",
            "country_2",
            "title",
            "abstract",
            "url",
            "venue",
            "fieldsOfStudy",
            "publicationTypes",
            "publicationDate",
            "authors",
            "paperId",
            "openAccessPdf",
        ]
    ].T.to_excel("papers.xlsx", index=True)

    ##################### Part II - Generate the frequency of each country-level dialect #####################
    ann_df = pd.read_excel("papers_ann.xlsx").T.reset_index(drop=True)
    ann_df.columns = ann_df.iloc[0]
    ann_df = ann_df.iloc[1:]

    values = (
        ann_df["country_0"].dropna().tolist()
        + ann_df["country_1"].dropna().tolist()
        + ann_df["country_2"].dropna().tolist()
    )
    values_dict = dict(Counter(values))

    region_to_countries = {
        "Maghreb": ["Moroc", "Algeria", "Tunisia"],
        "Gulf": ["Saudi", "UAE", "Kuwait", "Oman"],
        "Levant": ["Jordan", "Leban", "Palestin"],
    }

    for region in region_to_countries.keys():
        v = values_dict[region]
        for c in region_to_countries[region]:
            values_dict[c] += v

    for k in Counter(values_dict).most_common():
        value, count = k
        print(f"{value} ({count}), ", end="")


if __name__ == "__main__":
    main()
