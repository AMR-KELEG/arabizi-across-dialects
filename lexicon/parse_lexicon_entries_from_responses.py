import os
import re
import pandas as pd
from alignment_utils import align_word

for directory in ["../data/lexicon", "../data/lexicon_review"]:
    os.makedirs(directory, exist_ok=True)

WORDS_NORMALIZATION = {
    # Algeria
    "Bnadem, Insan": "Insan",
    "bera/barra": "bera / barra",
    "Bezaf or Bzf": "Bezaf / Bzf",
    "Blakar / plakar": "Blakar / plakar",
    "sabah or saba7": "sabah / saba7",
    "5ouk / khouk": "5ouk / khouk",
    "8adak / hadak": "8adak / hadak",
    "Fer7a / ferha": "Fer7a / ferha",
    "Crava6a / cravata": "Crava6a / cravata",
    "9osbor / kosbor": "9osbor / kosbor",
    "Herb,8reb": "Herb / 8reb",
    "Rou7 / rouh": "Rou7 / rouh",
    "Gayla or gaila": "Gayla / gaila",
    "Wahdi or wa7di": "Wahdi / wa7di",

    # Lebanon
    "djeij (but this means chicken, not mosque)": "djeij",
    "Gharib / 8arib": "Gharib / 8arib",
    "جراج jraj?": "jraj",
    'hadi2it l wared (more so "jnayne" or "hadi2a" in lebanese dialect)': "hadi2it l wared",

    # Morocco
    "Stikhdam/ sti3mal/ khedem": "Stikhdam",
    "Placard/ mariyo": "Placard",
    "balakar (je sais pas ce que ca veut dire)": "balakar",
    "sbah / sbah7 / sabah / saba7": "sbah / sbah7 / sabah / saba7",
    "Skhun/ skhon": "Skhun / skhon",
    "Teyara/ tayara": "Teyara / tayara",
    "Ferran (torres)": "Ferran",
    "Gal/ 9al": "Gal / 9al",
    "Werda/ warda": "Werda / warda",
    "Hrb or Hreb": "Hrb / Hreb",

    # Tunisia
    "behya / sem7a": "behya",
}

def form_inspection_data():
    for dialect in ["Algerian", "Egyptian", "Lebanese", "Moroccan", "Tunisian"]:
        df = pd.read_csv(f"../data/lexicon/{dialect}_lexicon_cleaned.tsv", sep="\t")

        words = [c for c in df.columns if c != "Responder_ID"]

        rows = []

        n_multiple_mappings = sum(["/" in m for word in words for m in df[word].dropna()])
        for word in words:
            mappings = sorted(
                set(
                    [
                        w
                        for l in df[word]
                        .dropna()
                        .apply(lambda s: s.strip().lower().split("/"))
                        .tolist()
                        for w in l
                    ]
                ),
                key=lambda s: len(s),
            )
            for mapping in mappings:
                alignment_len, alignment = align_word(word.strip(), mapping.strip())
                ar_row = {"Word": word, "Wrong Alignment?": "", "Invalid Transliteration?": ""}
                lat_row = {"Word": mapping, "Wrong Alignment?": "", "Invalid Transliteration?": ""}
                if alignment:
                    for i, step in enumerate(alignment):
                        ar_row[f"step_{i}"] = step[0]
                        lat_row[f"step_{i}"] = step[1]
                rows.append(ar_row)
                rows.append(lat_row)
                rows.append({})

        output_df = pd.DataFrame(rows)
        output_df.to_excel(f"../data/lexicon_review/{dialect}.xlsx", index=False)

        print(dialect, int(output_df.shape[0]/3))
        print(f"Number of words with multiple mappings: {n_multiple_mappings}")
        print()

def main():
    df = pd.read_csv("../data/parsed_survey_responses.csv")

    for dialect in ["Algerian", "Egyptian", "Lebanese", "Moroccan", "Tunisian"]:
        dialect_lexicon_df = df.loc[
            df["Dialect (Country)"] == dialect,
            ["Responder_ID"] + [c for c in df.columns if dialect in c],
        ]
        dialect_lexicon_df.columns = [
            re.split(r"_Q\d*_", c)[-1].strip("\u200e.").strip()
            for c in dialect_lexicon_df.columns
        ]
        dialect_lexicon_df["empty_lexicon_responses"] = dialect_lexicon_df.apply(
            lambda row: len(row.dropna()) == 1, axis=1
        )
        dialect_lexicon_df = dialect_lexicon_df[
            ~dialect_lexicon_df["empty_lexicon_responses"]
        ]
        dialect_lexicon_df.drop(columns=["empty_lexicon_responses"], inplace=True)
        dialect_lexicon_df.to_csv(
            f"../data/lexicon/{dialect}_lexicon_raw.tsv", sep="\t", index=False
        )

        cleaned_dialect_lexicon_df = dialect_lexicon_df.apply(
            lambda col: col.apply(lambda v: WORDS_NORMALIZATION.get(v, v))
        )
        cleaned_dialect_lexicon_df.to_csv(
            f"../data/lexicon/{dialect}_lexicon_cleaned.tsv", sep="\t", index=False
        )

    # Generate the inspection data
    form_inspection_data()

if __name__ == "__main__":
    main()
