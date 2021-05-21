import re
import os
import numpy as np
import pandas as pd

# HACK: (@)? are meaningless matches so each regex has 8 capture groups
# (1)-(U1)(A)
# (Exp)-(Site)(Hole)
sample_hole_regex = r"(^\d+)-(U\d+)([a-zA-Z])(@)?(@)?(@)?(@)?(@)?$"
# (1)-(U1)(A)-(1)
# (Exp)-(Site)(Hole)-(Core)
sample_core_regex = r"(^\d+)-(U\d+)([a-zA-Z])-(\d+)(@)?(@)?(@)?(@)?$"
# (1)-(U1)(A)-(1)(A)
# (Exp)-(Site)(Hole)-(Core)(Type)
sample_type_regex = r"(^\d+)-(U\d+)([a-zA-Z])-(\d+)([a-zA-Z])(@)?(@)?(@)?$"
# (1)-(U1)(A)-(1)(A)-(1)
# (1)-(U1)(A)-(1)(A)-(A)
# (Exp)-(Site)(Hole)-(Core)(Type)-(Section)
sample_sect_regex = r"(^\d+)-(U\d+)([a-zA-Z])-(\d+)([a-zA-Z])-(\w+)(@)?(@)?$"
# (1)-(U1)(A)-(1)(A)-(1)-(1)
# (1)-(U1)(A)-(1)(A)-(A)-(A)
# (Exp)-(Site)(Hole)-(Core)(Type)-(Section)-(AW)
sample_aw_regex = r"(^\d+)-(U\d+)([a-zA-Z])-(\d+)([a-zA-Z])-(\w+)-(\w+)(@)?$"
# (1)-(U1)(A)-(1)(A)-(1)-(1)-(1)
# (1)-(U1)(A)-(1)(A)-(A)-(A)-(A)
# (1)-(U1)(A)-(1)(A)-(A)-(A(A))-(A)
# (Exp)-(Site)(Hole)-(Core)(Type)-(Section)-(AW)-(Extra)
sample_extra_regex = (
    r"(^\d+)-(U\d+)([a-zA-Z])-(\d+)([a-zA-Z])-(\w+)-(\w+(\([\w\-]+\))?)(.*?)$"
)
# (1)-(U1)(A)-(1)-(1)-(1)
# (1)-(U1)(A)-(1)-(A)-(A)
# (Exp)-(Site)(Hole)-(Core)-(Section)-(AW)
sample_no_type_aw_regex = r"(^\d+)-(U\d+)([a-zA-Z])-(\d+)(@)?-(\w+)-(\w+)(@)?"
invalid_sample_regex = r"(-)?(-)?(-)?(-)?(-)?(-)?(-)?(-)?"


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


def rename_label_id(df):
    if "Label ID" in df.columns:
        cols = {"Label ID": "Sample"}
        df.rename(columns=cols, inplace=True)


def add_sample_col(df):
    if "Sample" in df.columns:
        pass
    else:
        create_sample_name(df)


def create_sample_name_for_row(row, columns):
    if len(row) == 0:
        return np.nan

    name = (
        f"{row['Exp']}-{row['Site']}{row['Hole']}-"
        f"{row['Core']}{row['Type']}-{row['Section']}-{row['A/W']}"
    )

    if "Extra Sample ID Data" in columns and isinstance(
        row["Extra Sample ID Data"], str
    ):

        if row["A/W"] is not np.nan and row["A/W"].startswith("PAL"):
            name = name + "-" + row["Extra Sample ID Data"]
        else:
            name = name + " " + row["Extra Sample ID Data"]

    name = re.sub("nan", "", name)
    name = re.sub("None", "", name)
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


def get_expedition_from_csv(df):
    if "Label ID" in df.columns:
        expeditions = df["Label ID"]
    elif "Sample" in df.columns:
        expeditions = df["Sample"]
    elif "Exp" in df.columns:
        expeditions = df["Exp"]
    else:
        raise ValueError("File does not expedition info.")

    if "Label ID" in df.columns or "Sample" in df.columns:
        unique_values = set([x[0] for x in expeditions.str.split("-")])
        if len(unique_values) > 1:
            raise ValueError("File has multiple expeditions.")

        return expeditions[0].split("-")[0]
    else:
        unique_values = expeditions.unique()
        if len(unique_values) > 1:
            raise ValueError("File has multiple expeditions.")
        return expeditions[0]


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
        name = re.sub("-#\d*", "", name)

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
    elif re.search(sample_extra_regex, name):
        return True
    else:
        # print("bad", name)
        return False


def extract_sample_parts(name):
    if isinstance(name, str):
        name = re.sub("-#\d*", "", name)

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
    elif re.search(sample_extra_regex, name):
        result = re.search(sample_extra_regex, name)
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
            "Extra Sample ID Data": [],
        }
    )

    for item in series.to_list():
        parts = extract_sample_parts(item)

        if len(parts) == 9:
            extra = parts[8]
        else:
            extra = parts[7]

        if extra:
            extra = extra.strip()
            extra = re.sub("^, -|^-|^,", "", extra).strip()

        parts_dict = {
            "Exp": parts[0],
            "Site": parts[1],
            "Hole": parts[2],
            "Core": parts[3],
            "Type": parts[4],
            "Section": parts[5],
            "A/W": parts[6],
            "Extra Sample ID Data": extra,
        }
        df = df.append(parts_dict, ignore_index=True)

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
        if re.match(".*\.\d+$", column):
            # gets original name of the column ("foo bar")
            original_name = re.sub("\.\d+$", "", column)
            if original_name in original_columns:
                cols = {column: original_name}
                df = df.rename(columns=cols)
    return df


def compare_and_restore_duplicate_column_names(df, csv_path):
    if any([col.endswith(".1") for col in df.columns]):
        csv_data = pd.read_csv(csv_path, header=None, nrows=1)
        original_columns = csv_data.iloc[0].to_list()
        df = restore_duplicate_column_names(df, original_columns)
    return df


def csv_cleanup(df, csv_path):
    df = compare_and_restore_duplicate_column_names(df, csv_path)
    df = restore_integer_columns(df)
    return replace_unnamed_xx_columns(df)


def normalize_columns(old_cols, new_col, all_cols):
    """Replace variations of column name with a standard column name"""
    return [new_col if column in old_cols else column for column in all_cols]


def extract_taxon_group_from_filename(filename):
    filename = re.sub("-+", "_", filename)
    filename = re.sub(" +", "_", filename)

    filename_parts = re.search(
        # matches 123-U1234A-taxon-group or 123-U1234A-taxongroup
        "^[0-9]{3}_+U[0-9]{4}[a-zA-Z]_+([a-zA-Z]+(_[a-zA-Z]+)?)(_\d)?_?\.csv",
        filename,
    )

    if filename_parts is None:
        filename_parts = re.search(
            # matches 123-taxon-group-U1234A- or 123-taxongroup-U1234A
            "^[0-9]{3}_+([a-zA-Z]+(_[a-zA-Z]+)?)_+U[0-9]{4}[a-zA-Z](_\d)?_?\.csv",
            filename,
        )

    if filename_parts is not None:
        taxon_group = filename_parts.groups()[0].lower()
        if taxon_group == "nannofossil":
            taxon_group = "nannofossils"
        elif taxon_group == "radiolarians_events":
            taxon_group = "radiolarians"
        elif taxon_group == "nannofossils_revised":
            taxon_group = "nannofossils"
        return taxon_group
    else:
        raise ValueError("Cannot extract taxon group.")


def fetch_unique_column_names(path, columns_set):
    content = pd.read_csv(path, nrows=1)
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


def check_duplicate_columns(df, filename):
    """
    Pandas do not allow duplicate column names. If there are duplicate columns
    in a csv, pd.read_csv keeps the first appearance of a column name, and
    renames subsequent columns by appending .<number>
    https://github.com/pandas-dev/pandas/issues/19383

    This function checks if duplicate columns have the same values.
    """
    dups = []

    for column in df.columns:
        # looks for columns renamed by pandas ("foo bar.1")
        if re.match(".*\.\d+$", column):
            # gets original name of the column ("foo bar")
            original_name = re.sub("\.\d+$", "", column)
            if original_name in df.columns:
                source = f"{filename}, {original_name}"
                # check if values are equal
                if df[original_name].equals(df[column]):
                    dups.append(column)
                else:
                    print(f"{source}: duplicate columns have different values")

    df.drop(dups, axis=1, inplace=True)
    return df


def get_taxonomy_columns(columns, skip_columns):
    filtered_columns = [col for col in columns if not col.startswith("Unnamed:")]
    return [col for col in filtered_columns if col not in skip_columns]


def clean_taxon_name(string):
    string = string.strip()
    string = re.sub(" {2,}", " ", string)
    return string


def taxa_needs_review(string):
    if re.match("^(.*) +\(.*\)$", string):
        return True
    elif re.search(" *> *\d+ *m$", string):
        return True
    elif re.search("_[A-Z]_?$", string):
        return True
    else:
        return False
