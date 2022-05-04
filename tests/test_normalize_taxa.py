import copy
import pandas as pd
import numpy as np
from pandas._testing import assert_frame_equal

from scripts.normalize_taxa import (
    add_normalized_name_column,
    taxon_name_parser,
    create_taxa_crosswalk_df,
)


class TestAddNormalizedNameColumn:
    def test_adds_normalized_name_column_to_dataframe(self):
        data = {
            "Any taxon above genus": ["a"],
            "genus modifier": ["gm"],
            "genus name": ["gn"],
            "subgenera modifier": ["sgm"],
            "subgenera name": ["sgn"],
            "species modifier": ["sm"],
            "species name": ["sn"],
            "subspecies modifier": ["ssm"],
            "subspecies name": ["ssn"],
            "non-taxa descriptor": ["d"],
        }
        df = pd.DataFrame(data)
        expected_data = copy.deepcopy(data)
        expected_data["normalized_name"] = ["a gm gn sgm sgn sm sn ssm ssn (d)"]
        expected = pd.DataFrame(expected_data)

        add_normalized_name_column(df)

        assert_frame_equal(df, expected)

    def test_do_not_include_descriptor(self):
        data = {
            "Any taxon above genus": ["a"],
            "genus modifier": ["gm"],
            "genus name": ["gn"],
            "subgenera modifier": ["sgm"],
            "subgenera name": ["sgn"],
            "species modifier": ["sm"],
            "species name": ["sn"],
            "subspecies modifier": ["ssm"],
            "subspecies name": ["ssn"],
            "non-taxa descriptor": ["d"],
        }
        df = pd.DataFrame(data)
        expected_data = copy.deepcopy(data)
        expected_data["normalized_name"] = ["a gm gn sgm sgn sm sn ssm ssn"]
        expected = pd.DataFrame(expected_data)

        add_normalized_name_column(df, include_descriptor=False)

        assert_frame_equal(df, expected)

    def test_do_not_include_modifier(self):
        data = {
            "Any taxon above genus": ["a"],
            "genus modifier": ["gm"],
            "genus name": ["gn"],
            "subgenera modifier": ["sgm"],
            "subgenera name": ["sgn"],
            "species modifier": ["sm"],
            "species name": ["sn"],
            "subspecies modifier": ["ssm"],
            "subspecies name": ["ssn"],
            "non-taxa descriptor": ["d"],
        }
        df = pd.DataFrame(data)
        expected_data = copy.deepcopy(data)
        expected_data["normalized_name"] = ["a gn sgn sn ssn (d)"]
        expected = pd.DataFrame(expected_data)

        add_normalized_name_column(df, include_modifier=False)

        assert_frame_equal(df, expected)

    def test_do_not_add_parenthesis_for_descriptors_with_parenthesis(self):
        data = {
            "Any taxon above genus": ["a"],
            "genus modifier": ["gm"],
            "genus name": ["gn"],
            "subgenera modifier": ["sgm"],
            "subgenera name": ["sgn"],
            "species modifier": ["sm"],
            "species name": ["sn"],
            "subspecies modifier": ["ssm"],
            "subspecies name": ["ssn"],
            "non-taxa descriptor": ["(d)"],
        }
        df = pd.DataFrame(data)
        expected_data = copy.deepcopy(data)
        expected_data["normalized_name"] = ["a gm gn sgm sgn sm sn ssm ssn (d)"]
        expected = pd.DataFrame(expected_data)

        add_normalized_name_column(df)

        assert_frame_equal(df, expected)

    def test_handles_empty_strings(self):
        data = {
            "Any taxon above genus": [""],
            "genus modifier": ["gm"],
            "genus name": ["gn"],
            "subgenera modifier": [""],
            "subgenera name": ["sgn"],
            "species modifier": [""],
            "species name": ["sn"],
            "subspecies modifier": [""],
            "subspecies name": [""],
            "non-taxa descriptor": ["d"],
        }
        df = pd.DataFrame(data)
        expected_data = copy.deepcopy(data)
        expected_data["normalized_name"] = ["gm gn sgn sn (d)"]
        expected = pd.DataFrame(expected_data)

        add_normalized_name_column(df)

        assert_frame_equal(df, expected)

    def test_handles_NA(self):
        data = {
            "Any taxon above genus": [np.nan],
            "genus modifier": ["gm"],
            "genus name": ["gn"],
            "subgenera modifier": [np.nan],
            "subgenera name": ["sgn"],
            "species modifier": [np.nan],
            "species name": ["sn"],
            "subspecies modifier": [np.nan],
            "subspecies name": [np.nan],
            "non-taxa descriptor": ["d"],
        }
        df = pd.DataFrame(data)
        expected_data = copy.deepcopy(data)
        expected_data["normalized_name"] = ["gm gn sgn sn (d)"]
        expected = pd.DataFrame(expected_data)

        add_normalized_name_column(df)

        assert_frame_equal(df, expected)

    def test_handles_all_NA(self):
        data = {
            "Any taxon above genus": [np.nan],
            "genus modifier": [np.nan],
            "genus name": [np.nan],
            "subgenera modifier": [np.nan],
            "subgenera name": [np.nan],
            "species modifier": [np.nan],
            "species name": [np.nan],
            "subspecies modifier": [np.nan],
            "subspecies name": [np.nan],
            "non-taxa descriptor": [np.nan],
        }
        df = pd.DataFrame(data)
        expected_data = copy.deepcopy(data)
        expected_data["normalized_name"] = [""]
        expected = pd.DataFrame(expected_data)

        add_normalized_name_column(df)

        assert_frame_equal(df, expected)


class TestTaxonNameParser:
    def test_parse_genus(self):
        string = "genus"
        expected = {"genus name": "genus"}
        assert taxon_name_parser(string) == expected

    def test_parse_genus_species(self):
        string = "genus species"
        expected = {"genus name": "genus", "species name": "species"}
        assert taxon_name_parser(string) == expected

    def test_parse_genus_species_subspecies(self):
        string = "genus species subspecies"
        expected = {
            "genus name": "genus",
            "species name": "species",
            "subspecies name": "subspecies",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_genus_modifier(self):
        string = "? genus"
        expected = {
            "genus modifier": "?",
            "genus name": "genus",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_genus_modifier_with_species(self):
        string = "? genus species"
        expected = {
            "genus modifier": "?",
            "genus name": "genus",
            "species name": "species",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_species_modifier(self):
        string = "genus cf. species"
        expected = {
            "genus name": "genus",
            "species modifier": "cf.",
            "species name": "species",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_genus_and_species_modifier(self):
        string = "? genus cf. species"
        expected = {
            "genus modifier": "?",
            "genus name": "genus",
            "species modifier": "cf.",
            "species name": "species",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_genus_species_subspecies_modifier(self):
        string = "? genus cf. species f. subspecies"
        expected = {
            "genus modifier": "?",
            "genus name": "genus",
            "species modifier": "cf.",
            "species name": "species",
            "subspecies modifier": "f.",
            "subspecies name": "subspecies",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_genus_and_descriptor(self):
        string = "genus (descriptor)"
        expected = {
            "genus name": "genus",
            "non-taxa descriptor": "(descriptor)",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_genus_and_species_and_descriptor(self):
        string = "genus species (descriptor)"
        expected = {
            "genus name": "genus",
            "species name": "species",
            "non-taxa descriptor": "(descriptor)",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_genus_species_subspecies_and_descriptor(self):
        string = "genus species subspecies (descriptor)"
        expected = {
            "genus name": "genus",
            "species name": "species",
            "subspecies name": "subspecies",
            "non-taxa descriptor": "(descriptor)",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_genus_modifier_and_descriptor(self):
        string = "? genus (descriptor)"
        expected = {
            "genus modifier": "?",
            "genus name": "genus",
            "non-taxa descriptor": "(descriptor)",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_genus_and_species_modifier_and_descriptor(self):
        string = "? genus cf. species (descriptor)"
        expected = {
            "genus modifier": "?",
            "genus name": "genus",
            "species modifier": "cf.",
            "species name": "species",
            "non-taxa descriptor": "(descriptor)",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_genus_species_subspecies_modifier_and_descriptor(self):
        string = "? genus cf. species f. subspecies (descriptor)"
        expected = {
            "genus modifier": "?",
            "genus name": "genus",
            "species modifier": "cf.",
            "species name": "species",
            "subspecies modifier": "f.",
            "subspecies name": "subspecies",
            "non-taxa descriptor": "(descriptor)",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_long_text(self):
        string = "text1 text2 text3 text4 text5"
        expected = {
            "genus name": "text1",
            "species name": "text2",
            "subspecies name": "text3",
        }
        assert taxon_name_parser(string) == expected

    def test_parse_parenthesis(self):
        string = "text1 (text2) text3"
        expected = {
            "genus name": "text1",
            "species name": "(text2)",
            "subspecies name": "text3",
        }
        assert taxon_name_parser(string) == expected


class Test_create_taxa_crosswalk_df:
    def format_df(self, attrs):
        common_columns = {
            "Any taxon above genus": np.nan,
            "genus modifier": np.nan,
            "genus name": np.nan,
            "subgenera modifier": np.nan,
            "subgenera name": np.nan,
            "species modifier": np.nan,
            "species name": np.nan,
            "subspecies modifier": np.nan,
            "subspecies name": np.nan,
            "non-taxa descriptor": np.nan,
            "normalized_name": np.nan,
            "taxon_group": np.nan,
            "verbatim_name": np.nan,
            "name comment field": np.nan,
            "Comment": np.nan,
            "Notes (change to Internal only notes?)": np.nan,
            "comments": np.nan,
        }
        for k, v in attrs.items():
            common_columns[k] = v

        return common_columns

    def test_add_columns_for_crosswalk_df(self):
        data = [
            {
                "verbatim_name": "a a1",
                "genus name": "a",
                "species name": "aa",
                "taxon_group": "group",
            },
            {
                "verbatim_name": "b b1",
                "genus name": "b",
                "species name": "bb",
                "taxon_group": "group",
            },
        ]
        df = pd.DataFrame(data)
        data = [
            self.format_df(
                {
                    "genus name": "a",
                    "species name": "aa",
                    "normalized_name": "a aa",
                    "taxon_group": "group",
                    "verbatim_name": "a a1",
                }
            ),
            self.format_df(
                {
                    "genus name": "b",
                    "species name": "bb",
                    "normalized_name": "b bb",
                    "taxon_group": "group",
                    "verbatim_name": "b b1",
                }
            ),
        ]
        expected = pd.DataFrame(data)

        new_df = create_taxa_crosswalk_df(df)

        assert_frame_equal(new_df, expected)

    def test_if_verbatim_name_has_Dextral_Sinistral(self):
        data = [
            {
                "verbatim_name": "Dextral:Sinistral a a1",
                "genus name": "a",
                "species name": "aa",
                "taxon_group": "group",
            },
            {
                "verbatim_name": "Dextral:Sinistral b b1",
                "genus name": "b",
                "species name": "bb",
                "taxon_group": "group",
            },
        ]
        df = pd.DataFrame(data)
        data = [
            self.format_df(
                {
                    "genus name": "a",
                    "species name": "aa",
                    "normalized_name": "a aa",
                    "taxon_group": "group",
                    "verbatim_name": "Dextral:Sinistral a a1",
                }
            ),
            self.format_df(
                {
                    "genus name": "b",
                    "species name": "bb",
                    "normalized_name": "b bb",
                    "taxon_group": "group",
                    "verbatim_name": "Dextral:Sinistral b b1",
                }
            ),
        ]
        expected = pd.DataFrame(data)

        new_df = create_taxa_crosswalk_df(df)

        assert_frame_equal(new_df, expected)
