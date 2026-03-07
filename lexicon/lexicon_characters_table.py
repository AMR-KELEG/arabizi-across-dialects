import pandas as pd
from pprint import pprint
from scripts_aligner import align_word, build_letters_map

DIALECTS = ["Algerian", "Egyptian", "Lebanese", "Moroccan", "Tunisian"]

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
    "je ne l'ai jamais écrit en arabizi, je crois que si je devais le faire j'écrirai ce mot directement en caractères arabes": None,
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
    "sakhana": None,
    "Skhana": None,
    "Broda": None,
    "Brouda": None,
    "Ils jouent": None,
}


def main():
    df = pd.read_csv("../data/parsed_survey_responses.csv")

    # Identify mappings that are not alignable
    for dialect in DIALECTS:
        dialect_word_alignments = set()
        print(f"Check '{dialect}' dialect and print words that do not align:")
        dialect_columns = [c for c in df.columns if dialect in c]

        for dialect_column in dialect_columns:
            word = dialect_column.split("_")[-1].strip("\u200e.").strip()

            # Apply normalization to the mappings for this dialect column (if any)
            mappings = (
                df[dialect_column]
                .apply(lambda w: WORDS_NORMALIZATION.get(w, w))
                .dropna()
            )

            # Split responses with multiple mappings and flatten the list
            mappings = mappings.apply(lambda m: m.split("/")).tolist()
            mappings = [item for sublist in mappings for item in sublist]
            mappings = list(set(mappings))

            for mapping in mappings:
                mapping = mapping.strip()
                mapping = mapping[0].lower() + mapping[1:]
                len_matched, alignment = align_word(word, mapping)
                if not alignment:
                    lower_mapping = mapping.lower()
                    lower_len_matched, lower_alignment = align_word(word, lower_mapping)
                    if not lower_alignment:
                        print(word, mapping)
                    else:
                        dialect_word_alignments.add(tuple(lower_alignment))
                else:
                    dialect_word_alignments.add(tuple(alignment))

        print("")
        print(f"Unique alignments for '{dialect}': {len(dialect_word_alignments)}")
        pprint(dialect_word_alignments)
        print("\n\n---------------------------------\n\n")

    def get_all_alignments(df, dialect):
        """Identify the letter alignment lists for all the words in the given dialect."""
        dialect_columns = [c for c in df.columns if dialect in c]
        all_alignments = []

        for dialect_column in dialect_columns:
            words = dialect_column.split("_")[-1].strip("\u200e.")

            for word in words.split(" / "):
                word = word.strip()
                mappings = df[dialect_column].dropna().tolist()
                mappings = [m.split(" / ") for m in mappings]
                mappings = [item.strip() for sublist in mappings for item in sublist]
                mappings = list(mappings)

                for mapping in mappings:
                    mapping = mapping.strip()

                    # Check if casing is significant!
                    mapping = mapping[0].lower() + mapping[1:]

                    len_matched, alignment = align_word(word, mapping)

                    # TODO: Handle lower case in a better way
                    if alignment:
                        all_alignments.append(alignment)

                    else:
                        lower_mapping = mapping.lower()
                        lower_len_matched, lower_alignment = align_word(
                            word, lower_mapping
                        )
                        if lower_alignment:
                            all_alignments.append(lower_alignment)

        return all_alignments

    full_dict, wikipedia_dict = build_letters_map()

    def get_letter_mappings_string(letter, mappings):
        """Get a string representation of letter mappings for the Table."""
        tuples = sorted(mappings.items(), key=lambda t: -t[1])
        letter = (
            letter
            if letter not in [" ", ""]
            else "sp." if letter == " " else r"$\epsilon$"
        )
        mappings = [
            t[0] if t[0] not in [" ", ""] else "sp." if t[0] == " " else r"$\epsilon$"
            for t in tuples
        ]
        colors = [
            (
                "red"
                if letter not in ["sp.", r"$\epsilon$"]
                and (letter not in wikipedia_dict or m not in wikipedia_dict[letter])
                else "black"
            )
            for m in mappings
        ]

        return " ".join(
            [
                f"\\textcolor{{{color}}}{{{m}~({t[1]})}}"
                for m, t, color in zip(mappings, tuples, colors)
            ]
        )

    # Generate the latex table for letter mappings
    dataframes = {}
    for dialect in DIALECTS:
        tuples = sum(get_all_alignments(df, dialect), [])
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
                        else rf"\FR{{{c}}}" if c == "چ" else rf"\textkurdish{{{c}}}"
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
        # dialect_df.set_index(characters, inplace=True, drop=True)
        dataframes[dialect] = dialect_df

    table_df = pd.concat(dataframes, axis=1, join="outer")
    table_df.fillna("", inplace=True)

    table_str = table_df.to_latex()
    for row in table_str.split("\n"):
        print(row)
        if row.endswith("\\"):
            print(r"\midrule")

    # Generate the reverse Table (Arabizi to Arabic)
    reverse_wikipedia_dict = {}

    for key in wikipedia_dict.keys():
        mappings = wikipedia_dict[key]
        for mapping in mappings:
            if mapping not in reverse_wikipedia_dict:
                reverse_wikipedia_dict[mapping] = set()
            reverse_wikipedia_dict[mapping].add(key)

    def get_letter_mappings_string(letter, mappings):
        """Get a string representation of letter mappings for the Table."""
        tuples = sorted(mappings.items(), key=lambda t: -t[1])
        letter = (
            letter
            if letter not in [" ", ""]
            else "sp." if letter == " " else r"$\epsilon$"
        )
        mappings = [
            t[0] if t[0] not in [" ", ""] else "sp." if t[0] == " " else r"$\epsilon$"
            for t in tuples
        ]

        rendered_mappings = [
            (
                rf"\AR{{{c}}}"
                if c not in ([" ", ""] + ["چ"] + ["ڜ", "ڤ", "ڭ", "ڥ"])
                else (
                    "sp."
                    if c == " "
                    else (
                        "$\\epsilon$"
                        if c == ""
                        else rf"\FR{{{c}}}" if c == "چ" else rf"\textkurdish{{{c}}}"
                    )
                )
            )
            for c in mappings
        ]

        colors = [
            (
                "red"
                if letter not in ["sp.", r"$\epsilon$"]
                and (
                    letter not in reverse_wikipedia_dict
                    or m not in reverse_wikipedia_dict[letter]
                )
                else "black"
            )
            for m in mappings
        ]
        # return " ".join([f"{'sp.' if t[0] == ' ' else (t[0] if t[0] else '$epsilon$')} ({t[1]})" for t in tuples])
        return " ".join(
            [
                f"\\textcolor{{{color}}}{{{m}~({t[1]})}}"
                for m, t, color in zip(rendered_mappings, tuples, colors)
            ]
        )

    # Generate the latex table for letter mappings
    dataframes = {}
    for dialect in DIALECTS:
        tuples = sum(get_all_alignments(df, dialect), [])

        char_mappings = {}
        for ar_char, en_char in tuples:
            if en_char not in char_mappings:
                char_mappings[en_char] = {}
            char_mappings[en_char][ar_char] = char_mappings[en_char].get(ar_char, 0) + 1

        characters = sorted(char_mappings.keys())
        rendered_characters = [
            (
                letter
                if letter not in [" ", ""]
                else "sp." if letter == " " else r"$\epsilon$"
            )
            for letter in characters
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
    table_df.sort_index(inplace=True)

    table_str = table_df.to_latex()
    for row in table_str.split("\n"):
        print(row)
        if row.endswith("\\"):
            print(r"\midrule")

    # ### Look at the transliteartions of common words

    # from collections import Counter

    # dialect_words = {}
    # for dialect in DIALECTS:
    #     dialect_columns = [c for c in df.columns if dialect in c]
    #     dialect_words[dialect] = [
    #         dialect_column.split("_")[-1].strip("\u200e.")
    #         for dialect_column in dialect_columns
    #     ]

    # common_words = Counter([t for d in DIALECTS for t in dialect_words[d]])
    # common_words.most_common(10)

    # word = "صباح"
    # for dialect in DIALECTS:
    #     columns = [c for c in df if word in c and dialect in c]
    #     if columns:
    #         forms = df[columns[0]].dropna().apply(lambda s: s.lower()).value_counts()
    #         print(forms)


if __name__ == "__main__":
    main()
