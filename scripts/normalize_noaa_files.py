from pathlib import Path
import pandas as pd


def unique_filenames(paths):
    """Find all the unique filenames for a list of paths"""
    index = filename_index(paths[0])

    files = set()
    for path in paths:
        filename = Path(path).parts[index]
        files.add(filename)

    return files


def unique_columns(paths):
    """Find all the unique column names for a list of paths"""
    columns = set()
    for path in paths:
        df = pd.read_csv(path, nrows=1)
        columns.update(df.columns)

    return columns


def filename_index(path):
    """Find the index for the filename for a given path string"""
    return len(Path(path).parts) - 1


def format_filepaths_set(data, type):
    """Convert a set of filepaths into a string"""
    if data[type]:
        value = ",".join(list(data[type]))
    else:
        value = ""

    return value
