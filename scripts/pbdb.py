import requests
import numpy as np
import pandas as pd
import time

PBDB_API = "https://paleobiodb.org/data1.2/"
PBDB_TAXA_NAME = f"{PBDB_API}taxa/single.json?vocab=pbdb&name="
PBDB_TAXA_ID = f"{PBDB_API}taxa/single.json?vocab=pbdb&id="
PBDB_TAXA_LIST_NAME = f"{PBDB_API}taxa/list.json?show=class&rel=all_parents&name="
PBDB_TAXA_LIST_ID = f"{PBDB_API}taxa/list.json?show=class&rel=all_parents&id="

rank_ids = {
    20: "phylum",
    19: "subphylum",
    18: "superclass",
    17: "class",
    13: "order",
    5: "genus",
    9: "family",
    3: "species",
    8: "subfamily",
    25: "unranked clade",
    23: "kingdom",
    21: "phylum",
    12: "suborder",
    10: "superfamily",
    16: "subclass",
    15: "infraclass",
    14: "superorder",
    11: "infraorder",
    22: "subkingdom",
    4: "subgenus",
    2: "subspecies",
    7: "tribe",
}


def fill_taxon(df, index, data, taxon_rank):
    # cast taxon_no to string to avoid pandas converting it to a float
    df.at[index, f"{taxon_rank}_taxon_id"] = str(data[0]["taxon_no"])
    df.at[index, f"{taxon_rank}_taxon_name"] = data[0]["taxon_name"]


def get_parent_taxa(df, parent_id, taxon_rank, round, index, data):
    if taxon_rank == "kingdom":
        return data
    elif parent_id == "0":
        return data
    elif round > 20:
        return data

    round = round + 1

    url_parent = PBDB_TAXA_ID + parent_id
    response = requests.get(url_parent)
    if response.status_code == 200:
        data = response.json()["records"]
        if len(data) == 1:
            taxon_rank = data[0]["taxon_rank"]
            parent_id = data[0]["parent_no"]
            if taxon_rank in ["genus", "family", "order", "class", "phylum", "kingdom"]:
                fill_taxon(df, index, data, taxon_rank)
            elif parent_id == "0":
                fill_taxon(df, index, data, taxon_rank)

            return get_parent_taxa(df, parent_id, taxon_rank, round, index, data)


def fix_pbdb_id(
    df, correction_text, correct_id, correct_col="Corrections to pbdb_taxon_id"
):
    """look up pbdb data for taxon id. update dateframe with new pdbd"""
    print(correct_id)
    columns = [
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
        "unranked clade_taxon_id",
        "unranked clade_taxon_name",
    ]

    col = correct_col
    url_parent = PBDB_TAXA_LIST_ID + str(correct_id)
    response = requests.get(url_parent)
    if response.status_code == 200:
        data = response.json()["records"]

        if len(data) > 0:
            last_record = data[len(data) - 1]

            for taxa_col in columns:
                df.loc[df[col] == correction_text, taxa_col] = np.nan

            df.loc[df[col] == correction_text, "pbdb_taxon_name"] = last_record["nam"]
            df.loc[df[col] == correction_text, "pbdb_taxon_rank"] = rank_ids[
                last_record["rnk"]
            ]
            df.loc[df[col] == correction_text, "pbdb_taxon_id"] = correct_id

            for index, row in df[df[col] == correction_text].iterrows():
                process_taxa_hierarchy(df, data, index)

    else:
        raise ValueError(f"{correct_id} ID not found")

    df.loc[df[col] == correction_text, "corrected"] = True


def check_multiple_pbdb_id(df):
    """check if pbdb data is same for each pbdb taxon id"""
    cols = [
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

    tmp = df[cols].copy().drop_duplicates()
    return tmp[tmp.duplicated(subset=["pbdb_taxon_id", "pbdb_taxon_name"])]


pbdb_cols = [
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


def create_genus_df(df):
    df["genus name"] = df["genus name"].str.strip()
    cols = [
        "taxon_group",
        "genus name",
    ] + pbdb_cols

    genus_df = df[df["genus name"].notna()].copy()
    genus_df = genus_df[cols]
    genus_df.drop_duplicates(inplace=True)

    return genus_df


def create_higher_taxa_df(df):
    df["Any taxon above genus"] = df["Any taxon above genus"].str.strip()
    cols = [
        "taxon_group",
        "Any taxon above genus",
    ] + pbdb_cols

    higher_df = df[df["Any taxon above genus"].notna() & df["genus name"].isna()].copy()
    higher_df = higher_df[cols]
    higher_df.drop_duplicates(inplace=True)

    return higher_df


def fetch_pdbd_data(df, target_col, search_type="name"):
    if 'check' not in df:
        df['check']=False

    if "pbdb_taxon_id" not in df:
        df["pbdb_taxon_id"] = pd.NA

    for index, row in df.iterrows():
        if row["check"] == "True" or row["check"] == True:
            continue

        if pd.notna(row["pbdb_taxon_id"]):
            continue

        if index % 5 == 0:
            time.sleep(0.5)

        if index % 50 == 0:
            print(index, end=" ")

        # if index > 50:
        #     break

        if search_type == "name":
            url = PBDB_TAXA_LIST_NAME + row[target_col]
        else:
            url = PBDB_TAXA_LIST_ID + row[target_col]
        # print(url)
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()["records"]
            if len(data) > 0:
                last_record = data[len(data) - 1]
                df.at[index, "pbdb_taxon_id"] = last_record["oid"].replace("txn:", "")
                df.at[index, "pbdb_taxon_name"] = last_record["nam"]
                df.at[index, "pbdb_taxon_rank"] = rank_ids[last_record["rnk"]]

                process_taxa_hierarchy(df, data, index)
        else:
            print(row[target_col], " not found")

        df.at[index, "check"] = True


def process_taxa_hierarchy(df, data, index, include_unranked_clade=False):
    for record in data:
        taxon_rank = rank_ids[record["rnk"]]
        if taxon_rank in [
            "species",
            "genus",
            "family",
            "order",
            "class",
            "phylum",
            "kingdom",
        ]:
            df.at[index, f"{taxon_rank}_taxon_id"] = record["oid"].replace("txn:", "")
            df.at[index, f"{taxon_rank}_taxon_name"] = record["nam"]
        if taxon_rank == 'unranked clade' and include_unranked_clade:
            df.at[index, f"{taxon_rank}_taxon_id"] = record["oid"].replace("txn:", "")
            df.at[index, f"{taxon_rank}_taxon_name"] = record["nam"]


def add_pbdb_data(df, pbdb_df, target_col):
    allowed_cols = pbdb_cols + [
        "genus_taxon_id",
        "genus_taxon_name",
        "unranked clade_taxon_id",
        "unranked clade_taxon_name",
        "subclass_taxon_id",
        "subclass_taxon_name",
    ]
    if "pbdb_taxon_id" not in df:
        df["pbdb_taxon_id"] = pd.NA

    for index, row in df.iterrows():
        # skip if has pbdb_taxon_id
        if pd.notna(row["pbdb_taxon_id"]):
            continue

        # skip if no genus name
        if pd.isna(row[target_col]):
            continue

        # find records in genus_df that matches row genus name
        tmp = pbdb_df[
            (pbdb_df[target_col] == row[target_col])
            & (pbdb_df["taxon_group"] == row["taxon_group"])
            & (pbdb_df["pbdb_taxon_id"].notna())
        ]

        for index2, row2 in tmp.iterrows():
            for col in allowed_cols:
                if col in row2:
                    df.loc[index, col] = row2[col]


def add_genus_species(taxa_df, genus_only=False):
    taxa_df.loc[
        ~taxa_df["species name"]
        .str.contains("spp\.|sp\..*?", regex=True)
        .fillna(False),
        "genus species",
    ] = (
        taxa_df["genus name"] + " " + taxa_df["species name"]
    )
    taxa_df.loc[taxa_df["Any taxon above genus"].notna(), "genus species"] = pd.NA
    taxa_df.loc[
        taxa_df["Any taxon above genus modifier"].notna(), "genus species"
    ] = pd.NA

    if genus_only:
        taxa_df.loc[
            taxa_df["species name"]
            .str.contains("spp\.|sp\..*?", regex=True)
            .fillna(False),
            "genus species",
        ] = taxa_df["genus name"]
        taxa_df.loc[taxa_df["species name"].isna(), "genus species"] = taxa_df[
            "genus name"
        ]

    taxa_df["genus species"] = taxa_df["genus species"].str.strip()

def fix_taxa_for_row_id(df, row_id, correct_id, include_unranked_clade=False):
    """update pbdb data for a given row"""
    print(correct_id)
    columns = [
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
        "unranked clade_taxon_id",
        "unranked clade_taxon_name",
    ]

    url_parent = PBDB_TAXA_LIST_ID + str(correct_id)
    response = requests.get(url_parent)
    if response.status_code == 200:
        data = response.json()["records"]

        if len(data) > 0:
            last_record = data[len(data) - 1]

            for taxa_col in columns:
                df.at[row_id, taxa_col] = np.nan

            df.at[row_id, "pbdb_taxon_name"] = last_record["nam"]
            df.at[row_id, "pbdb_taxon_rank"] = rank_ids[last_record["rnk"]]
            df.at[row_id, "pbdb_taxon_id"] = correct_id

            process_taxa_hierarchy(df, data, row_id, include_unranked_clade)

    else:
        raise ValueError(f"{correct_id} ID not found")

    df.at[row_id, "corrected"] = True
