import os
import pandas as pd
from pathlib import Path
from form_revised_lexicon_character_level_table import form_mappings_df


def fix_row(row, mappings_dict):
    arabic_words = row.keys()
    values = {}
    for arabic_word in arabic_words:
        arabizi_word = row[arabic_word]
        if pd.isnull(arabizi_word) or str(arabizi_word).lower().strip() == "nan":
            values[arabic_word] = ""
            continue
        else:
            arabizi_word = arabizi_word.strip()

        # Handle multiple cases
        if "/" in arabizi_word:
            variants = []
            for arabizi_variant in arabizi_word.split("/"):
                arabizi_variant = arabizi_variant.strip()
                if mappings_dict[(arabic_word, arabizi_variant.lower())]["discard"]:
                    continue
                variants.append(arabizi_variant)

            values[arabic_word] = " / ".join(variants)

        elif mappings_dict[(arabic_word, arabizi_word.lower())]["discard"]:
            values[arabic_word] = ""
        else:
            values[arabic_word] = arabizi_word

    return values


def main():
    OUTPUT_DIR = "../data/lexicon_final/"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for dialect in ["Algerian", "Egyptian", "Lebanese", "Moroccan", "Tunisian"]:
        mappings_dict = form_mappings_df(dialect)

        dialect_df = pd.read_csv(
            f"../data/lexicon/{dialect}_lexicon_cleaned.tsv", sep="\t"
        )
        dialect_df = dialect_df.set_index("Responder_ID")

        final_df = pd.DataFrame(
            dialect_df.apply(lambda row: fix_row(row, mappings_dict), axis=1).tolist()
        )
        final_df.index = dialect_df.index

        final_df.to_csv(Path(OUTPUT_DIR, f"{dialect}_lexicon_final.tsv", sep="\t"))


if __name__ == "__main__":
    main()
