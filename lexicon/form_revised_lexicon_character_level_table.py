import pandas as pd
from form_lexicon_character_level_table import (
    get_letter_mappings_string,
    build_letters_map,
)

pd.set_option("display.max_colwidth", None)

DIALECTS = ["Algerian", "Egyptian", "Lebanese", "Moroccan", "Tunisian"]


def extract_steps(arabic_row, latin_row):
    steps = []
    first_nan_step = True
    for step in range(0, 14):
        if f"step_{step}" not in arabic_row:
            assert f"step_{step}" not in latin_row
            continue
        try:
            arabic, latin = arabic_row[f"step_{step}"], latin_row[f"step_{step}"]
            if str(arabic).lower() == "nan":
                arabic = ""
            if str(latin).lower() == "nan":
                latin = ""

            if not arabic and not latin:
                if not first_nan_step:
                    first_nan_step = False
                    continue
            elif not first_nan_step:
                print("ERROR!!")
                print(arabic_row.T)
                print(latin_row.T)
                print()
            else:
                steps.append((arabic, latin))
        except:
            print(arabic_row)

    return tuple(steps)


def form_mappings_df(dialect):
    original_df = pd.read_excel(f"../data/lexicon_review/{dialect}.xlsx")
    reviewed_df = pd.read_excel(f"../data/lexicon_reviewed/{dialect}_reviewed.xlsx")

    for df in [original_df, reviewed_df]:
        df.dropna(subset="Word", inplace=True)

    assert original_df.shape[0] == reviewed_df.shape[0]
    original_df.shape[0]

    discard_column = "Invalid Transliteration?\n\nThese will be discarded"

    transliteration_dictionary = {}
    for i in range(0, original_df.shape[0], 2):
        original_arabic_row = original_df.iloc[i]
        original_transliterated_row = original_df.iloc[i + 1]

        arabic_word = original_arabic_row["Word"]
        transliteration = original_transliterated_row["Word"]

        transliteration_dictionary[(arabic_word, transliteration)] = {
            "original_steps": extract_steps(
                original_arabic_row, original_transliterated_row
            ),
            "frequency": original_arabic_row["Frequency"],
        }

    for i in range(0, reviewed_df.shape[0], 2):
        reviewed_arabic_row = reviewed_df.iloc[i]
        reviewed_transliterated_row = reviewed_df.iloc[i + 1]

        arabic_word = reviewed_arabic_row["Word"]
        transliteration = reviewed_transliterated_row["Word"]

        transliteration_dictionary[(arabic_word, transliteration)][
            "reviewed_steps"
        ] = extract_steps(reviewed_arabic_row, reviewed_transliterated_row)
        transliteration_dictionary[(arabic_word, transliteration)]["discard"] = (
            str(reviewed_df.iloc[i][discard_column]) != "nan"
        )
        transliteration_dictionary[(arabic_word, transliteration)]["modified"] = (
            transliteration_dictionary[(arabic_word, transliteration)]["original_steps"]
        ) != (
            transliteration_dictionary[(arabic_word, transliteration)]["reviewed_steps"]
        )

    return transliteration_dictionary


## Generate the table
mapped_dfs = {}
for dialect in DIALECTS:
    transliteration_dictionary = form_mappings_df(dialect)
    mapped_df = pd.DataFrame(transliteration_dictionary).T.reset_index()
    print(
        dialect,
        "Discarded transliterations:",
        mapped_df.apply(
            lambda row: int(row["frequency"]) * int(row["discard"]), axis=1
        ).sum(),
        "Out of: ",
        mapped_df["frequency"].sum(),
    )
    print(
        "Modified transliterations:",
        mapped_df["modified"].sum(),
        "out of:",
        mapped_df.shape[0],
    )
    print()
    mapped_dfs[dialect] = mapped_df

# Generate the latex table for letter mappings
dataframes = {}
for dialect in DIALECTS:
    mapped_df = mapped_dfs[dialect]
    tuples = [
        t
        for l, f in zip(
            mapped_df[(mapped_df["discard"] == False)]["reviewed_steps"].tolist(),
            mapped_df[(mapped_df["discard"] == False)]["frequency"].tolist(),
        )
        for t in list(l)
        for _ in range(int(f))
    ]
    char_mappings = {}
    for ar_char, en_char in tuples:
        if ar_char not in char_mappings:
            char_mappings[ar_char] = {}
        char_mappings[ar_char][en_char] = char_mappings[ar_char].get(en_char, 0) + 1

    characters = sorted(char_mappings.keys())
    rendered_characters = [
        (
            rf"\AR{{{c}}}"
            if c not in ([" ", ""] + ["چ"] + ["ڜ", "ڤ", "ڭ", "ڥ"])
            else (
                "sp."
                if c == " "
                else (
                    r"$\epsilon$"
                    if c == ""
                    else rf"\FR{{{c}}}"
                    if c == "چ"
                    else rf"\textkurdish{{{c}}}"
                )
            )
        )
        for c in characters
    ]
    dialect_df = pd.DataFrame(
        [
            {dialect: get_letter_mappings_string(c, char_mappings[c])}
            for c in characters
        ],
        index=rendered_characters,
    )
    dataframes[dialect] = dialect_df

table_df = pd.concat(dataframes, axis=1, join="outer")
table_df.fillna("", inplace=True)

table_str = table_df.to_latex(escape=False)

print(table_str)
