import re


def extract_taxon_group_from_filename(filename):
    filename = re.sub("-+", "_", filename)
    filename = re.sub(" +", "_", filename)

    filename_parts = re.search(
        # matches 123-U1234A-taxon-group or 123-U1234A-taxongroup
        r"^[0-9]{3}_+U[0-9]{4}[a-zA-Z]{0,3}_+([a-zA-Z]+(_[a-zA-Z]+)?)(_\d)?_?\.csv",
        filename,
    )

    if filename_parts is None:
        filename_parts = re.search(
            # matches 123-taxon-group-U1234A- or 123-taxongroup-U1234A
            r"^[0-9]{3}_+([a-zA-Z]+(_[a-zA-Z]+)?)_+U[0-9]{4}[a-zA-Z](_\d)?_?\.csv",
            filename,
        )

    if filename_parts is None:
        filename_parts = re.search(
            # matches 123-taxon-group-U1234A_123_T01_taxon_group
            r"^[0-9]{3}_+U[0-9]{4}[a-zA-Z]{0,3}_[0-9]{3}_T[0-9]{2}_+([a-zA-Z]+(_[a-zA-Z]+)?)(_\d)?_?\.csv",  # noqa: E501
            filename,
        )

    if filename_parts is not None:
        return filename_parts.groups()[0].lower()
    else:
        raise ValueError("Cannot extract taxon group.")


def get_taxa_and_taxon_groups(df):
    """Returns dictionary of verbatim names and their taxon groups"""
    all_verbatim_names = {}
    for index, row in df.iterrows():
        name = row["verbatim_name"].strip()
        if name not in all_verbatim_names:
            all_verbatim_names[name] = []

        if row["taxon_group"] not in all_verbatim_names[name]:
            all_verbatim_names[name].append(row["taxon_group"])

    return all_verbatim_names
