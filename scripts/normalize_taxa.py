#!/usr/bin/env python

import pandas as pd
import re

from scripts.normalize_data import remove_whitespace

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

# taxon_groups includes LIMS processed taxa
taxon_groups = [
    "benthic_forams",
    "bolboformids",
    "chrysophyte_cysts",
    "diatoms",
    "dinoflagellates",
    "ebridians",
    "nannofossils",
    "ostracods",
    "palynology",
    "planktic_forams",
    "radiolarians",
    "silicoflagellates",
]

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
    "name comment field",
    "Comment",
    "Notes (change to Internal only notes?)",
    "comments",
]

pdbd_fields = [
    "pbdb_taxon_id",
    "pbdb_taxon_name",
    "pbdb_taxon_rank",
    "family_taxon_id",
    "family_taxon_name",
    "order_taxon_id",
    "order_taxon_name",
    "class_taxon_id",
    "class_taxon_name",
    "phylum_taxon_id",
    "phylum_taxon_name",
    "kingdom_taxon_id",
    "kingdom_taxon_name",
]


def add_normalized_name_column(
    df, include_descriptor=True, include_modifier=True, col_name="normalized_name"
):
    if include_modifier:
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
    else:
        fields = [
            "genus name",
            "subgenera name",
            "species name",
            "subspecies name",
        ]
    temp_df = df.copy()
    temp_df.fillna("", inplace=True)

    # concatenate taxa fields into a string
    df[col_name] = temp_df["Any taxon above genus"].str.cat(
        temp_df[fields], sep=" ", na_rep=""
    )

    if include_descriptor:
        descriptor = "non-taxa descriptor"
        df.loc[
            (temp_df[descriptor] != "") & (~temp_df[descriptor].str.contains("\(")),
            col_name,
        ] = (
            df[col_name] + " (" + temp_df[descriptor] + ")"
        )
        df.loc[
            (temp_df[descriptor] != "") & (temp_df[descriptor].str.contains("\(")),
            col_name,
        ] = (
            df[col_name] + " " + temp_df[descriptor]
        )

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


def taxon_name_parser(taxon_name):
    name_parts = {}
    modifiers = ["?", "aff.", "cf.", "f.", "morph", "s.s.", "s.l.", "var."]
    ranks = ["genus", "species", "subspecies"]

    if bool(re.search(r"\(.*?\)$", taxon_name)):
        descriptor = re.search("\(.*?\)$", taxon_name).group(0)
        name_parts["non-taxa descriptor"] = descriptor
        taxon_name = taxon_name.split(descriptor)[0].strip()

    parts = taxon_name.split(" ")

    current_rank_index = 0
    for index, part in enumerate(parts):
        if current_rank_index == 3:
            continue

        if part in modifiers:
            name_parts[ranks[current_rank_index] + " modifier"] = parts[index]
        else:
            name_parts[ranks[current_rank_index] + " name"] = parts[index]
            current_rank_index += 1

    if bool(re.search(r"\(.*?\)$", taxon_name)):
        descriptor = re.search(r"\(.*?\)$", taxon_name).group(0)
        name_parts["non-taxa descriptor"] = descriptor

    return name_parts


def create_taxa_crosswalk_df(df):
    fields = taxa_rank_fields + taxa_fields + metadata_fields
    print("fields:", fields)

    filtered_taxa = pd.DataFrame(df, columns=fields)
    remove_whitespace(filtered_taxa)
    print("initial df: ", filtered_taxa.shape)

    add_normalized_name_column(filtered_taxa)

    filtered_taxa = filtered_taxa.drop(
        filtered_taxa[filtered_taxa["normalized_name"] == ""].index
    )
    print("remove nontaxa df: ", filtered_taxa.shape)

    filtered_taxa.drop_duplicates(
        keep="first",
        inplace=True,
        subset=["verbatim_name", "normalized_name", "taxon_group"],
    )
    print("drop duplicates df: ", filtered_taxa.shape)

    return filtered_taxa


def create_taxa_list_df(df):
    fields = taxa_rank_fields + taxa_fields + pdbd_fields
    print("fields:", fields)

    filtered_taxa = pd.DataFrame(df, columns=fields)
    remove_whitespace(filtered_taxa)
    print("initial df: ", filtered_taxa.shape)

    add_normalized_name_column(filtered_taxa)

    filtered_taxa = filtered_taxa.drop(
        filtered_taxa[filtered_taxa["normalized_name"] == ""].index
    )
    print("remove nontaxa df: ", filtered_taxa.shape)

    filtered_taxa.drop_duplicates(
        keep="first", inplace=True, subset=["normalized_name", "taxon_group"]
    )
    print("drop duplicates df: ", filtered_taxa.shape)

    return filtered_taxa
