import re
import os
import numpy as np
import pandas as pd
import chardet

# HACK: (@)? are meaningless matches so each regex has 7 capture groups
# (1)-(U1)(A)
# (Exp)-(Site)(Hole)
sample_hole_regex = r"(^\d+)-(U\d+)([a-zA-Z])(@)?(@)?(@)?(@)?$"
# (1)-(U1)(A)-(1)
# (Exp)-(Site)(Hole)-(Core)
sample_core_regex = r"(^\d+)-(U\d+)([a-zA-Z])-(\d+)(@)?(@)?(@)?$"
# (1)-(U1)(A)-(1)(A)
# (Exp)-(Site)(Hole)-(Core)(Type)
sample_type_regex = r"(^\d+)-(U\d+)([a-zA-Z])-(\d+)([a-zA-Z])(@)?(@)?$"
# (1)-(U1)(A)-(1)(A)-(1)
# (1)-(U1)(A)-(1)(A)-(A)
# (Exp)-(Site)(Hole)-(Core)(Type)-(Section)
sample_sect_regex = r"(^\d+)-(U\d+)([a-zA-Z])-(\d+)([a-zA-Z])-(\w+)(@)?$"
# (1)-(U1)(A)-(1)(A)-(1)-(1)
# (1)-(U1)(A)-(1)(A)-(A)-(A)
# (Exp)-(Site)(Hole)-(Core)(Type)-(Section)-(AW)
sample_aw_regex = r"(^\d+)-(U\d+)([a-zA-Z])-(\d+)([a-zA-Z])-(\w+)-(\w+)"
# (1)-(U1)(A)-(1)-(1)-(1)
# (1)-(U1)(A)-(1)-(A)-(A)
# (Exp)-(Site)(Hole)-(Core)-(Section)-(AW)
sample_no_type_aw_regex = r"(^\d+)-(U\d+)([a-zA-Z])-(\d+)(@)?-(\w+)-(\w+)"
invalid_sample_regex = r"(-)?(-)?(-)?(-)?(-)?(-)?(-)?"


def tablerize(word):
    """Converts a word into a format suitable for database field names"""
    # only allow letters, numbers, and underscores
    clean_word = re.sub("[^a-zA-Z0-9_ ]", "", str(word))
    # replace one or more spaces with one underscore
    clean_word = re.sub(" +", "_", clean_word)

    return clean_word.lower()


def convert_column_names(names):
    """Converts a list of names into a dict with original & formatted names"""
    dict = {}
    for name in names:
        dict[name] = tablerize(name)

    return dict


def create_directory(newpath):
    if not os.path.exists(newpath):
        os.makedirs(newpath)


def normalize_sample_col(df):
    if "Sample" in df.columns:
        pass
    elif "Label ID" in df.columns:
        cols = {"Label ID": "Sample"}
        df.rename(columns=cols, inplace=True)
    else:
        create_sample_name(df)


def not_empty(col):
    return pd.notna(col) and col == col


def create_sample_name_for_row(row, columns):
    name = ""
    if not_empty(row["Exp"]):
        name = f"{row['Exp']}"

    name += "-"
    if not_empty(row["Site"]):
        name += f"{row['Site']}"
    if not_empty(row["Hole"]):
        name += f"{row['Hole']}"
    name += "-"
    if not_empty(row["Core"]):
        name += f"{row['Core']}"
    if not_empty(row["Type"]):
        name += f"{row['Type']}"
    name += "-"
    if not_empty(row["Section"]):
        name += f"{row['Section']}"
    name += "-"
    if not_empty(row["A/W"]):
        name += f"{row['A/W']}"

    extra = "Extra Sample ID Data"
    if extra in columns and row[extra] is not None and row[extra] is not np.NaN:
        if row["A/W"] == "PAL":
            name = name + "-" + row[extra]
        else:
            name = name + " " + row[extra]

    name = re.sub("-{2,}", "-", name)
    return re.sub("-$", "", name)


def create_sample_name(df):
    """Uses Exp...A/W columns to create a name for a sample"""
    names = {"Exp", "Site", "Hole", "Core", "Type", "Section", "A/W"}
    if names.issubset(df.columns):
        df["Sample"] = df.apply(
            lambda row: create_sample_name_for_row(row, df.columns), axis=1
        )

    else:
        raise ValueError("File does not have the expected columns.")


def normalize_expedition_section_cols(df):
    """Create Exp...Section columns using Sample or Label ID"""
    # NOTE: There was one file that did not have A/W column
    names = {"Exp", "Site", "Hole", "Core", "Type", "Section"}
    if names.issubset(df.columns):
        pass
    elif "Sample" in df.columns:
        df = df.join(create_sample_cols(df["Sample"]))
    elif "Label ID" in df.columns:
        df = df.join(create_sample_cols(df["Label ID"]))
    else:
        raise ValueError("File does not have the expected columns.")
    return df


def valid_sample_value(name):
    if isinstance(name, str):
        if pd.notna(name):
            name = re.sub(r"-#\d*", "", name)
            name = re.sub(r", [0-9]+[-–][0-9]+$", "", name)

    if name is None:
        return True
    elif name is np.NaN:
        return True
    elif name == "No data this hole":
        return True
    elif re.search(sample_hole_regex, name):
        return True
    elif re.search(sample_core_regex, name):
        return True
    elif re.search(sample_type_regex, name):
        return True
    elif re.search(sample_sect_regex, name):
        return True
    elif re.search(sample_no_type_aw_regex, name):
        return True
    elif re.search(sample_aw_regex, name):
        return True
    else:
        # print("bad", name)
        return False


def extract_sample_parts(name):
    if isinstance(name, str):
        name = re.sub(r"-#\d*", "", name)

    if name is None or name == "No data this hole" or name is np.NaN:
        result = re.search(invalid_sample_regex, "")
    elif re.search(sample_hole_regex, name):
        result = re.search(sample_hole_regex, name)
    elif re.search(sample_core_regex, name):
        result = re.search(sample_core_regex, name)
    elif re.search(sample_type_regex, name):
        result = re.search(sample_type_regex, name)
    elif re.search(sample_sect_regex, name):
        result = re.search(sample_sect_regex, name)
    elif re.search(sample_no_type_aw_regex, name):
        result = re.search(sample_no_type_aw_regex, name)
    elif re.search(sample_aw_regex, name):
        result = re.search(sample_aw_regex, name)
    else:
        result = re.search(invalid_sample_regex, name)

    return result.groups()


def create_sample_cols(series):
    """Extract Exp...A/W info from a panda series"""
    df = pd.DataFrame(
        {
            "Exp": [],
            "Site": [],
            "Hole": [],
            "Core": [],
            "Type": [],
            "Section": [],
            "A/W": [],
        }
    )

    for item in series.to_list():
        if pd.notna(item):
            item = re.sub(r", [0-9]+[-–][0-9]+$", "", item)

        parts = extract_sample_parts(item)
        parts_dict = {
            "Exp": parts[0],
            "Site": parts[1],
            "Hole": parts[2],
            "Core": parts[3],
            "Type": parts[4],
            "Section": parts[5],
            "A/W": parts[6],
        }
        temp = pd.DataFrame([parts_dict])
        df = pd.concat([df, temp], ignore_index=True)

    if not all([valid_sample_value(x) for x in series]):
        raise ValueError("Sample name uses wrong format.")

    return df


def restore_integer_columns(df):
    """
    When there are NAs in a column of integers, pandas will convert the column
    into floats. The function restores the column of converted floats back to
    integers.
    https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html
    """
    for col in df.columns:
        try:
            df[col] = df[col].astype("Int64")
        except TypeError:
            pass
        except ValueError:
            pass
    return df


def update_metadata(metadata, new_col_dict):
    """Only update metadata if column doesn't exist"""
    new_metadata = pd.DataFrame(new_col_dict)
    new_col_name = list(new_col_dict.keys())[0]

    if new_col_name not in metadata.columns:
        metadata = metadata.join(new_metadata)

    return metadata


def replace_unnamed_xx_columns(df):
    """
    pandas will add "Unnamed: xx" as column name for columns without names.
    This function replaces "Unnamed: xx" with "".
    """
    cols = df.columns
    new_cols = ["" if re.search(r"Unnamed: \d+", col) else col for col in cols]
    df.columns = new_cols
    return df


def restore_duplicate_column_names(df, original_columns):
    """
    Pandas do not allow duplicate column names. If there are duplicate columns
    in a csv, pd.read_csv keeps the first appearance of a column name, and
    renames subsequent columns by appending .<number>
    https://github.com/pandas-dev/pandas/issues/19383

    This function replaces renamed columns with the original column name.
    """

    current_columns = df.columns
    diff_columns = set(current_columns) - set(original_columns)

    for column in diff_columns:
        # looks for columns renamed by pandas ("foo bar.1")
        if re.match(r".*\.\d+$", column):
            # gets original name of the column ("foo bar")
            original_name = re.sub(r"\.\d+$", "", column)
            if original_name in original_columns:
                cols = {column: original_name}
                df = df.rename(columns=cols)
    return df


def compare_and_restore_duplicate_column_names(df, csv_path):
    if any([col.endswith(".1") for col in df.columns]):
        csv_data = pd.read_csv(csv_path, header=None, nrows=1, dtype=str)
        original_columns = csv_data.iloc[0].to_list()
        df = restore_duplicate_column_names(df, original_columns)
    return df


def csv_cleanup(df, csv_path):
    df = compare_and_restore_duplicate_column_names(df, csv_path)
    df = restore_integer_columns(df)
    return replace_unnamed_xx_columns(df)


def normalize_columns(df, columns_mapping):
    """Replace variations of column name with a standard column name"""
    temp = {}
    for col in df.columns:
        if col in columns_mapping:
            value = columns_mapping[col]
            if value and value == value:
                temp[col] = value

    if len(temp) > 0:
        df.rename(columns=temp, inplace=True)


def fetch_unique_column_names(path, columns_set):
    content = pd.read_csv(path, dtype=str)
    content = csv_cleanup(content, path)
    return columns_set.update(set(content.columns))


def append_set(my_set, regex, all_columns):
    [my_set.add(col) for col in all_columns if re.match(regex, col, re.IGNORECASE)]


def filter_existing_set(my_set, regex):
    return {item for item in my_set if not re.match(regex, item, re.IGNORECASE)}


def add_missing_columns(path, normalized_columns):
    """Add columns to dataframe so every dataframe has the same columns"""
    content = pd.read_csv(path, dtype=str)
    columns = list(content.columns)

    missing_columns = list(set(normalized_columns) - set(columns))
    content = content.reindex(columns=columns + missing_columns)

    changed = len(columns) != len(content.columns)

    if changed:
        content = csv_cleanup(content, path)
        content.to_csv(path, index=False)

    return changed


def delete_duplicate_columns(df):
    for column in df.columns:
        # looks for columns renamed by pandas ("foo bar.1")
        if re.match(r".*\.\d+$", column):
            # gets original name of the column ("foo bar")
            original_name = re.sub(r"\.\d+$", "", column)
            original_name = original_name.strip()
            if original_name in df.columns:
                # delete column if values are identical
                if df[original_name].fillna("").equals(df[column].fillna("")):
                    del df[column]

        # look for columns with leading or trailing space
        if column.strip() != column:
            strip_column = column.strip()
            if strip_column in df.columns:
                if df[strip_column].fillna("").equals(df[column].fillna("")):
                    del df[column]


def check_duplicate_columns(df, filename):
    """
    Pandas do not allow duplicate column names. If there are duplicate columns
    in a csv, pd.read_csv keeps the first appearance of a column name, and
    renames subsequent columns by appending .<number>
    https://github.com/pandas-dev/pandas/issues/19383
    """
    bad_columns = []
    for column in df.columns:
        # looks for columns renamed by pandas ("foo bar.1")
        if re.match(r".*\.\d+$", column):
            # gets original name of the column ("foo bar")
            original_name = re.sub(r"\.\d+$", "", column)
            if original_name in df.columns:
                source = f"{filename}, {original_name}"
                if df[original_name].fillna("").equals(df[column].fillna("")):
                    print(f"{source}: duplicate columns have same values")
                    bad_columns.append(
                        {"filename": filename, "bad_column": column, "same_value": True}
                    )
                else:
                    print(f"{source}: duplicate columns have different values")
                    bad_columns.append(
                        {
                            "filename": filename,
                            "bad_column": column,
                            "same_value": False,
                        }
                    )

        # look for columns with leading or trailing space
        elif column.strip() != column:
            strip_column = column.strip()
            if strip_column in df.columns:
                source = f"{filename}, {column}"
                if df[strip_column].fillna("").equals(df[column].fillna("")):
                    print(f"{source}: duplicate columns have same values")
                    bad_columns.append(
                        {
                            "filename": filename,
                            "bad_column": column,
                            "same_value": True,
                        }
                    )
                else:
                    print(f"{source}: duplicate columns have different values")
                    bad_columns.append(
                        {
                            "filename": filename,
                            "bad_column": column,
                            "same_value": False,
                        }
                    )

    return bad_columns


def get_taxonomy_columns(columns, skip_columns):
    filtered_columns = [col for col in columns if not col.startswith("Unnamed:")]
    return [col for col in filtered_columns if col not in skip_columns]


def clean_taxon_name(string):
    string = string.strip()
    string = re.sub(" {2,}", " ", string)
    return string


def taxa_needs_review(string):
    if re.match(r"^(.*) +\(.*\)$", string):
        return True
    elif re.search(r" *> *\d+ *m$", string):
        return True
    elif re.search("_[A-Z]_?$", string):
        return True
    else:
        return False


def change_file_encoding(file):
    with open(file, "rb") as f:
        content_bytes = f.read()
    detected = chardet.detect(content_bytes)
    encoding = detected["encoding"]
    content_text = content_bytes.decode(encoding)

    with open(file, "w", encoding="utf-8") as f:
        f.write(content_text)


def get_non_taxa_fields(df, target_column):
    non_taxa_dict = {}

    df = df.dropna(subset=["normalized"])
    df = df.dropna(subset=[target_column])
    for index, row in df.iterrows():
        values = set()
        values.update(row[target_column].split(" | "))
        for value in values:
            non_taxa_dict[value] = row["normalized"]

    return non_taxa_dict


def remove_whitespace(df):
    """remove leading and trailing spaces from dataframe rows"""
    for col in df.columns:
        # only process string columns
        if df[col].dtype == "object":
            if len(df[df[col].isna()]) > 0:
                df[col].fillna("", inplace=True)

            try:
                df[col] = df[col].map(str.strip)
            except TypeError:
                print('Must call fillna("") before using whitespace_remover.')


def remove_bracket_text(df):
    """remove trailing text inside brackets."""
    df.replace(r" *\[.*\] *$", "", regex=True, inplace=True)
    return df


def remove_empty_unnamed_columns(df):
    for col in df.columns:
        if re.match(r"^Unnamed: \d+$", col):
            if len(df[col].dropna(how="all")) == 0:
                del df[col]


def print_df(df, num_rows=5):
    print(df.shape)
    return df.head(num_rows)


def normalize_abundance_codes(
    df, file_taxon_group, codes_df, verbatim_names_taxon_groups, path=None
):
    changed = False

    exps = df["Exp"].unique()
    if len(exps) > 1:
        print("multiple expeditions: ", path, exps)
    exp = exps[0]

    verbatim_names = verbatim_names_taxon_groups.keys()
    taxa_cols = list(set(df.columns).intersection(set(verbatim_names)))
    if len(taxa_cols) == 0:
        return {"changed": changed, "df": df}

    codes_filter_df = codes_df[(codes_df["expedition"] == exp)]

    for taxon in taxa_cols:
        # get taxon groups vetted by the PIs
        groups = verbatim_names_taxon_groups[taxon]

        if len(groups) == 0:
            raise (ValueError(f"{taxon} does not have taxon groups."))

        # if taxa has one taxon group, use PI approved taxon group
        if len(groups) == 1:
            codes_filter_df = codes_df[
                (codes_df["expedition"] == exp) & (codes_df["taxon_group"] == groups[0])
            ]
            for ind, row in codes_filter_df.iterrows():
                if row["taxon_group"] != groups[0]:
                    continue

                # update abundance code for a particular taxon
                taxa_filter_df = df[taxon]
                df[taxon] = taxa_filter_df.replace(
                    to_replace=row["original_abundance"],
                    value=row["normalized_abundance"],
                    regex=False,
                )
                if not taxa_filter_df.fillna("").equals(df[taxon].fillna("")):
                    changed = True

        # if taxa has multiple taxon groups
        elif len(groups) > 1:
            codes_filter_df = codes_df[
                (codes_df["expedition"] == exp)
                & (codes_df["taxon_group"] == file_taxon_group)
            ]
            for ind, row in codes_filter_df.iterrows():
                if file_taxon_group not in groups:
                    raise (
                        ValueError(f"{taxon} does not belong to {file_taxon_group}.")
                    )

                # update abundance code for a particular taxon
                taxa_filter_df = df[taxon]
                df[taxon] = taxa_filter_df.replace(
                    to_replace=row["original_abundance"],
                    value=row["normalized_abundance"],
                    regex=False,
                )

                if not taxa_filter_df.fillna("").equals(df[taxon].fillna("")):
                    changed = True

    return {"changed": changed, "df": df}


def normalize_abundance_codes_group(df, codes_df, taxon_group, path):
    changed = False

    exps = df["Exp"].unique()
    if len(exps) > 1:
        print("multiple expeditions: ", path, exps)
    exp = exps[0]

    exp_df = codes_df[
        (codes_df["Exp"] == exp)
        & (codes_df["taxon_group"] == taxon_group)
        & (codes_df["file"].str.contains(path))
    ]

    for index, row in exp_df.iterrows():
        tmp = df[row["original_header"]]
        df[row["original_header"]] = tmp.replace(
            to_replace=row["abundance_code"],
            value=row["harmonized_code"],
            regex=False,
        )
        if not tmp.fillna("").equals(df[row["original_header"]].fillna("")):
            changed = True

    return {"changed": changed, "df": df}


def normalize_switched_abundance_preservation(
    df, codes_df, taxon_group, fixed_df, path
):
    """set Preservation and Group Abundance to what is in the fixed dataframe"""
    changed = False

    exps = df["Exp"].unique()
    if len(exps) > 1:
        print("multiple expeditions: ", path, exps)
    exp = exps[0]

    exp_df = codes_df[
        (codes_df["Exp"] == exp)
        & (codes_df["taxon_group"] == taxon_group)
        & (codes_df["file"].str.contains(path))
    ]

    if len(exp_df) > 0:
        cols = set(df.columns).intersection(set(exp_df["original_header"]))

        for col in cols:
            df[col] = fixed_df[col]
            changed = True

    return {"changed": changed, "df": df}
