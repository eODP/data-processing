#!/usr/bin/env python

import pandas as pd
import numpy as np

# taxon_groups = [
#     "benthic_foraminfera",
#     "bolboformids",
#     "chrysophyte_cysts",
#     "diatoms",
#     "dinoflagellates",
#     "dinoflagellates/acritarchs/prasinophytes",
#     "ebridians",
#     "nannofossils",
#     "ostracods",
#     "palynology",
#     "phytoliths",
#     "planktic_foraminfera",
#     "pollen",
#     "pteropods",
#     "radiolarians",
#     "silicoflagellates",
# ]


taxa_rank_fields = [
    "Any taxon above genus",
    "genus modifier",
    "genus name",
    "subgenera modifier",
    "subgenera name",
    "species modifier",
    "species name",
    "subspecies modifier",
    "subspecies name",
]

taxa_fields = ["non-taxa descriptor", "normalized_name", "taxon_group"]

metadata_fields = [
    "verbatim_name",
    "comments",
]


def add_normalized_name_column(df, include_descriptor=True, col_name="normalized_name"):
    fields = [
        "genus modifier",
        "genus name",
        "subgenera modifier",
        "subgenera name",
        "species modifier",
        "species name",
        "subspecies modifier",
        "subspecies name",
    ]

    # concatenate taxa fields into a string
    df[col_name] = df["Any taxon above genus"].str.cat(df[fields], sep=" ", na_rep="")

    if include_descriptor:
        # add "(descriptor)" if it exists
        descriptor = np.where(
            df["non-taxa descriptor"].notnull(),
            "(" + df["non-taxa descriptor"] + ")",
            "",
        )
        df[col_name] = df[col_name] + descriptor

    # get rid of extra spaces
    df[col_name] = df[col_name].str.strip()
    df[col_name] = df[col_name].replace(to_replace="  +", value=" ", regex=True)

    return df


def create_crosswalk_taxa_csv(data, path, columns):
    """create csv with unique verbatim_name from the LIMS files and
    normalized_name from the eODP researchers
    """
    df = pd.DataFrame(data, columns=columns)

    add_normalized_name_column(df)
    df = df.drop(df[df["normalized_name"] == ""].index)
    df = df.drop_duplicates(keep="first", subset=["verbatim_name", "normalized_name"])
    df.to_csv(path, index=False)

    return df


def create_unique_taxa_csv(data, path, columns):
    """create csv with unique normalized_name from the eODP researchers"""
    df = pd.DataFrame(data, columns=columns)
    df = df.drop_duplicates()
    df.to_csv(path, index=False)

    return df
