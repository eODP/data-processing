import requests

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
