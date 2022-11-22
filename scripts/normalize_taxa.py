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

    # handle cases when no space between ? and first letter
    if bool(re.search(r"^\?[A-Za-z]", taxon_name)):
        taxon_name = '?' + ' ' + taxon_name[1:]

    # handle cases when name ends with (text text)
    if bool(re.search(r"\(.*?\)$", taxon_name)):
        # if there are multiple (, save descriptor with ()
        if len(list(re.finditer('\(', taxon_name))) > 1:
            match = re.search("\(.*?\)$", taxon_name)
            name_parts["non-taxa descriptor"] = match.group()
        # save descriptor without ()
        else:
            match = re.search("\((.*?)\)$", taxon_name)
            name_parts["non-taxa descriptor"] = match.groups()[0]
        taxon_name = taxon_name.split(match.group())[0].strip()

    parts = taxon_name.split(" ")

    current_rank_index = 0
    for index, part in enumerate(parts):
        if current_rank_index == 3:
            continue

        if part in modifiers:
            name_parts[ranks[current_rank_index] + " modifier"] = parts[index]
        # add all ending parts to subspecies
        elif current_rank_index == 2:
            name_parts[ranks[current_rank_index] + " name"] = ' '.join(parts[index:])
            current_rank_index += 1
        else:
            name_parts[ranks[current_rank_index] + " name"] = parts[index]
            current_rank_index += 1

    return name_parts


dex_sin_conversion_1 = {
    "Dextral:Sinistral _N. acostaensis_": [
        "Neogloboquadrina acostaensis (dextral)",
        "Neogloboquadrina acostaensis (sinistral)",
    ],
    "Dextral:Sinistral _P. finalis_": [
        "Pulleniatina finalis (dextral)",
        "Pulleniatina finalis (sinistral)",
    ],
    "Dextral:Sinistral _P. obliquiloculata_": [
        "Pulleniatina obliquiloculata (dextral)",
        "Pulleniatina obliquiloculata (sinistral)",
    ],
    "Dextral:Sinistral _P. praecursor_": [
        "Pulleniatina praecursor (dextral)",
        "Pulleniatina praecursor (sinistral)",
    ],
    "Dextral:Sinistral _P. praespectabilis_": [
        "Pulleniatina praespectabilis (dextral)",
        "Pulleniatina praespectabilis (sinistral)",
    ],
    "Dextral:Sinistral _P. primalis_": [
        "Pulleniatina primalis (dextral)",
        "Pulleniatina primalis (sinistral)",
    ],
    "Dextral:Sinistral _P. spectabilis_": [
        "Pulleniatina spectabilis (dextral)",
        "Pulleniatina spectabilis (sinistral)",
    ],
}


dex_sin_conversion_2 = {
    "Dextral:Sinistral _N. acostaensis_": [
        "Dextral N. acostaensis",
        "Sinistral N. acostaensis",
    ],
    "Dextral:Sinistral _P. finalis_": ["Dextral P. finalis", "Sinistral P. finalis"],
    "Dextral:Sinistral _P. obliquiloculata_": [
        "Dextral P. obliquiloculata",
        "Sinistral P. obliquiloculata",
    ],
    "Dextral:Sinistral _P. praecursor_": [
        "Dextral P. praecursor",
        "Sinistral P. praecursor",
    ],
    "Dextral:Sinistral _P. praespectabilis_": [
        "Dextral P. praespectabilis",
        "Sinistral P. praespectabilis",
    ],
    "Dextral:Sinistral _P. primalis_": ["Dextral P. primalis", "Sinistral P. primalis"],
    "Dextral:Sinistral _P. spectabilis_": [
        "Dextral P. spectabilis",
        "Sinistral P. spectabilis",
    ],
}


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


def create_noaa_1_taxa_crosswalk_df(metadata_df, base_dir):
    taxa = set()
    for index, row in metadata_df.iterrows():
        if row['type'] == 'taxa':
            df = pd.read_csv(base_dir / row['path'])
            df.dropna(axis=0, inplace=True, how='all')
            df.dropna(axis=1, inplace=True, how='all')

            df['verbatim'] = df['fossil'].str.strip()
            df['verbatim'] = df['verbatim'].fillna('')
            df['name'] = ''

            for index2, row2 in df.iterrows():
                if '(q)' in row2['verbatim']:
                    # set 'name' to 'verbatim name' without '(q)'
                    df.at[index2, 'name'] = re.sub('(.*?) ?\(q\)', r'? \1', row2['verbatim'])

            taxa.update(df['verbatim'] + '|' + df['name'] + '|' + row['taxon_group'])

    return create_noaa_taxa_list_df(taxa)


def create_noaa_2_taxa_crosswalk_df(metdata_df, base_dir):
    common_fields = {
        'Age From (oldest)',
        'Age To (youngest)',
        'Comment',
        'Cor',
        'Data',
        'Depth (mbsf)',
        'Fossil Group',
        'Fossil Group                                 ',
        'Group Abundance',
        'Group Preservation',
        'H',
        'Leg',
        'Sc',
        'Scientist',
        'Site',
        'T',
        'Top(cm)',
        'Zone From (bottom)',
        'Zone To  (top)'
    }

    taxa = set()
    for index, row in metdata_df.iterrows():
        df = pd.read_csv(base_dir / row['path'])
        df.dropna(axis=1, inplace=True, how='all')
        df.dropna(axis=0, inplace=True, how='all')

        file_taxa = set(df.columns) - common_fields
        for taxon in file_taxa:
            if isinstance(taxon, str) and len(taxon.strip()) > 0:
                taxa.add(taxon.strip() + '||' + row['taxon_group'])

    return create_noaa_taxa_list_df(taxa)


def create_noaa_taxa_list_df(taxa):
    all_ranks = [
        'genus modifier', 'genus name', 'species modifier', 'species name',
        'subspecies modifier', 'subspecies name', 'non-taxa descriptor'
    ]
    taxa_list = []
    for taxon in taxa:
        if not pd.isna(taxon):
            verbatim, name, taxon_group = taxon.split('|')

            if name == '':
                taxon_name_parts = taxon_name_parser(verbatim)
            else:
                taxon_name_parts = taxon_name_parser(name)

            data = {
                'taxon_group': taxon_group,
                'verbatim_name': verbatim,
                'name': name
            }

            for rank in all_ranks:
                if rank in taxon_name_parts:
                    data[rank] = taxon_name_parts[rank]
                else:
                    data[rank] = pd.NA

            taxa_list.append(data)

    df = pd.DataFrame(taxa_list).sort_values(['taxon_group', 'verbatim_name'])
    df = df.reindex(columns=['taxon_group', 'verbatim_name', 'name'] + all_ranks)
    df = df.drop_duplicates()
    return df
