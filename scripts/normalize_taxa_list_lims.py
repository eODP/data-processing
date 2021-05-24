#!/usr/bin/env python

import pandas as pd
import numpy as np

import normalize_taxa as nt


input_file = f"notebooks/raw_data/taxa/Micropal_headers_PBDB_Taxonomy_notes_taxa_list_{nt.date}.csv"

for taxon_group in nt.taxon_groups:
    crosswalk_file = (
        f"notebooks/cleaned_data/taxa/taxa_crosswalk_{taxon_group}_{nt.date}.csv"
    )
    taxa_list_file = (
        f"notebooks/cleaned_data/taxa/taxa_list_{taxon_group}_{nt.date}.csv"
    )

    # skip and drop rows with bad data
    df = pd.read_csv(input_file, skiprows=9)

    # setup the columns
    dict = {"Comment": "initial_comments"}
    df.rename(columns=dict, inplace=True)
    df["normalized_name"] = np.nan

    # select taxa for one taxa group
    filtered_df = df[df["taxon_group"] == taxon_group]

    # create csvs
    fields = nt.taxa_rank_fields + nt.taxa_fields + nt.metadata_fields
    crosswalk_taxa = nt.create_crosswalk_taxa_csv(
        data=filtered_df, path=crosswalk_file, columns=fields
    )

    fields = nt.taxa_rank_fields + nt.taxa_fields
    nt.create_unique_taxa_csv(data=crosswalk_taxa, path=taxa_list_file, columns=fields)
