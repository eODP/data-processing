import requests
import numpy as np 

PBDB_API = "https://paleobiodb.org/data1.2/"
PBDB_TAXA_NAME = f"{PBDB_API}taxa/single.json?vocab=pbdb&name="
PBDB_TAXA_ID = f"{PBDB_API}taxa/single.json?vocab=pbdb&id="


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
            if taxon_rank in ["family", "order", "class", "phylum", "kingdom"]:
                fill_taxon(df, index, data, taxon_rank)
            elif parent_id == "0":
                fill_taxon(df, index, data, taxon_rank)

            return get_parent_taxa(df, parent_id, taxon_rank, round, index, data)


def fix_pbdb_id(df, correction_text, correct_id):
    """look up pbdb data for taxon id. update dateframe with new pdbd"""
    print(correct_id)
    columns = [
        'pbdb_taxon_id',
        'pbdb_taxon_name', 'pbdb_taxon_rank',
        'family_taxon_id', 'family_taxon_name', 
        'order_taxon_id',  'order_taxon_name', 
        'class_taxon_id', 'class_taxon_name',
        'phylum_taxon_id', 'phylum_taxon_name', 
        'kingdom_taxon_id', 'kingdom_taxon_name',
        'unranked clade_taxon_id', 'unranked clade_taxon_name'
    ]



    col = "Corrections to pbdb_taxon_id"
    url_parent = PBDB_TAXA_ID + str(correct_id)
    response = requests.get(url_parent)
    if response.status_code == 200:
        data = response.json()["records"]
        if len(data) == 1:
            for taxa_col in columns:
                df.loc[df[col] == correction_text, taxa_col] = np.nan

            df.loc[df[col] == correction_text, "pbdb_taxon_name"] = data[0][
                "taxon_name"
            ]
            df.loc[df[col] == correction_text, "pbdb_taxon_rank"] = data[0][
                "taxon_rank"
            ]
            df.loc[df[col] == correction_text, "pbdb_taxon_id"] = correct_id

            for index, row in df[df[col] == correction_text].iterrows():
                round = 0
                get_parent_taxa(
                    df, data[0]["parent_no"], data[0]["taxon_rank"], round, index, None
                )

        else:
            raise ValueError("multipe ID found")
    else:
        raise ValueError("ID not found")

    df.loc[df[col] == correction_text, "corrected"] = True
