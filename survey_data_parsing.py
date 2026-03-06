import pandas as pd
import re
import os
import argparse
import numpy as np


def merge_column_with_others_option(
    df, column_name, text_column_name, other_option="Other (Please specify)"
):
    """
    Merges a specified column with another text column if the value is the 'other_option'.
    Args:
        df: The DataFrame containing the columns.
        column_name: The name of the column to check for 'Other (Please specify)'.
        text_column_name: The name of the text column to merge with.
        other_option: The value indicating 'Other' in the column.
    Returns:
        None: The DataFrame is modified in place.
    """
    if column_name in df.columns and text_column_name in df.columns:
        df.loc[df[column_name] == other_option, column_name] = df.loc[
            df[column_name] == other_option, text_column_name
        ]
        df.drop(columns=[text_column_name], inplace=True)


def full_dialect_data_pipeline(raw_input_filepath: str, final_output_filepath: str):
    """
    Processes a raw dialect survey CSV file through a complete, end-to-end
    cleaning and structuring pipeline.
    Args:
        raw_input_filepath: Path to the absolute raw CSV file from the survey tool.
        final_output_filepath: Path where the final, processed dataset will be saved.
    """
    if not os.path.exists(raw_input_filepath):
        print(f"Error: The file '{raw_input_filepath}' was not found.")
        return
    print("--- Starting Full Data Processing Pipeline ---")
    # --- Step 0: Load Raw Data ---
    print(f"\n[0] Loading raw data from '{raw_input_filepath}'...")
    df = pd.read_csv(raw_input_filepath)
    print(f"    > Loaded dataframe with {df.shape[0]} rows and {df.shape[1]} columns.")

    # --- Step 1: Initial Column Deletion ---
    print("\n[1] Performing initial deletion of metadata and tracking columns...")
    columns_to_delete = [
        "StartDate",
        "EndDate",
        "Status",
        "IPAddress",
        "RecordedDate",
        "ResponseId",
        "RecipientLastName",
        "RecipientFirstName",
        "RecipientEmail",
        "ExternalReference",
        "LocationLatitude",
        "LocationLongitude",
        "DistributionChannel",
        "Q_RecaptchaScore",
        "Consent",
        "Email",
        "Q55",
    ]
    patterns_to_remove = ["_Click Count", "_First Click", "_Last Click", "_Page Submit"]
    timing_cols_to_remove = [
        col for col in df.columns if any(p in col for p in patterns_to_remove)
    ]
    all_columns_to_remove = list(set(columns_to_delete + timing_cols_to_remove))
    original_col_count = df.shape[1]
    df.drop(columns=all_columns_to_remove, errors="ignore", inplace=True)
    print(
        f"    > Dropped {original_col_count - df.shape[1]} columns. New column count: {df.shape[1]}."
    )

    # --- Step 2: Initial Column Renaming ---
    print("\n[2] Performing initial renaming of 'Algeria words' columns...")
    df.columns = [col.replace("Algeria words", "Q0") for col in df.columns]
    print(f"    > Renamed columns containing 'Algeria words'.")

    metadata_row = df.iloc[0]

    # --- Step 3: Enrich Transliteration Columns with Words ---
    print("\n[3] Renaming transliteration columns with Arabic words...")
    word_pattern = re.compile(
        r"^(.+?)\s*-\s*\[CurrentLoopNumber]\/\[TotalLoops\]", re.DOTALL
    )
    word_rename_map = {}
    for col_name in df.columns:
        cell_text = metadata_row.get(col_name)
        if isinstance(cell_text, str) and word_pattern.match(cell_text):
            extracted_word = word_pattern.match(cell_text).group(1).strip()
            word_rename_map[col_name] = f"{col_name}_{extracted_word}"
    df.rename(columns=word_rename_map, inplace=True)
    print(f"    > Renamed {len(word_rename_map)} columns.")

    # --- Step 4: Add Dialect Information to Column Names ---
    print(
        "\n[4] Adding dialect tags (Tunisian, Moroccan, etc.) to column names based on Q-codes"
    )
    dialect_map = {
        "Q17": "Tunisian",
        "Q14": "Moroccan",
        "Q11": "Lebanese",
        "Q": "Egyptian",
        "Q0": "Algerian",
    }
    dialect_pattern = re.compile(r"^(\d+)_(Q17|Q14|Q11|Q0|Q)_(.+)$")
    dialect_rename_map = {}
    for col_name in df.columns:
        match = dialect_pattern.match(col_name)
        if match:
            prefix, q_code, word = match.groups()
            dialect = dialect_map.get(q_code)
            if dialect:
                dialect_rename_map[col_name] = f"{prefix}_{dialect}_{q_code}_{word}"
    df.rename(columns=dialect_rename_map, inplace=True)
    print(f"    > Added dialect tags to {len(dialect_rename_map)} columns.")

    # --- Step 5: Remove Hidden Columns ---
    print("\n[5] Removing hidden columns based on metadata row content...")
    hidden_mask = metadata_row.str.contains("\\(Hidden\\)", na=False, regex=True)
    columns_to_drop = df.columns[hidden_mask].tolist()
    df.drop(columns=columns_to_drop, inplace=True)
    print(f"    > Removed {len(columns_to_drop)} hidden columns.")

    # --- Step 6: Standardize Final Column Names ---
    print("\n[6] Applying final renaming to demographic/opinion columns...")
    final_rename_map = {
        "Q46": "Second language",
        "Q46_6_TEXT": "Second language_TEXT",
        "Q29": "Arabizi perception",
        "Q29_6_TEXT": "Arabizi perception_TEXT",
        "Q30": "Arabizi perception (explanation)",
        "Q31": "Used Arabizi",
        "Q48": "Year of starting texting on mobile phones",
        "Q50": "Usage of Arabizi now compared to year of starting to use mobile phones",
        "Q35": "Arabizi use cases",
        "Q35_4_TEXT": "Arabizi use cases (others)",
        "Q37": "Social media platforms used",
        "Q37_11_TEXT": "Social media platforms used (others)",
        "Q38": "Social media platforms where Arabizi is used",
        "Q38_10_TEXT": "Social media platforms where Arabizi is used (others)",
        "Q40": "Script used on responding to Arabizi",
        "Q40_3_TEXT": "Script used on responding to Arabizi_TEXT",
        "Q41": "Script used on responding to Arabic script",
        "Q41_3_TEXT": "Script used on responding to Arabic script_TEXT",
    }
    df.rename(columns=final_rename_map, inplace=True)
    print("    > Standardized demographic and opinion column names.")

    # --- Step 7: Clean Redundant Header Rows ---
    print("\n[7] Removing non-data header rows...")
    original_row_count = len(df)
    df = df.iloc[2:].reset_index(drop=True)
    print(
        f"    > Removed 2 header rows. Data rows changed from {original_row_count} to {len(df)}."
    )

    # --- Step 8: Add a Unique Identifier ---
    print("\n[8] Adding unique Responder_ID column...")
    df.insert(0, "Responder_ID", range(1, len(df) + 1))
    print(f"    > Added IDs for {len(df)} respondents.")

    # --- Step 9: Remove Incomplete Responses ---
    print("\n[9] Removing rows with incomplete progress and saving them separately...")
    initial_row_count = len(df)

    # Keep track of discarded rows
    void_response_percentage = 33
    discarded_rows = df[df["Progress"].astype(int) < void_response_percentage].copy()

    # Keep only valid rows
    df = df[~(df["Progress"].astype(int) < void_response_percentage)].reset_index(
        drop=True
    )

    removed_count = initial_row_count - len(df)
    print(
        f"    > Removed {removed_count} rows with Progress < {void_response_percentage}. Remaining rows: {len(df)}"
    )

    # Save discarded rows
    if not discarded_rows.empty:
        discarded_filepath = final_output_filepath.replace(".csv", "_discarded.csv")
        discarded_rows.to_csv(discarded_filepath, index=False, encoding="utf-8-sig")
        print(f"    > Discarded rows saved to '{discarded_filepath}'")

    # --- Step 10: Merge related columns ---
    print("\n[10] Merging columns with 'Other (Please specify)' options...")

    merge_column_with_others_option(df, "Dialect (Country)", "Dialect (Country)_6_TEXT")
    merge_column_with_others_option(df, "Second language", "Second language_TEXT")

    df["Living abroad info"] = df["Living abroad info"].str.replace(
        " (please specify if you want)", "", regex=False
    )
    conditions = [
        (df["Living abroad"] == "Yes")
        & (df["Living abroad info"] == "An Arab country"),
        (df["Living abroad"] == "Yes")
        & (df["Living abroad info"] == "An non-Arab country"),
    ]
    choices = [df["Living abroad info_4_TEXT"], df["Living abroad info_5_TEXT"]]
    df["Living abroad (Country)"] = np.select(conditions, choices, default=None)
    df.drop(
        columns=["Living abroad info_4_TEXT", "Living abroad info_5_TEXT"], inplace=True
    )

    # Handle the 'Social media platforms used' column
    if (
        "Social media platforms used" in df.columns
        and "Social media platforms used (others)" in df.columns
    ):
        mask_used = df["Social media platforms used"].str.contains(
            "Other (Please specify)", na=False, regex=False
        )
        if mask_used.any():
            print(
                f"    > Found {mask_used.sum()} rows with 'Other (Please specify)' in 'Social media platforms used'"
            )
            for idx in df[mask_used].index:
                original_value = df.loc[idx, "Social media platforms used"]
                replacement_text = df.loc[idx, "Social media platforms used (others)"]
                if pd.notna(replacement_text):
                    df.loc[idx, "Social media platforms used"] = original_value.replace(
                        "Other (Please specify)", str(replacement_text)
                    )
                else:
                    df.loc[idx, "Social media platforms used"] = (
                        original_value.replace("Other (Please specify)", "")
                        .strip()
                        .rstrip(",")
                    )
        df.drop(
            columns=["Social media platforms used (others)"],
            errors="ignore",
            inplace=True,
        )
        print("    > Merged 'other' text in 'Social media platforms used'.")

    # Handle the 'Social media platforms where Arabizi is used' column
    if (
        "Social media platforms where Arabizi is used" in df.columns
        and "Social media platforms where Arabizi is used (others)" in df.columns
    ):
        mask_where_used = df[
            "Social media platforms where Arabizi is used"
        ].str.contains("Other (Please specify)", na=False, regex=False)
        if mask_where_used.any():
            print(
                f"    > Found {mask_where_used.sum()} rows with 'Other (Please specify)' in 'Social media platforms where Arabizi is used'"
            )
            # Iterate through each row that needs replacement
            for idx in df[mask_where_used].index:
                original_value = df.loc[
                    idx, "Social media platforms where Arabizi is used"
                ]
                replacement_text = df.loc[
                    idx, "Social media platforms where Arabizi is used (others)"
                ]
                if pd.notna(replacement_text):
                    df.loc[idx, "Social media platforms where Arabizi is used"] = (
                        original_value.replace(
                            "Other (Please specify)", str(replacement_text)
                        )
                    )
                else:
                    # If no replacement text, just remove "Other (Please specify)"
                    df.loc[idx, "Social media platforms where Arabizi is used"] = (
                        original_value.replace("Other (Please specify)", "")
                        .strip()
                        .rstrip(",")
                    )
        df.drop(
            columns=["Social media platforms where Arabizi is used (others)"],
            errors="ignore",
            inplace=True,
        )
        print(
            "    > Merged 'other' text in 'Social media platforms where Arabizi is used'."
        )

    merge_column_with_others_option(
        df, "Arabizi perception", "Arabizi perception_TEXT", "Others (please specify)"
    )
    merge_column_with_others_option(
        df,
        "Script used on responding to Arabizi",
        "Script used on responding to Arabizi_TEXT",
        "Others (Please specify)",
    )
    merge_column_with_others_option(
        df,
        "Script used on responding to Arabic script",
        "Script used on responding to Arabic script_TEXT",
        "Others (Please specify)",
    )

    # --- Step 11: Manually map some values for free-form fields ---
    print("\n[11] Manually mapping values for free-form fields...")
    dialect_map = {
        "خليجية": "Gulf",
        "سعودية": "Saudi",
        "سودانية": "Sudanese",
        "فلسطينية": "Palestinian",
        "عراقية": "Iraqi",
        "عمانية": "Omani",
        "Saudi Arabia": "Saudi",
        "syrian levantine": "Syrian",
        "Sudan": "Sudanese",
        "Sudanese ": "Sudanese",
        "Sudan ": "Sudanese",
        "Syria": "Syrian",
        "Khaliji": "Gulf",
    }
    df["Dialect (Country)"] = df["Dialect (Country)"].replace(dialect_map)
    df.loc[df["Dialect (Country)"].isnull(), "Dialect (Country)"] = "Other-unspecified"

    df.loc[
        df["Year of starting texting on mobile phones"] == "٢٠٢٥",
        "Year of starting texting on mobile phones",
    ] = 2025

    # --- Step 12: Normalize Dialect (City) values ---
    print("\n[12] Normalizing Dialect (City) values...")
    if "Dialect (City)" in df.columns:
        df["Dialect (City)"] = df["Dialect (City)"].astype(str).str.strip()
        df["Dialect (City)"].replace("nan", np.nan, inplace=True)
        original_series = df["Dialect (City)"].copy()

        # mapping dictionary
        city_dialect_map = {
            "الجداوية": "Jeddah",
            "اسكندراني": "Alexandria",
            "Akkari in Tunisia (from Zarzis, Medenine)": "Zarzis",
            "Shami (blend)": "Shami",
            "Caireness (Cairo Dialect)": "Cairo",
            "le dialecte de Marrakech": "Marrakech",
            "Rabat's dialect in Morocco": "Rabat",
            "Casablanca dialect in morocco": "Casablanca",
            "Mix between Najdi (Central Saudi) and Hejazi (Western Saudi)": "Najdi/Hejazi",
            "اللهجة الجنوبية في المملكة العربية السعودية": "Southern Saudi",
            "اللهجة القاهرية": "Cairo",
            "le dialecte d'Alger en Algérie": "Alger",
            "Tripoli Lebanon": "Tripoli",
            "Marrakshi dialect and Oriental (Oujdi) dialect in Morocco": "Marrakech/Oujda",
            "Tripoli (Lebanon)": "Tripoli",
            "Tunis dialect in Tunisia": "Tunis",
            "Moslawi Baghdadi mix": "Moslawi/Baghdad",
            "Alger en Algérie": "Alger",
            "Algérois": "Alger",
            "Algiersese": "Alger",
            "Algiers": "Alger",
            "Algeirs/ Algeria": "Alger",
            "L'algérois d'Alger": "Alger",
            "Gafsa tunisie": "Gafsa",
            "Khenchela's dialect": "Khenchela",
            "القاهرية": "Cairo",
            "نابلسية": "Nablus",
            "I speak an Eastern Algerian dialect.": "Eastern Algeria",
            "Western (Gharbawi) Libyan dialect, specifically Tripoli Dialect.": "Tripoli Libya",
            "حضري قطري": "Qatari",
            "Qalqeeli, Palestine": "Qalqilya",
            "القصرينية في تونس": "Kasserine",
            "Sa'idi": "Saidi",
            "My first language is English": "English",
            "Ba7rani (dialect of shia arabs in bahrain and eastern saudi)": "Bahrani",
            "Setif in Algeria (Hilalian - not sure)": "Setif",
            "Aleppo dialect": "Aleppo",
            "Riyadh Najdi": "Najdi",
            "Blida's dialect in Algeria": "Blida",
            "Darija ( Algerian) and Baghdadi": "Algeria/Baghdad",
            "Aleppine": "Aleppo",
            "Alexandrian in Egypt": "Alexandria",
            "اللهجة النابلسية": "Nablus",
            "Northern Lebanese Dialect": "Northern Lebanese",
            "Standard Cairo Egyptian Arabic": "Cairo",
            "Cairenese": "Cairo",
            "cairene": "Cairo",
            "قاهرية": "Cairo",
            "Makhtar, Tunisie": "Maktar",
            "Casablanca's dialect in Morocco": "Casablanca",
            "Sahli dialect": "Sousse",
            "PALB - Beirut": "Beirut",
            "Msaken, sousse dialect": "Sousse",
            "Salé (Rabat) in Morocco": "Salé",
            "Normal dialect : same as casablanca, rabat": "Casablanca",
            "Beiruti Lebanese, Tripolitan Lebanese": "Beirut/Tripoli",
            "tunisian": "Tunisian",
            "Sousse (dialecte du Sahel tunisien)": "Sousse",
            "Le dialecte de Salé au Maroc": "Salé",
            "Rabat et Marrakech au maroc": "Rabat/Marrakech",
            "Coast sahel": "Sousse",
            "Rabat's dialect": "Rabat",
            "اللهجة الفاسية في المغرب": "Fas",
            "Fassi dialect": "Fas",
            "Khaliji, Kuwaiti": "Kuwait",
            "Sousse en Tunisie": "Sousse",
            "لهجة العاصمة": "Tunis",
            "سوسة": "Sousse",
            "Algerian, Algiers": "Alger",
            "لهجة عبري": "Ibri",
            "اللهجة العراقية في بغداد": "Baghdad",
            "Oujda Maroc": "Oujda",
            "west amman": "Amman",
            "Le dialecte de Rabat au Maroc": "Rabat",
            "My strongest dialect is Cairene, my second-strongest is Nabulsi, and the third dialect I have used in daily life is that of Meknes": "Cairo/Nablus/Meknes",
            "Beiruti & Southern accents in Lebanon": "Beirut/Southern Lebanese",
            "Beiruti": "Beirut",
            "Oran's Dialect": "Oran",
            "الناصرة": "Nazareth",
            "اللهجة العروبية": "Arubiya",
            "Sehli": "Sousse",
            "Rabat’s dialect": "Rabat",
            "Tlemcenien": "Tlemcen",
        }

        # Apply the mapping
        df["Dialect (City)"] = df["Dialect (City)"].replace(city_dialect_map)
        changes_made = (
            (original_series != df["Dialect (City)"]) & original_series.notna()
        ).sum()
        print(f"    > Actually normalized {changes_made} dialect city values.")

    else:
        print(
            "    > 'Dialect (City)' column not found. Skipping dialect city normalization."
        )

    print("\n--- Pipeline Complete ---")
    df.to_csv(final_output_filepath, index=False, encoding="utf-8-sig")
    print(f"Final, processed dataset saved to '{final_output_filepath}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean and process the raw dialect survey CSV file."
    )
    parser.add_argument(
        "--input_filepath",
        default="survey.csv",
        help="Path to the raw input CSV file from the survey tool.",
    )
    parser.add_argument(
        "--output_filepath",
        default="parsing/survey_cleaned.csv",
        help="Path to save the final, processed CSV file.",
    )
    args = parser.parse_args()
    full_dialect_data_pipeline(args.input_filepath, args.output_filepath)
