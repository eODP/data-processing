from io import StringIO

import pandas as pd
import numpy as np
from pandas._testing import assert_frame_equal
import pytest

from scripts.normalize_data import (
    tablerize,
    convert_column_names,
    normalize_sample_col,
    create_sample_name,
    normalize_expedition_section_cols,
    create_sample_cols,
    restore_integer_columns,
    update_metadata,
    replace_unnamed_xx_columns,
    normalize_columns,
    extract_taxon_group_from_filename,
    check_duplicate_columns,
    restore_duplicate_column_names,
    clean_taxon_name,
    taxa_needs_review,
    remove_whitespace,
)


class TestTablerize:
    def test_returns_lowercase_letters(self):
        assert tablerize("ABcD") == "abcd"

    def test_returns_mixture_of_numbers_letters_underscores(self):
        assert tablerize("ABc_123") == "abc_123"

    def test_replaces_spaces_with_one_underscore(self):
        assert tablerize("ABc abC    Abc") == "abc_abc_abc"

    def test_ignores_other_characters(self):
        assert tablerize("?.ABc' 123-#'") == "abc_123"


class TestConvertColumnNames:
    def test_returns_a_dictionary_of_original_and_formatted_names(self):
        names = ["ABC 123", "AbC", "A Bc"]
        assert convert_column_names(names) == {
            "ABC 123": "abc_123",
            "AbC": "abc",
            "A Bc": "a_bc",
        }

    def test_handles_single_item_list(self):
        names = ["ABC 123"]
        assert convert_column_names(names) == {"ABC 123": "abc_123"}

    def test_returns_empty_dictionary_when_list_is_empty(self):
        names = []
        assert convert_column_names(names) == {}


class TestNormalizeSampleCol:
    def test_dataframe_does_not_change_if_Sample_column_exist(self):
        df = pd.DataFrame({"Sample": ["abc"]})
        expected = pd.DataFrame({"Sample": ["abc"]})

        normalize_sample_col(df)

        assert_frame_equal(df, expected)

    def test_changes_Label_ID_to_Sample(self):
        df = pd.DataFrame({"Label ID": ["abc"]})
        expected = pd.DataFrame({"Sample": ["abc"]})

        normalize_sample_col(df)

        assert_frame_equal(df, expected)

    def test_adds_Sample_if_correct_columns_exist(self):
        data = {
            "Exp": [1, 10],
            "Site": ["s", "S"],
            "Hole": ["h", "H"],
            "Core": [2, 20],
            "Type": ["t", "T"],
            "Section": [3, 30],
            "A/W": ["a", "A"],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1-sh-2t-3-a", "10-SH-20T-30-A"]
        expected = pd.DataFrame(data)

        normalize_sample_col(df)

        assert_frame_equal(df, expected)

    def test_otherwise_raise_error(self):
        df = pd.DataFrame({"foo": [1]})

        message = "File does not have the expected columns."
        with pytest.raises(ValueError, match=message):
            normalize_sample_col(df)


class TestCreateSampleName:
    def test_returns_Sample_if_all_columns_are_present(self):
        data = {
            "Exp": [1],
            "Site": ["s"],
            "Hole": ["h"],
            "Core": [2],
            "Type": ["t"],
            "Section": [3],
            "A/W": ["a"],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1-sh-2t-3-a"]
        expected = pd.DataFrame(data)

        create_sample_name(df)

        assert_frame_equal(df, expected)

    def test_adds_dash_extra_sample_data_if_PAL_aw(self):
        data = {
            "Exp": [1],
            "Site": ["s"],
            "Hole": ["h"],
            "Core": [2],
            "Type": ["t"],
            "Section": [3],
            "A/W": ["PAL"],
            "Extra Sample ID Data": ["e"],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1-sh-2t-3-PAL-e"]
        expected = pd.DataFrame(data)

        create_sample_name(df)

        assert_frame_equal(df, expected)

    def test_adds_space_extra_sample_data_if_any_aw(self):
        data = {
            "Exp": [1],
            "Site": ["s"],
            "Hole": ["h"],
            "Core": [2],
            "Type": ["t"],
            "Section": [3],
            "A/W": ["a"],
            "Extra Sample ID Data": ["e"],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1-sh-2t-3-a e"]
        expected = pd.DataFrame(data)

        create_sample_name(df)

        assert_frame_equal(df, expected)

    def test_creates_Sample_string_if_column_are_null(self):
        data = {
            "Exp": [1],
            "Site": [None],
            "Hole": ["h"],
            "Core": [2],
            "Type": ["t"],
            "Section": [3],
            "A/W": ["a"],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1-h-2t-3-a"]
        expected = pd.DataFrame(data)

        create_sample_name(df)

        assert_frame_equal(df, expected)

    def test_creates_Sample_string_if_column_are_null_2(self):
        data = {
            "Exp": [1],
            "Site": [None],
            "Hole": [None],
            "Core": [2],
            "Type": ["t"],
            "Section": [3],
            "A/W": ["a"],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1-2t-3-a"]
        expected = pd.DataFrame(data)

        create_sample_name(df)

        assert_frame_equal(df, expected)

    def test_creates_Sample_string_if_column_are_null_3(self):
        data = {
            "Exp": [1],
            "Site": [None],
            "Hole": [None],
            "Core": [None],
            "Type": ["t"],
            "Section": [3],
            "A/W": ["a"],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1-t-3-a"]
        expected = pd.DataFrame(data)

        create_sample_name(df)

        assert_frame_equal(df, expected)

    def test_creates_Sample_string_if_column_are_null_4(self):
        data = {
            "Exp": [1],
            "Site": [None],
            "Hole": [None],
            "Core": [None],
            "Type": [None],
            "Section": [3],
            "A/W": ["a"],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1-3-a"]
        expected = pd.DataFrame(data)

        create_sample_name(df)

        assert_frame_equal(df, expected)

    def test_creates_Sample_string_if_column_are_null_5(self):
        data = {
            "Exp": [1],
            "Site": [None],
            "Hole": [None],
            "Core": [None],
            "Type": [None],
            "Section": [None],
            "A/W": ["a"],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1-a"]
        expected = pd.DataFrame(data)

        create_sample_name(df)

        assert_frame_equal(df, expected)

    def test_creates_Sample_string_if_column_are_null_6(self):
        data = {
            "Exp": [1],
            "Site": [None],
            "Hole": [None],
            "Core": [None],
            "Type": [None],
            "Section": [None],
            "A/W": [None],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1"]
        expected = pd.DataFrame(data)

        create_sample_name(df)

        assert_frame_equal(df, expected)

    def test_removes_dash_from_end_of_string(self):
        data = {
            "Exp": [1],
            "Site": [None],
            "Hole": [None],
            "Core": [None],
            "Type": [None],
            "Section": [3],
            "A/W": [None],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1-3"]
        expected = pd.DataFrame(data)

        create_sample_name(df)

        assert_frame_equal(df, expected)

    def test_removes_dash_from_end_of_string_2(self):
        data = {
            "Exp": [1],
            "Site": [None],
            "Hole": [None],
            "Core": [None],
            "Type": ["t"],
            "Section": [None],
            "A/W": [None],
        }
        df = pd.DataFrame(data)
        data["Sample"] = ["1-t"]
        expected = pd.DataFrame(data)

        create_sample_name(df)

        assert_frame_equal(df, expected)

    def test_raise_error_if_some_columns_are_missing(self):
        data = {
            "Exp": [1],
            "Site": ["s"],
            "Hole": [None],
            "Core": [None],
            "Type": [None],
            "Section": [None],
        }
        df = pd.DataFrame(data)

        message = "File does not have the expected columns."
        with pytest.raises(ValueError, match=message):
            create_sample_name(df)

    def test_otherwise_raise_error(self):
        df = pd.DataFrame({"foo": [1]})

        message = "File does not have the expected columns."
        with pytest.raises(ValueError, match=message):
            create_sample_name(df)


class TestNormalizeExpeditionSectionCols:
    def test_dataframe_does_not_change_if_expection_section_columns_exist(self):
        data = {
            "Col": [0, 1],
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": ["t", "T"],
            "Section": ["3", "3"],
            "A/W": ["a", "A"],
        }
        df = pd.DataFrame(data)
        expected = pd.DataFrame(data)

        df = normalize_expedition_section_cols(df)

        assert_frame_equal(df, expected)

    def test_dataframe_does_not_change_if_expection_section_Sample_exist(self):
        data = {
            "Col": [0, 1],
            "Sample": ["1-U1h-2t-3-a", "10-U2H-20T-3-A"],
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": ["t", "T"],
            "Section": ["3", "3"],
            "A/W": ["a", "A"],
        }
        df = pd.DataFrame(data)
        expected = pd.DataFrame(data)

        df = normalize_expedition_section_cols(df)

        assert_frame_equal(df, expected)

    def test_dataframe_does_not_change_if_expection_section_Label_exist(self):
        data = {
            "Col": [0, 1],
            "Label ID": ["1-U1h-2t-3-a", "10-U2H-20T-3-A"],
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": ["t", "T"],
            "Section": ["3", "3"],
            "A/W": ["a", "A"],
        }
        df = pd.DataFrame(data)
        expected = pd.DataFrame(data)

        df = normalize_expedition_section_cols(df)

        assert_frame_equal(df, expected)

    def test_adds_missing_expection_section_using_Label(self):
        data = {
            "Col": [0, 1],
            "Label ID": ["1-U1h-2t-3-a", "10-U2H-20T-3-A"],
        }
        df = pd.DataFrame(data)

        data = {
            "Col": [0, 1],
            "Label ID": ["1-U1h-2t-3-a", "10-U2H-20T-3-A"],
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": ["t", "T"],
            "Section": ["3", "3"],
            "A/W": ["a", "A"],
        }
        expected = pd.DataFrame(data)

        df = normalize_expedition_section_cols(df)

        assert_frame_equal(df, expected)

    def test_adds_missing_expection_section_using_Sample(self):
        data = {
            "Col": [0, 1],
            "Sample": ["1-U1h-2t-3-a", "10-U2H-20T-3-A"],
        }
        df = pd.DataFrame(data)

        data = {
            "Col": [0, 1],
            "Sample": ["1-U1h-2t-3-a", "10-U2H-20T-3-A"],
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": ["t", "T"],
            "Section": ["3", "3"],
            "A/W": ["a", "A"],
        }
        expected = pd.DataFrame(data)

        df = normalize_expedition_section_cols(df)

        assert_frame_equal(df, expected)

    def test_handles_missing_aw_col(self):
        data = {
            "Col": [0, 1],
            "Sample": ["1-U1h-2t-3", "10-U2H-20T-3"],
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": ["t", "T"],
            "Section": ["3", "3"],
        }
        df = pd.DataFrame(data)
        expected = pd.DataFrame(data)

        df = normalize_expedition_section_cols(df)

        assert_frame_equal(df, expected)

    def test_handles_no_data(self):
        data = {
            "Col": [0],
            "Sample": ["No data this hole"],
        }
        df = pd.DataFrame(data)

        data = {
            "Col": [0],
            "Sample": ["No data this hole"],
            "Exp": [None],
            "Site": [None],
            "Hole": [None],
            "Core": [None],
            "Type": [None],
            "Section": [None],
            "A/W": [None],
        }
        expected = pd.DataFrame(data)

        df = normalize_expedition_section_cols(df)

        assert_frame_equal(df, expected)

    def test_otherwise_raise_error(self):
        df = pd.DataFrame({"foo": [1]})

        message = "File does not have the expected columns."
        with pytest.raises(ValueError, match=message):
            normalize_expedition_section_cols(df)


class TestCreateSampleCols:
    def test_extracts_parts_from_exp_site_hole_core_type_section_aw_string(self):
        data = {
            "Label ID": ["1-U1h-2t-3-a", "10-U20H-20T-Sec-4AA"],
        }
        df = pd.DataFrame(data)

        data = {
            "Exp": ["1", "10"],
            "Site": ["U1", "U20"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": ["t", "T"],
            "Section": ["3", "Sec"],
            "A/W": ["a", "4AA"],
        }
        expected = pd.DataFrame(data)

        df = create_sample_cols(df["Label ID"])
        assert_frame_equal(df, expected)

    def test_raises_error_if_exp_is_letters(self):
        data = {
            "Sample": ["e-U1h-2t-3-a"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            create_sample_cols(df["Sample"])

    def test_raises_error_if_site_does_not_begin_with_U(self):
        data = {
            "Sample": ["1-1h-2t-3-a"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            create_sample_cols(df["Sample"])

    def test_raises_error_if_site_ends_with_letters(self):
        data = {
            "Sample": ["1-Ush-2t-3-a"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            create_sample_cols(df["Sample"])

    def test_raises_error_if_hole_is_a_number(self):
        data = {
            "Sample": ["1-U11-2t-3-a"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            create_sample_cols(df["Sample"])

    def test_raises_error_if_hole_has_multiple_letters(self):
        data = {
            "Sample": ["1-U1hh-2t-3-a"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            create_sample_cols(df["Sample"])

    def test_raises_error_if_cores_has_letters(self):
        data = {
            "Sample": ["1-U1h-ct-3-a"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            create_sample_cols(df["Sample"])

    def test_handles_missing_type(self):
        data = {
            "Sample": ["1-U1h-11-3-a"],
        }
        df = pd.DataFrame(data)

        data = {
            "Exp": ["1"],
            "Site": ["U1"],
            "Hole": ["h"],
            "Core": ["11"],
            "Type": [None],
            "Section": ["3"],
            "A/W": ["a"],
        }
        expected = pd.DataFrame(data)

        df = create_sample_cols(df["Sample"])
        assert_frame_equal(df, expected)

    def test_raises_error_if_type_has_multiple_letters(self):
        data = {
            "Sample": ["1-U1h-1tt-3-a"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            create_sample_cols(df["Sample"])

    def test_accepts_exp_site_hole_core_type_section_string(self):
        data = {
            "Label ID": ["1-U1h-2t-3", "10-U2H-20T-3"],
        }
        df = pd.DataFrame(data)

        data = {
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": ["t", "T"],
            "Section": ["3", "3"],
            "A/W": [None, None],
        }
        expected = pd.DataFrame(data)

        df = create_sample_cols(df["Label ID"])
        assert_frame_equal(df, expected)

    def test_accepts_exp_site_hole_core_type_string(self):
        data = {
            "Sample": ["1-U1h-2t", "10-U2H-20T"],
        }
        df = pd.DataFrame(data)

        data = {
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": ["t", "T"],
            "Section": [None, None],
            "A/W": [None, None],
        }
        expected = pd.DataFrame(data)

        df = create_sample_cols(df["Sample"])
        assert_frame_equal(df, expected)

    def test_accepts_exp_site_hole_core_string(self):
        data = {
            "Sample": ["1-U1h-2", "10-U2H-20"],
        }
        df = pd.DataFrame(data)

        data = {
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": [None, None],
            "Section": [None, None],
            "A/W": [None, None],
        }
        expected = pd.DataFrame(data)

        df = create_sample_cols(df["Sample"])
        assert_frame_equal(df, expected)

    def test_accepts_exp_site_hole_string(self):
        data = {
            "Sample": ["1-U1h", "10-U2H"],
        }
        df = pd.DataFrame(data)

        data = {
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": [None, None],
            "Type": [None, None],
            "Section": [None, None],
            "A/W": [None, None],
        }
        expected = pd.DataFrame(data)

        df = create_sample_cols(df["Sample"])
        assert_frame_equal(df, expected)

    def test_rejects_exp_site_string(self):
        data = {
            "Sample": ["1-U1", "10-U2"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            df = create_sample_cols(df["Sample"])

    def test_rejects_exp_string(self):
        data = {
            "Sample": ["1", "10"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            df = create_sample_cols(df["Sample"])

    def test_ignores_hash_symbol_element_in_sample_name(self):
        data = {
            "Sample": ["349-U1431E-7R-1-#1-A", "349-U1431E-7R-1-#1"],
        }
        df = pd.DataFrame(data)

        data = {
            "Exp": ["349", "349"],
            "Site": ["U1431", "U1431"],
            "Hole": ["E", "E"],
            "Core": ["7", "7"],
            "Type": ["R", "R"],
            "Section": ["1", "1"],
            "A/W": ["A", None],
        }
        expected = pd.DataFrame(data)

        df = create_sample_cols(df["Sample"])
        assert_frame_equal(df, expected)

    def test_returns_None_when_input_is_None(self):
        data = {
            "Sample": [None],
        }
        df = pd.DataFrame(data)

        data = {
            "Exp": [None],
            "Site": [None],
            "Hole": [None],
            "Core": [None],
            "Type": [None],
            "Section": [None],
            "A/W": [None],
        }
        expected = pd.DataFrame(data)

        df = create_sample_cols(df["Sample"])
        assert_frame_equal(df, expected)

    def test_returns_none_when_input_is_No_data_this_hole(self):
        data = {
            "Sample": ["No data this hole"],
        }
        df = pd.DataFrame(data)

        data = {
            "Exp": [None],
            "Site": [None],
            "Hole": [None],
            "Core": [None],
            "Type": [None],
            "Section": [None],
            "A/W": [None],
        }
        expected = pd.DataFrame(data)

        df = create_sample_cols(df["Sample"])
        assert_frame_equal(df, expected)

    def test_otherwise_raise_error(self):
        data = {
            "Sample": ["AAA", "BBB"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            create_sample_cols(df["Sample"])


class TestRestoreIntColumns:
    def test_integer_columns_are_changed_to_integers(self):
        df = pd.read_csv("./tests/data/missing_values.csv")
        assert isinstance(df["int"][0], np.float64)
        assert str(df["int"][0]) == "1.0"
        assert str(df["int"][1]) == "2.0"
        assert str(df["int"][2]) == "3.0"

        df = restore_integer_columns(df)

        assert isinstance(df["int"][0], np.int64)
        assert str(df["int"][0]) == "1"
        assert str(df["int"][1]) == "2"
        assert str(df["int"][2]) == "3"

    def test_integer_null_columns_are_changed_to_integers(self):
        df = pd.read_csv("./tests/data/missing_values.csv")
        assert isinstance(df["int null"][0], np.float64)
        assert str(df["int null"][0]) == "1.0"

        df = restore_integer_columns(df)

        assert isinstance(df["int null"][0], np.int64)
        assert str(df["int null"][0]) == "1"

    def test_integer_float_columns_remain_floats(self):
        df = pd.read_csv("./tests/data/missing_values.csv")
        assert isinstance(df["int float"][0], np.float64)
        assert str(df["int float"][0]) == "1.0"
        assert str(df["int float"][1]) == "2.0"
        assert str(df["int float"][2]) == "3.1"

        df = restore_integer_columns(df)

        assert isinstance(df["int float"][0], np.float64)
        assert str(df["int float"][0]) == "1.0"
        assert str(df["int float"][1]) == "2.0"
        assert str(df["int float"][2]) == "3.1"


class TestUpdateMetadata:
    def test_adds_new_column_to_dataframe_if_column_does_not_exists(self):
        metadata = pd.DataFrame({"a": [1, 2]})
        dict = {"b": [3, 4]}
        new_metadata = update_metadata(metadata, dict)

        expected = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

        assert_frame_equal(new_metadata, expected)

    def test_does_not_update_dataframe_if_columns_exists(self):
        metadata = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        dict = {"b": [5, 6]}
        new_metadata = update_metadata(metadata, dict)

        expected = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

        assert_frame_equal(new_metadata, expected)


class TestReplaceUnnamedXXColumns:
    def test_replace_unnamed_xx_with_empty_string(self):
        df = pd.DataFrame(
            {
                "a": [1],
                "Unnamed: 1": [1],
                "Unnamed: 10": [1],
                "Unnamed: 1000": [1],
                "b": [1],
            }
        )

        new_df = replace_unnamed_xx_columns(df)

        assert len(df.columns) == len(new_df.columns)
        assert new_df.columns[0] == "a"
        assert new_df.columns[1] == ""
        assert new_df.columns[3] == ""
        assert new_df.columns[4] == "b"

    def test_leaves_other_columns_unchanged(self):
        df = pd.DataFrame({"a": [1], "Bb": [1], "CC CC": [1]})

        new_df = replace_unnamed_xx_columns(df)

        assert len(df.columns) == len(new_df.columns)
        assert new_df.columns[0] == "a"
        assert new_df.columns[1] == "Bb"
        assert new_df.columns[2] == "CC CC"


class TestNormalizeColumns:
    def test_replaces_column_if_column_matches(self):
        all_cols = ["a", "B"]
        old_cols = {"A", "a", "aa"}
        new_col = "AAA"

        res = normalize_columns(old_cols, new_col, all_cols)

        assert len(all_cols) == len(res)
        assert res[0] == "AAA"
        assert res[1] == "B"

    def test_does_not_replace_column_if_no_matches(self):
        all_cols = ["a", "B"]
        old_cols = {"BB", "bb", "b"}
        new_col = "BBB"

        res = normalize_columns(old_cols, new_col, all_cols)

        assert len(all_cols) == len(res)
        assert res[0] == "a"
        assert res[1] == "B"


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


class TestCompareDuplicateColumns:
    def test_returns_True_if_duplicate_columns_have_same_value(self):
        csv_data = "a,a,a\n" "1,1,1\n" "2,2,2\n"

        df = pd.read_csv(StringIO(csv_data))
        assert list(df.columns) == ["a", "a.1", "a.2"]

        assert check_duplicate_columns(df, "file") is True

    def test_returns_False_if_duplicate_columns_have_different_values(self):
        csv_data = "a,a,a\n" "1,3,3\n" "2,4,4\n"

        df = pd.read_csv(StringIO(csv_data))
        assert list(df.columns) == ["a", "a.1", "a.2"]

        assert check_duplicate_columns(df, "file") is False

    def test_returns_None_if_column_end_with_number_but_is_not_duplicate(self):
        csv_data = "taxon taxon,taxon taxon f.1\n" "1,1\n" "2,2\n"

        df = pd.read_csv(StringIO(csv_data))
        assert list(df.columns) == ["taxon taxon", "taxon taxon f.1"]

        assert check_duplicate_columns(df, "file") is None

    def test_returns_None_for_unique_columns(self):
        csv_data = "aaa,bbb\n" "1,1\n" "2,2\n"

        df = pd.read_csv(StringIO(csv_data))
        assert list(df.columns) == ["aaa", "bbb"]

        assert check_duplicate_columns(df, "file") is None


class TestDeleteDuplicateColumns:
    def test_deletes_columns_with_same_names_and_same_values(self):
        csv_data = "a,a,a,b\n" "1,1,1,1\n" "2,2,2,2\n"
        df = pd.read_csv(StringIO(csv_data))
        csv_data2 = "a,b\n" "1,1\n" "2,2\n"
        expected = pd.read_csv(StringIO(csv_data2))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b"]
        assert_frame_equal(df, expected)

    def test_deletes_columns_with_surrounding_spaces_and_same_names_and_values(self):
        csv_data = "a,a , a,b\n" "1,1,1,1\n" "2,2,2,2\n"
        df = pd.read_csv(StringIO(csv_data))
        csv_data2 = "a,b\n" "1,1\n" "2,2\n"
        expected = pd.read_csv(StringIO(csv_data2))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b"]
        assert_frame_equal(df, expected)

    def test_ignores_columns_with_same_names_but_different_values(self):
        csv_data = "a,a,a,b\n" "1,2,3,1\n" "4,5,6,2\n"
        df = pd.read_csv(StringIO(csv_data))
        expected = pd.read_csv(StringIO(csv_data))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "a.1", "a.2", "b"]
        assert_frame_equal(df, expected)

    def test_ignores_columns_with_surrounding_spaces_and_same_names_but_different_values(self):
        csv_data = "a,a , a,b\n" "1,2,3,1\n" "4,5,6,2\n"
        df = pd.read_csv(StringIO(csv_data))
        expected = pd.read_csv(StringIO(csv_data))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "a ", " a", "b"]
        assert_frame_equal(df, expected)

    def test_ignores_columns_with_different_names_and_same_values(self):
        csv_data = "a,b\n" "1,1\n" "2,2\n"
        df = pd.read_csv(StringIO(csv_data))
        expected = pd.read_csv(StringIO(csv_data))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b"]
        assert_frame_equal(df, expected)


    def test_ignores_columns_with_surrounding_spaces_different_names_and_same_values(self):
        csv_data = "a,b \n" "1,1\n" "2,2\n"
        df = pd.read_csv(StringIO(csv_data))
        expected = pd.read_csv(StringIO(csv_data))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b "]
        assert_frame_equal(df, expected)


class TestRestoreDuplicateColumnNames:
    def test_returns_dataframe_with_original_column_names(self):
        csv_data = "a,a,a,b\n" "1,1,3,5\n" "2,2,4,6\n"
        original_columns = ["a", "a", "a", "b"]

        df = pd.read_csv(StringIO(csv_data))
        assert list(df.columns) == ["a", "a.1", "a.2", "b"]

        df = restore_duplicate_column_names(df, original_columns)
        assert list(df.columns) == original_columns

    def test_does_not_affect_columns_added_after_read_csv(self):
        csv_data = "a,a,a,b\n" "1,1,3,5\n" "2,2,4,6\n"
        original_columns = ["a", "a", "a", "b"]

        df = pd.read_csv(StringIO(csv_data))
        df["c"] = 7
        df["d"] = 8
        df["d.1"] = 9
        assert list(df.columns) == ["a", "a.1", "a.2", "b", "c", "d", "d.1"]

        df = restore_duplicate_column_names(df, original_columns)
        assert list(df.columns) == original_columns + ["c", "d", "d.1"]


class TestCleanTaxonName:
    def test_removes_extra_spaces(self):
        string = "   Aaa   bbb   "
        assert clean_taxon_name(string) == "Aaa bbb"


class TestTaxaNeedsReview:
    def test_returns_true_if_string_ends_with_parathesis_content(self):
        string = "aa (1)"
        assert taxa_needs_review(string) is True

    def test_returns_true_if_strings_ends_withgreater_than_distance(self):
        string = "aa > 1m"
        assert taxa_needs_review(string) is True

    def test_returns_true_if_strings_ends_with_underscore_letter(self):
        string = "aa _T"
        assert taxa_needs_review(string) is True

        string = "aa _T_"
        assert taxa_needs_review(string) is True

    def test_returns_false_otherwise(self):
        string = "aa"
        assert taxa_needs_review(string) is False


class TestRemoveWhitespace:
    def test_remove_leading_and_trailing_spaces_from_dataframe(self):
        data = {
            "A": ["A", "B ", "  C", "D  ", "  Ed  ", " 1 "],
            "B": ["Aa", "Bb ", "  Cc", "Dd  ", "  Ed Ed  ", " 11 "],
        }
        df = pd.DataFrame(data)
        data2 = {
            "A": ["A", "B", "C", "D", "Ed", "1"],
            "B": ["Aa", "Bb", "Cc", "Dd", "Ed Ed", "11"],
        }
        expected = pd.DataFrame(data2)

        remove_whitespace(df)

        assert_frame_equal(df, expected)

    def test_ignores_numeric_columns(self):
        data = {
            "A": ["A", "B  ", "  C"],
            "B": [1, 2, 3],
            "C": [1.1, 2.2, 3.3],
        }
        df = pd.DataFrame(data)
        data2 = {
            "A": ["A", "B", "C"],
            "B": [1, 2, 3],
            "C": [1.1, 2.2, 3.3],
        }
        expected = pd.DataFrame(data2)

        remove_whitespace(df)

        assert_frame_equal(df, expected)

    def test_handles_empty_strings(self):
        data = {"A": ["A", "B  ", "  C", " "]}
        df = pd.DataFrame(data)
        data2 = {"A": ["A", "B", "C", ""]}
        expected = pd.DataFrame(data2)

        remove_whitespace(df)

        assert_frame_equal(df, expected)

    def test_converts_nan_to_empty_strings(self):
        data = {"A": ["A", "B  ", "  C", np.nan]}
        df = pd.DataFrame(data)
        data2 = {"A": ["A", "B", "C", ""]}
        expected = pd.DataFrame(data2)

        remove_whitespace(df)

        assert_frame_equal(df, expected)
