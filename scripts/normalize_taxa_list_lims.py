#!/usr/bin/env python

import pandas as pd
import numpy as np


TAXON_GROUPS = [
    "nannofossils",
    "silicoflagellates",
    "ostracods",
    "ebridians",
    "chrysophyte_cysts",
    "bolboformids",
    "diatoms",
    "planktic_forams",
    "radiolarians",
]
DATE = "2021-05-05"

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
    "processing_notes",
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


input_file = (
    f"notebooks/raw_data/taxa/Micropal_headers_PBDB_Taxonomy_notes_taxa_list_{DATE}.csv"
)
for taxon_group in TAXON_GROUPS:
    crosswalk_file = (
        f"notebooks/cleaned_data/taxa/taxa_crosswalk_{taxon_group}_{DATE}.csv"
    )
    taxa_list_file = f"notebooks/cleaned_data/taxa/taxa_list_{taxon_group}_{DATE}.csv"

    # skip and drop rows with bad data
    df = pd.read_csv(input_file, skiprows=9)
    df = df.drop(list(range(28)))

    # setup the columns
    dict = {"Comment": "initial_comments", "notes": "processing_notes"}
    df.rename(columns=dict, inplace=True)
    df["normalized_name"] = np.nan

    # select taxa for one taxa group
    filtered_df = df[df["taxon_group"] == taxon_group]

    # create csvs
    fields = taxa_rank_fields + taxa_fields + metadata_fields
    crosswalk_taxa = create_crosswalk_taxa_csv(
        data=filtered_df, path=crosswalk_file, columns=fields
    )

    fields = taxa_rank_fields + taxa_fields
    create_unique_taxa_csv(data=crosswalk_taxa, path=taxa_list_file, columns=fields)
