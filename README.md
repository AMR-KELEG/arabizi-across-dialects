# Arabizi across Dialects

## Steps:

### Parsing the data (Note: the data is not released for privacy reasons)
- `python survey_data_parsing.py --input_filepath data/raw_survey_responses.csv --output_filepath data/parsed_survey_responses.csv`

### Quantiative Analysis
- Generate the quanitative analysis plots (Requires access to the parsed data):<br/>
`cd survey_quantitative_analysis && python generate_survey_plots.py`

- Measure the statistical significance of the identified patterns:<br/>
`cd survey_quantitative_analysis && python survey_trends_stat_significance.py`


### Lexicon
- Parse the raw lexicon of Arabic-Arabizi words:<br/>
`cd lexicon && python parse_lexicon_entries_from_responses.py`
  - Outputs:
    - data/lexicon/*_raw.tsv: original responses provided by users.
    - data/lexicon/*_raw.tsv: responses provided by users after unifying the format for words with multiple provided transliterations.
    - data/lexicon_review/*: the Arabic-Latin alignments identified by the algorithm
    - data/lexicon_reviewed/*: the manually corrected Arabic-Latin alignments.

- Form the character-level mapping Table based on the original responses:<br/>
`cd lexicon && python form_revised_lexicon_character_level_table.py`


#### Scripts:
* `survey_data_parsing.py` - parse the Qualtrics raw responses into a csv file.
* `semanticscholar_analysis/semanticscholar_dialects_in_studies.py` - Identify the representation of the dialects in Arabizi studies.
