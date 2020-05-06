import re
import os


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
