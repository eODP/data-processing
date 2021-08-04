from pathlib import Path
import pandas as pd
import re


def unique_filenames_for_paths(paths):
    """Find all the unique filenames for a list of paths"""
    index = filename_index(paths[0])

    files = set()
    for path in paths:
        filename = Path(path).parts[index]
        files.add(filename)

    return files


def unique_columns_for_paths(paths, sep=","):
    """Find all the unique column names for a list of paths"""
    columns = set()
    for path in paths:
        df = pd.read_csv(path, nrows=1, sep=sep)
        columns.update(df.columns)

    return columns


def column_counts_for_paths(paths):
    """Returns the unique number of columns for a list of paths"""
    counts = set()
    for path in paths:
        df = pd.read_csv(path, nrows=0)
        counts.add(len(df.columns))

    return counts


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


def qa_files_for_paths(paths, expected_fields, sep=","):
    results = {
        "bad_encoding": [],  # does not use utf-8 encoding
        "bad_tabs": [],  # rows have different number of columns than headers
        "space_delim": [],  # uses spaces as delimiter
        "missing_fields": [],  # does not have all the fields
        "good_files": [],
        "unnamed_column": []
    }

    for file in paths:
        try:
            df = pd.read_csv(file, delimiter=sep, nrows=3)
        except UnicodeDecodeError:
            results["bad_encoding"].append(file)
            continue
        except pd.errors.ParserError:
            results["bad_tabs"].append(file)
            continue

        expected_fields = {re.sub(" {2,}", " ", field) for field in expected_fields}
        columns = [re.sub(" {2,}", " ", col) for col in df.columns]

        if len([col for col in columns if col.startswith('Unnamed')]) > 0:
            results["unnamed_column"].append(file)
        elif expected_fields.issubset(columns):
            results["good_files"].append(file)
        elif len(df.columns) == 1:
            results["space_delim"].append(file)
        else:
            results["missing_fields"].append(file)

    return results
