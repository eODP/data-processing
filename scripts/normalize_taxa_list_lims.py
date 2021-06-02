#!/usr/bin/env python

import os
import pandas as pd
import numpy as np
import fire

import normalize_taxa as nt

input_file = f"notebooks/raw_data/taxa/Micropal_headers_PBDB_Taxonomy_notes_taxa_list_{nt.date}.csv"
metadata_file = "notebooks/cleaned_data/metadata/LIMS/Micropal_changes.csv"
taxa_dir = "notebooks/cleaned_data/taxa"

df = pd.read_csv(metadata_file)
taxon_groups = df["taxon_group"].unique()


class TaxaList:
    def generate_taxon_group_taxa_files(self):
        for taxon_group in taxon_groups:
            crosswalk_file = (
                f"{taxa_dir}/LIMS/taxa_crosswalk_{taxon_group}_{nt.date}.csv"
            )
            taxa_list_file = f"{taxa_dir}/LIMS/taxa_list_{taxon_group}_{nt.date}.csv"

            # skip and drop rows with bad data
            df = pd.read_csv(input_file, skiprows=9)

            # setup the columns
            dict = {"Comment": "initial_comments"}
            df.rename(columns=dict, inplace=True)
            df["normalized_name"] = np.nan

            # update taxon_group
            df["taxon_group"] = df["taxon_group"].apply(nt.update_taxon_group)

            # select taxa for one taxon group
            filtered_df = df[df["taxon_group"] == taxon_group]

            # create csvs
            fields = nt.taxa_rank_fields + nt.taxa_fields + nt.metadata_fields
            crosswalk_taxa = nt.create_crosswalk_taxa_csv(
                data=filtered_df, path=crosswalk_file, columns=fields
            )

            fields = nt.taxa_rank_fields + nt.taxa_fields
            nt.create_unique_taxa_csv(
                data=crosswalk_taxa, path=taxa_list_file, columns=fields
            )

    def generate_approved_taxa_list(self, mode="write"):
        """create taxa list by combining the taxon group taxa lists"""
        taxa_file = f"{taxa_dir}/approved_eodp_taxa_list.csv"

        # append existing taxa file or create new taxa file
        if mode == "append":
            df = pd.read_csv(taxa_file)
        else:
            df = pd.DataFrame()

        # combine all taxon group taxa lists
        for taxon_group in taxon_groups:
            crosswalk_file = (
                f"{taxa_dir}/LIMS/taxa_crosswalk_{taxon_group}_{nt.date}.csv"
            )
            taxa_df = pd.read_csv(crosswalk_file)
            df = pd.concat([df, taxa_df])

        df.to_csv(taxa_file, index=False)


if __name__ == "__main__":
    fire.Fire(TaxaList)
