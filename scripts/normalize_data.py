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
