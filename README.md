# Arabizi across Dialects

## Steps:

### Parsing the data
- `python survey_data_parsing.py`

### Quantiative Analysis
- Generate the quanitative analysis plots:<br/>
`cd survey_quantitative_analysis && python generate_survey_plots.py`

- Measure the statistical significance of the identified patterns:<br/>
`cd survey_quantitative_analysis && python survey_trends_stat_significance.py`


### Lexicon
- Form the character-level mapping Table based on the original responses:<br/>
`cd lexicon && python form_lexicon_character_level_table.py`

- Parse the raw lexicon of Arabic-Arabizi words:<br/>
`cd lexicon && python parse_lexicon_entries_from_responses.py`

#### Scripts:
* `survey_data_parsing.py` - parse the Qualtrics raw responses into a csv file.
* `semanticscholar_analysis/semanticscholar_dialects_in_studies.py` - Identify the representation of the dialects in Arabizi studies.
