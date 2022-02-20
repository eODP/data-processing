#!/usr/bin/env python

import os
import pandas as pd
import fire

import normalize_taxa as nt

taxa_dir = ["notebooks", "cleaned_data", "taxa", "LIMS"]


class TaxaList:
    def read_PI_taxa_list(self, date):
        input_file = os.path.join(
            "notebooks",
            "raw_data",
            "taxa",
            f"LIMS_Micropal_headers_PBDB_Taxonomy_notes_taxa_list_{date}.csv",
        )
        # skip and drop rows with bad data
        df = pd.read_csv(input_file, skiprows=9, dtype=str)
        df = df.drop(df.index[[0, 1]])
        df = df.dropna(how="all", axis="index")

        return df

    def get_taxon_groups(self, df):
        """get a list of taxon groups that have been approved by the PIs."""
        non_blank_df = df.dropna(axis="index", how="all", subset=nt.taxa_rank_fields)

        return list(non_blank_df["taxon_group"].unique())

    def generate_taxon_group_taxa_lists(self, date):
        """use the taxa list  from the PIs to create a taxa list for each taxon group"""
        df = self.read_PI_taxa_list(date)
        taxon_groups = self.get_taxon_groups(df)

        for taxon_group in taxon_groups:
            crosswalk_file = os.path.join(
                *taxa_dir, f"taxa_crosswalk_{taxon_group}_{date}.csv"
            )

            taxa_list_file = os.path.join(
                *taxa_dir, f"taxa_list_{taxon_group}_{date}.csv"
            )

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

    def generate_taxa_list_from_taxon_groups(self, date, mode="write"):
        """create taxa list by combining the separate taxon group taxa lists"""
        taxa_file = os.path.join(*taxa_dir, f"combined_taxa_list_{date}.csv")

        # append existing taxa file or create new taxa file
        if mode == "append":
            df = pd.read_csv(taxa_file, dtype=str)
        else:
            df = pd.DataFrame()

        pi_df = self.read_PI_taxa_list(date)
        taxon_groups = self.get_taxon_groups(pi_df)

        # combine all taxon group taxa lists
        for taxon_group in taxon_groups:
            crosswalk_file = os.path.join(
                *taxa_dir, f"taxa_crosswalk_{taxon_group}_{date}.csv"
            )
            taxa_df = pd.read_csv(crosswalk_file, dtype=str)
            df = pd.concat([df, taxa_df])

        df.to_csv(taxa_file, index=False)

    def generate_taxa_list(self, date):
        """create taxa list for all taxon groups by processing the taxa list
        from the PIs"""
        taxa_file = os.path.join(*taxa_dir, f"taxa_list_{date}.csv")
        crosswalk_file = os.path.join(*taxa_dir, f"taxa_crosswalk_{date}.csv")

        taxa_df = self.read_PI_taxa_list(date)

        # create csvs
        fields = nt.taxa_rank_fields + nt.taxa_fields + nt.metadata_fields
        crosswalk_taxa = nt.create_crosswalk_taxa_csv(
            data=taxa_df, path=crosswalk_file, columns=fields
        )

        fields = nt.taxa_rank_fields + nt.taxa_fields
        nt.create_unique_taxa_csv(data=crosswalk_taxa, path=taxa_file, columns=fields)


if __name__ == "__main__":
    fire.Fire(TaxaList)
