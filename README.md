# Romanized Arabic Across Dialects: Views, Usage Patterns, and Linguistic Variation

This is the codebase accompanying the `Romanized Arabic Across Dialects: Views, Usage Patterns, and Linguistic Variation` paper, accepted at EMNLP 2026 (Findings).

## Steps:

### Parsing the data (Note: the data is not released for privacy reasons. Please reach out if you need to access it.)
- `python survey_data_parsing.py --input_filepath data/raw_survey_responses.csv --output_filepath data/parsed_survey_responses.csv`

### (1) Quantiative Analysis
- Generate the quanitative analysis plots (Requires access to the parsed data):<br/>
`cd survey_quantitative_analysis && python generate_survey_plots.py`

- Measure the statistical significance of the identified patterns:<br/>
`cd survey_quantitative_analysis && python survey_trends_stat_significance.py`


### (2) Lexicon
- Parse the raw lexicon of Arabic-Arabizi words:<br/>
`cd lexicon && python parse_lexicon_entries_from_responses.py`
  - Outputs:
    - data/lexicon/*_raw.tsv: original responses provided by users.
    - data/lexicon/*_clean.tsv: responses provided by users after unifying the format for words with multiple provided transliterations.
    - data/lexicon_review/*: the Arabic-Latin alignments identified by the algorithm
    - data/lexicon_reviewed/*: the manually corrected Arabic-Latin alignments.

- Form the character-level mapping Table based on the manually validated responses:<br/>
`cd lexicon && python form_revised_lexicon_character_level_table.py`

- Form the final lexicon after discarding the invalid entries:<br/>
`cd lexicon && python form_final_lexicon.py`

#### Scripts:
* `survey_data_parsing.py` - parse the Qualtrics raw responses into a csv file.
* `semanticscholar_analysis/semanticscholar_dialects_in_studies.py` - Identify the representation of the dialects in Arabizi studies.

## Citation
```
@inproceedings{keleg-etal-2026-romanized,
    title = "Romanized {A}rabic Across Dialects: Views, Usage Patterns, and Linguistic Variation",
    author = "Keleg, Amr  and
      Ben Abdallah, Ahmed Amine  and
      Yassine, Taha  and
      Helwe, Chadi  and
      Guellil, Imane  and
      Ousidhoum, Nedjma",
    booktitle = "Findings of the Association for Computational Linguistics: EMNLP 2026",
    month = nov,
    year = "2026",
    address = "Budapest, Hungary",
    publisher = "Association for Computational Linguistics",
}
```