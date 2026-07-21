import pandas as pd
from math import inf
from functools import lru_cache
from copy import deepcopy


def build_letters_map():
    """
    Build a mapping of Arabic letters to their transliterated forms based on the Wikipedia Arabic chat alphabet.
    The mapping is iteratively augmented with manual modifications to align more responses from the participants.
    """

    words_df = pd.read_csv("letters_map_wikipedia.tsv", sep="\t")

    letters_map = {}
    for letters, mapping in zip(words_df["Letters"], words_df["Arabic chat alphabet"]):
        for l in letters.split():
            if l in letters_map:
                print("ISSUE!")
            letters_map[l] = sorted(mapping.split())
            letters_map[l].reverse()

    letters_map[" "] = [" ", ""]

    wikipedia_letters_map = deepcopy(letters_map)

    # manual modifications (Note: some cases are not dialect-specific)

    # Algerian
    letters_map["أ"] = letters_map["أ"] + ["a"]
    letters_map["آ"] = letters_map["آ"] + ["a"]
    letters_map["إ"] = letters_map["إ"] + ["i"]

    letters_map["ب"] = letters_map["ب"] + ["bb"]
    letters_map["م"] = letters_map["م"] + ["mm"]
    letters_map["ن"] = letters_map["ن"] + ["nn"]
    letters_map["ر"] = letters_map["ر"] + ["rr"]
    letters_map["ز"] = letters_map["ز"] + ["zz"]
    letters_map["س"] = letters_map["س"] + ["ss"]
    letters_map["ص"] = letters_map["ص"] + ["ss"]
    letters_map["ه"] = letters_map["ه"] + ["8"] + ["t"]
    letters_map["ذ"] = letters_map["ذ"] + [] + ["dh"]
    letters_map["ك"] = letters_map["ك"] + ["c"]
    letters_map["ء"] = letters_map["ء"] + [""]
    letters_map["ؤ"] = letters_map["ؤ"] + ["ou", "o"]
    letters_map["ڤ"] = letters_map["ڤ"] + ["g", "gh", "f", "9"]
    letters_map["ق"] = letters_map["ق"] + ["gh"]
    letters_map["ط"] = letters_map["ط"] + ["tt"]
    letters_map["ظ"] = letters_map["ظ"] + ["d"]
    letters_map["ض"] = letters_map["ض"] + ["dd"]
    letters_map["ڜ"] = letters_map.get("ڜ", []) + ["tch"]

    # Egyptian
    letters_map["إ"] = letters_map["إ"] + ["e"]
    letters_map["ي"] = letters_map["ي"] + ["e"]
    letters_map["ق"] = letters_map["ق"] + ["k", "'"]
    letters_map["ا"] = letters_map["ا"] + ["", "2"] + ["e", "i"]
    letters_map["ت"] = letters_map["ت"] + ["tt"]
    letters_map["ى"] = letters_map["ى"] + ["ah"]
    letters_map["ف"] = letters_map["ف"] + ["ph"]
    letters_map["ع"] = letters_map["ع"] + ["a'"]
    letters_map["غ"] = letters_map["غ"] + ["3'"] + ["3’"]
    letters_map["س"] = letters_map["س"] + [] + ["c"]
    letters_map["ل"] = letters_map["ل"] + ["ll"]
    letters_map["ك"] = letters_map["ك"] + ["q"]
    letters_map["ج"] = letters_map["ج"] + ["sh"]
    letters_map["چ"] = letters_map["چ"] + ["sh"]
    letters_map["و"] = letters_map["و"] + ["ww"]
    letters_map["ئ"] = letters_map["ئ"] + ["a'"] + ["2e"]
    letters_map["ه"] = letters_map["ه"] + ["eh"] + ["o", ""]
    letters_map["ي"] = letters_map["ي"] + ["yy", "ya"] + ["a", ""]  # for alef maksura
    letters_map["ة"] = letters_map["ة"] + ["a", "ah"]
    letters_map["ة"] = letters_map["ة"] + ["t"]

    # Lebanese
    letters_map["آ"] = letters_map["آ"] + ["e"]
    letters_map["ا"] = letters_map["ا"] + ["e"]
    letters_map["ج"] = letters_map["ج"] + ["j"]
    letters_map["د"] = letters_map["د"] + ["dd"]
    letters_map["ك"] = letters_map["ك"] + ["kk"]
    letters_map["ق"] = letters_map["ق"] + ["a"]
    letters_map["ع"] = letters_map["ع"] + ["a", "e"]
    letters_map["ض"] = letters_map["ض"] + ["t"]
    letters_map["ة"] = letters_map["ة"] + ["i"]
    letters_map["ى"] = letters_map["ى"] + ["e"]
    letters_map["د"] = letters_map["د"] + [""]

    # Moroccan
    letters_map["أ"] = letters_map["أ"] + ["a"]
    letters_map["ز"] = letters_map["ز"] + ["s"]
    letters_map["ڭ"] = letters_map.get("ڭ", []) + ["g"]
    letters_map["ظ"] = letters_map["ظ"] + ["dd"]
    letters_map["ف"] = letters_map["ف"] + ["f"]
    letters_map["ئ"] = letters_map["ئ"] + ["a", "i", "-"]
    letters_map["ؤ"] = letters_map["ؤ"] + ["-"]

    # Tunisian
    letters_map["أ"] = letters_map["أ"] + ["e", ""]
    letters_map["إ"] = letters_map["إ"] + [""]
    letters_map["ذ"] = letters_map["ذ"] + ["4"]
    letters_map["ظ"] = letters_map["ظ"] + ["4"]
    letters_map["ض"] = letters_map["ض"] + ["4"]

    # Gulf Arabic
    letters_map["غ"] = letters_map["غ"] + [] + ["g"]

    # Misc. (for cases like أم)
    letters_map["أ"] = letters_map["أ"] + ["o"]
    letters_map["#"] = ["#"]
    letters_map["_"] = ["_"]
    letters_map["ل"] = (
        letters_map["ل"] + [] + [""]
    )  # A hack for the dropped lam in some North African dialects

    return letters_map, wikipedia_letters_map


SKIPPABLE_LETTERS = "aeéiouy' "
letters_map, wikipedia_letters_map = build_letters_map()


@lru_cache(maxsize=100000)
def align_word(arabic_word, transliterated_word):
    """
    Determine the longest alignment between an Arabic word and its transliterated form.
    This function uses a recursive approach to match letters based on a provided mapping.
    The letters in SKIPPABLE_LETTERS are vowels that can be present in Arabizi without a corresponding Arabic letter.
    """

    if not arabic_word:
        if not transliterated_word:
            # Both words are empty, return a match
            return 0, []

        # Skip vowels at the end (if needed)
        if transliterated_word[0] in SKIPPABLE_LETTERS:
            len_matched, remaining_alignment = align_word(
                arabic_word, transliterated_word[1:]
            )

            # If we can skip the vowel and still have a match, return it
            if len_matched >= 0:
                return len_matched, [("", transliterated_word[0])] + remaining_alignment

            # If we reach here, it means we have an Arabic word but no transliterated match
            return -inf, []

        # If we have an empty Arabic word but a transliterated word with a letter that cannot be skipped
        return -inf, []

    current_arabic_letter, remaining_word = arabic_word[0], arabic_word[1:]
    potential_letter_mappings = letters_map.get(current_arabic_letter, [])
    max_len, max_alignment = -inf, []

    # Try to match the current Arabic letter with all its potential transliterated forms based on the letters_map
    for matching in potential_letter_mappings:
        if transliterated_word.startswith(matching):
            # Attempt this matching
            len_matched, remaining_alignment = align_word(
                remaining_word, transliterated_word[len(matching) :]
            )

            # If we have a valid match, check if it is the longest found so far
            if len_matched >= 0:
                if len(matching) + len_matched > max_len:
                    max_len = len(matching) + len_matched
                    max_alignment = [
                        (current_arabic_letter, matching)
                    ] + remaining_alignment

    # Try skipping vowels without consuming from the Arabic word!
    if transliterated_word and transliterated_word[0] in SKIPPABLE_LETTERS:
        len_matched, remaining_alignment = align_word(
            arabic_word, transliterated_word[1:]
        )
        if len_matched >= 0:
            if len_matched > max_len:
                max_len = len_matched
                max_alignment = [("", transliterated_word[0])] + remaining_alignment

    return max_len, max_alignment


def get_letter_mappings_string(letter, mappings):
    """Get a string representation of letter mappings for the Table."""
    tuples = sorted(mappings.items(), key=lambda t: -t[1])
    letter = (
        letter if letter not in [" ", ""] else "sp." if letter == " " else r"$\epsilon$"
    )
    mappings = [
        t[0] if t[0] not in [" ", ""] else "sp." if t[0] == " " else r"$\epsilon$"
        for t in tuples
    ]
    colors = [
        (
            "red"
            if letter not in ["sp.", r"$\epsilon$"]
            and (
                letter not in wikipedia_letters_map
                or m not in wikipedia_letters_map[letter]
            )
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


if __name__ == "__main__":
    arabic_sentence = input("Arabic sentence?\n").strip().lower()
    arabizi_sentence = input("Arabizi sentence?\n").strip().lower()

    print(align_word(arabic_sentence, arabizi_sentence))
