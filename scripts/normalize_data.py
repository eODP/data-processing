import re
import os
import numpy as np
import pandas as pd


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


def create_sample_name(df):
    names = {"Exp", "Site", "Hole", "Core", "Type", "Section", "A/W"}
    if names.issubset(df.columns):
        dash = ["-" for i in range(len(df))]

        # NOTE: must convert all columns to strings to handle None
        df["Sample"] = (
            df["Exp"].astype(str)
            + dash
            + df["Site"].astype(str)
            + df["Hole"].astype(str)
            + dash
            + df["Core"].astype(str)
            + df["Type"].astype(str)
            + dash
            + df["Section"].astype(str)
            + dash
            + df["A/W"].astype(str)
        )

        # NOTE: Remove the string version of None;
        # NOTE: a None value in an integer column will convert all integers to
        # floats. Remove the float decimal.
        df["Sample"] = df["Sample"].map(
            lambda a: str(a).replace("nan", "").replace(".0", "").replace("None", "")
        )
        df["Sample"] = df["Sample"].str.replace(r"([\d\w])--+", r"\1-", regex=True)
        df["Sample"] = df["Sample"].str.replace(r"-$", "", regex=True)

    else:
        raise ValueError("File does not have the expected columns.")


def get_expedition_from_csv(df):
    if "Label ID" in df.columns:
        expedition = df["Label ID"]
    elif "Sample" in df.columns:
        expedition = df["Sample"]
    elif "Exp" in df.columns:
        expedition = df["Exp"]
    else:
        raise ValueError("File does not expedition info.")

    return expedition[0].split("-")[0]


def normalize_expedition_section_cols(df):
    # NOTE: There was one file that did not have A/W column
    names = {"Exp", "Site", "Hole", "Core", "Type", "Section"}
    if names.issubset(df.columns):
        pass
    elif "Sample" in df.columns:
        df = df.join(extract_sample_parts(df["Sample"]))
    elif "Label ID" in df.columns:
        df = df.join(extract_sample_parts(df["Label ID"]))
    else:
        raise ValueError("File does not have the expected columns.")
    return df


def valid_sample_value(x):
    if x is None:
        return True

    if x is np.NaN:
        return True

    if x == "No data this hole":
        return True

    regex = r"(^\d+)-(U\d+)(\w)-?(\d+)?(\w)?-?([\d\w]+)?-?(\w)?"
    return re.search(regex, x) is not None


def extract_sample_parts(df):
    # matches (1)-(U1)(A)-(1)(A)-(1)-(A)
    #         (1)-(U1)(A)-(1)(A)-(A)-(A)
    reg = r"(^\d+)-(U\d+)(\w)-?(\d+)?(\w)?-?([\d\w]+)?-?(\w)?"
    res = df.str.extract(reg)
    res.columns = ["Exp", "Site", "Hole", "Core", "Type", "Section", "A/W"]

    if not all([valid_sample_value(x) for x in df]):
        raise ValueError("Sample name uses wrong format.")

    return res


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


def csv_cleanup(df):
    df = restore_integer_columns(df)
    return replace_unnamed_xx_columns(df)


def normalize_columns(old_cols, new_col, all_cols):
    return [new_col if column in old_cols else column for column in all_cols]


def extract_taxon_group_from_filename(filename):
    filename_parts = re.search(
        # matches 123-U1234A-taxon-group or 123-U1234A-taxongroup
        "^[0-9]{3}[-_]+U[0-9]{4}[a-zA-Z][-_]+([a-zA-Z]+([-_ ][a-zA-Z]+)?)([_-]\d)?\.csv",
        filename,
    )

    if filename_parts is not None:
        return filename_parts.groups()[0].lower().replace("-", "_").replace(" ", "_")
    else:
        raise ValueError("Cannot extract taxon group.")


def fetch_unique_column_names(path, columns_set):
    content = pd.read_csv(path)
    content = csv_cleanup(content)
    return columns_set.update(set(content.columns))


def append_set(my_set, regex, all_columns):
    [my_set.add(col) for col in all_columns if re.match(regex, col, re.IGNORECASE)]


def filter_existing_set(my_set, regex):
    return {item for item in my_set if not re.match(regex, item, re.IGNORECASE)}


def add_missing_columns(path, normalized_columns):
    content = pd.read_csv(path)
    columns = list(content.columns)

    missing_columns = list(set(normalized_columns) - set(columns))
    content = content.reindex(columns=columns + missing_columns)

    changed = len(columns) != len(content.columns)

    if changed:
        content = csv_cleanup(content)
        content.to_csv(path, index=False)

    return changed
