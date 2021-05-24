#!/usr/bin/env python

import pandas as pd
import numpy as np

taxon_groups = [
    "nannofossils",
    "silicoflagellates",
    "ostracods",
    "ebridians",
    "chrysophyte_cysts",
    "bolboformids",
    "diatoms",
    "planktic_forams",
    "radiolarians",
    "dinoflagellates",
    "palynology",
    "benthic_forams",
]

date = "2021-05-24"

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
    "initial_comments",
    "comments",
]


def add_normalized_name_column(df):
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
    df["normalized_name"] = df["Any taxon above genus"].str.cat(
        df[fields], sep=" ", na_rep=""
    )

    # add "(descriptor)" if it exists
    descriptor = np.where(
        df["non-taxa descriptor"].notnull(), "(" + df["non-taxa descriptor"] + ")", ""
    )
    df["normalized_name"] = df["normalized_name"] + descriptor

    # get rid of extra spaces
    df["normalized_name"] = df["normalized_name"].str.strip()
    df["normalized_name"] = df["normalized_name"].replace(
        to_replace="  +", value=" ", regex=True
    )

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
