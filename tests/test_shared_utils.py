import pandas as pd

from scripts.shared_utils import (
    extract_taxon_group_from_filename,
    get_taxa_and_taxon_groups,
)


class TestExtractTaxonGroupFromFilename:
    def test_returns_taxon_group_from_filename(self):
        file = "123_U1234A_taxon.csv"

        assert extract_taxon_group_from_filename(file) == "taxon"

    def test_works_with_hyphens_and_underscores(self):
        file = "123-U1234A_taxon.csv"

        assert extract_taxon_group_from_filename(file) == "taxon"

    def test_ignores_numbers_after_taxon(self):
        file1 = "123-U1234A_taxon-1.csv"
        file2 = "123-U1234A_taxon_1.csv"

        assert extract_taxon_group_from_filename(file1) == "taxon"
        assert extract_taxon_group_from_filename(file2) == "taxon"

    def test_returns_underscore_version_of_two_part_taxon_names(self):
        file1 = "123-U1234A_taxon_group.csv"
        file2 = "123-U1234A_taxon-group.csv"
        file3 = "123-U1234A_taxon group.csv"

        assert extract_taxon_group_from_filename(file1) == "taxon_group"
        assert extract_taxon_group_from_filename(file2) == "taxon_group"
        assert extract_taxon_group_from_filename(file3) == "taxon_group"

    def test_returns_lowercase_taxon_group_from_file(self):
        file = "123_U1234A_Taxon_Group.csv"

        assert extract_taxon_group_from_filename(file) == "taxon_group"

    def test_replace_one_or_more_spaces_with_one_underscore(self):
        file1 = "123 U1234A taxon group .csv"
        file2 = "123  U1234A  taxon  group  .csv"

        assert extract_taxon_group_from_filename(file1) == "taxon_group"
        assert extract_taxon_group_from_filename(file2) == "taxon_group"

    def test_replace_one_or_more_dashes_with_one_underscore(self):
        file1 = "123-U1234A-taxon-group.csv"
        file2 = "123--U1234A--taxon--group.csv"

        assert extract_taxon_group_from_filename(file1) == "taxon_group"
        assert extract_taxon_group_from_filename(file2) == "taxon_group"

    def test_v2_returns_taxon_group_from_filename(self):
        file = "123_taxon_U1234A.csv"

        assert extract_taxon_group_from_filename(file) == "taxon"

    def test_v2_works_with_hyphens_and_underscores(self):
        file = "123_taxon-U1234A.csv"

        assert extract_taxon_group_from_filename(file) == "taxon"

    def test_v2_ignores_numbers_after_taxon(self):
        file1 = "123_taxon-U1234A-1.csv"
        file2 = "123_taxon-U1234A_1.csv"

        assert extract_taxon_group_from_filename(file1) == "taxon"
        assert extract_taxon_group_from_filename(file2) == "taxon"

    def test_v2_returns_underscore_version_of_two_part_taxon_names(self):
        file1 = "123_taxon_group-U1234A.csv"
        file2 = "123_taxon-group-U1234A.csv"
        file3 = "123_taxon group-U1234A.csv"

        assert extract_taxon_group_from_filename(file1) == "taxon_group"
        assert extract_taxon_group_from_filename(file2) == "taxon_group"
        assert extract_taxon_group_from_filename(file3) == "taxon_group"

    def test_v2_returns_lowercase_taxon_group_from_file(self):
        file = "123_Taxon_Group_U1234A.csv"

        assert extract_taxon_group_from_filename(file) == "taxon_group"

    def test_v2_replace_one_or_more_spaces_with_one_underscore(self):
        file1 = "123 taxon group U1234A.csv"
        file2 = "123  taxon  group  U1234A  .csv"

        assert extract_taxon_group_from_filename(file1) == "taxon_group"
        assert extract_taxon_group_from_filename(file2) == "taxon_group"

    def test_v2_replace_one_or_more_dashes_with_one_underscore(self):
        file1 = "123-taxon-group-U1234A.csv"
        file2 = "123--taxon--group--U1234A.csv"

        assert extract_taxon_group_from_filename(file1) == "taxon_group"
        assert extract_taxon_group_from_filename(file2) == "taxon_group"


class TestGetTaxaAndTaxonGroups:
    def test_returns_a_dictionary_of_verbatim_names_and_taxon_groups(self):
        data = [
            {"verbatim_name": "taxon A", "taxon_group": "group 1", "name": "A a"},
            {"verbatim_name": "taxon B", "taxon_group": "group 2", "name": "B b"},
            {"verbatim_name": "taxon C", "taxon_group": "group 3", "name": "C c"},
        ]
        taxa_df = pd.DataFrame(data)

        expected = {
            "taxon A": ["group 1"],
            "taxon B": ["group 2"],
            "taxon C": ["group 3"],
        }
        assert get_taxa_and_taxon_groups(taxa_df) == expected

    def test_handles_verbatim_names_with_multiple_taxon_groups(self):
        data = [
            {"verbatim_name": "taxon A", "taxon_group": "group 1", "name": "A a"},
            {"verbatim_name": "taxon A", "taxon_group": "group 2", "name": "A a"},
            {"verbatim_name": "taxon B", "taxon_group": "group 2", "name": "C c"},
        ]
        taxa_df = pd.DataFrame(data)

        expected = {"taxon A": ["group 1", "group 2"], "taxon B": ["group 2"]}
        assert get_taxa_and_taxon_groups(taxa_df) == expected

    def test_ignores_record_with_duplicate_verbatim_name_and_taxon_group(self):
        data = [
            {"verbatim_name": "taxon A", "taxon_group": "group 1", "name": "A a"},
            {"verbatim_name": "taxon A", "taxon_group": "group 1", "name": "B b"},
            {"verbatim_name": "taxon A", "taxon_group": "group 2", "name": "A a"},
        ]
        taxa_df = pd.DataFrame(data)

        expected = {"taxon A": ["group 1", "group 2"]}
        assert get_taxa_and_taxon_groups(taxa_df) == expected

    def test_strips_extra_whitespace_from_verbatim_name(self):
        data = [
            {"verbatim_name": "taxon A", "taxon_group": "group 1", "name": "A a"},
            {"verbatim_name": " taxon A", "taxon_group": "group 1", "name": "B b"},
            {"verbatim_name": " taxon A ", "taxon_group": "group 1", "name": "C c"},
            {"verbatim_name": " taxon A", "taxon_group": "group 1", "name": "D d"},
        ]
        taxa_df = pd.DataFrame(data)

        expected = {"taxon A": ["group 1"]}
        assert get_taxa_and_taxon_groups(taxa_df) == expected
