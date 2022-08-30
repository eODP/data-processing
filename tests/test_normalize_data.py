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
    check_duplicate_columns,
    restore_duplicate_column_names,
    clean_taxon_name,
    taxa_needs_review,
    remove_whitespace,
    delete_duplicate_columns,
    remove_bracket_text,
    remove_empty_unnamed_columns,
    normalize_abundance_codes,
    normalize_abundance_codes_group,
    normalize_switched_abundance_preservation,
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

    def test_creates_Sample_string_if_column_are_nan(self):
        data = {
            "Exp": [1],
            "Site": [np.nan],
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

    def test_creates_Sample_string_if_column_are_nan_2(self):
        data = {
            "Exp": [1],
            "Site": [np.nan],
            "Hole": [np.nan],
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

    def test_creates_Sample_string_if_column_are_nan_3(self):
        data = {
            "Exp": [1],
            "Site": [np.nan],
            "Hole": [np.nan],
            "Core": [np.nan],
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

    def test_creates_Sample_string_if_column_are_nan_4(self):
        data = {
            "Exp": [1],
            "Site": [np.nan],
            "Hole": [np.nan],
            "Core": [np.nan],
            "Type": [np.nan],
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

    def test_creates_Sample_string_if_column_are_nan_5(self):
        data = {
            "Exp": [1],
            "Site": [np.nan],
            "Hole": [np.nan],
            "Core": [np.nan],
            "Type": [np.nan],
            "Section": [np.nan],
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

    def test_creates_Sample_string_if_column_are_nan_6(self):
        data = {
            "Exp": [1],
            "Site": [np.nan],
            "Hole": [np.nan],
            "Core": [np.nan],
            "Type": [np.nan],
            "Section": [np.nan],
            "A/W": [np.nan],
        }
        df = pd.DataFrame(data, dtype=str)
        data["Sample"] = ["1"]
        expected = pd.DataFrame(data, dtype=str)

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

    def test_removes_dash_from_end_of_string_nan(self):
        data = {
            "Exp": [1],
            "Site": [np.nan],
            "Hole": [np.nan],
            "Core": [np.nan],
            "Type": [np.nan],
            "Section": [3],
            "A/W": [np.nan],
        }
        df = pd.DataFrame(data, dtype=str)
        data["Sample"] = ["1-3"]
        expected = pd.DataFrame(data, dtype=str)

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

    def test_removes_dash_from_end_of_string_nan_2(self):
        data = {
            "Exp": [1],
            "Site": [np.nan],
            "Hole": [np.nan],
            "Core": [np.nan],
            "Type": ["t"],
            "Section": [np.nan],
            "A/W": [np.nan],
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
        }
        df = pd.DataFrame(data)
        data = {
            "Col": [0, 1],
            "Sample": ["1-U1h-2t-3", "10-U2H-20T-3"],
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": ["t", "T"],
            "Section": ["3", "3"],
            "A/W": [None, None],
        }
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

    def test_ignores_ending_interval(self):
        data = {
            "Sample": ["1-U1h-2t-3, 0-20", "10-U2H-20T-3"],
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
    def test_replace_column_name_with_value_from_columns_mapping(self):
        columns_mapping = {"aa": "A"}
        data = {"aa": [1]}
        df = pd.DataFrame(data)
        data = {"A": [1]}
        expected = pd.DataFrame(data)

        normalize_columns(df, columns_mapping)

        assert_frame_equal(df, expected)

    def test_replace_multiple_column_name_with_value_from_columns_mapping(self):
        columns_mapping = {"aa": "A", "b b": "B"}
        data = {"aa": [1], "b b": [2]}
        df = pd.DataFrame(data)
        data = {"A": [1], "B": [2]}
        expected = pd.DataFrame(data)

        normalize_columns(df, columns_mapping)

        assert_frame_equal(df, expected)

    def test_does_not_affect_columns_not_in_columns_mapping(self):
        columns_mapping = {"aa": "A", "b b": "B"}
        data = {"aa": [1], "b b": [2], "cc": [3]}
        df = pd.DataFrame(data)
        data = {"A": [1], "B": [2], "cc": [3]}
        expected = pd.DataFrame(data)

        normalize_columns(df, columns_mapping)

        assert_frame_equal(df, expected)

    def test_does_not_affect_columns_if_columns_mapping_has_no_value(self):
        columns_mapping = {"aa": None, "bb": "", "cc": np.nan}
        data = {"aa": [1], "b b": [2], "cc": [3]}
        df = pd.DataFrame(data)
        expected = pd.DataFrame(data)

        normalize_columns(df, columns_mapping)

        assert_frame_equal(df, expected)


class TestCompareDuplicateColumns:
    def test_returns_True_if_duplicate_columns_have_same_value(self):
        csv_data = "a,a,a\n" "1,1,1\n" "2,2,2\n"

        df = pd.read_csv(StringIO(csv_data))
        assert list(df.columns) == ["a", "a.1", "a.2"]

        expected = [
            {"filename": "file", "bad_column": "a.1", "same_value": True},
            {"filename": "file", "bad_column": "a.2", "same_value": True},
        ]
        assert check_duplicate_columns(df, "file") == expected

    def test_returns_False_if_duplicate_columns_have_different_values(self):
        csv_data = "a,a,a\n" "1,3,3\n" "2,4,4\n"

        df = pd.read_csv(StringIO(csv_data))
        assert list(df.columns) == ["a", "a.1", "a.2"]

        expected = [
            {"filename": "file", "bad_column": "a.1", "same_value": False},
            {"filename": "file", "bad_column": "a.2", "same_value": False},
        ]
        assert check_duplicate_columns(df, "file") == expected

    def test_returns_empty_list_if_column_end_with_number_but_is_not_duplicate(self):
        csv_data = "taxon taxon,taxon taxon f.1\n" "1,1\n" "2,2\n"

        df = pd.read_csv(StringIO(csv_data))
        assert list(df.columns) == ["taxon taxon", "taxon taxon f.1"]

        assert check_duplicate_columns(df, "file") == []

    def test_returns_empty_list_for_unique_columns(self):
        csv_data = "aaa,bbb\n" "1,1\n" "2,2\n"

        df = pd.read_csv(StringIO(csv_data))
        assert list(df.columns) == ["aaa", "bbb"]

        assert check_duplicate_columns(df, "file") == []

    def test_returns_True_if_space_columns_have_similiar_names_and_same_values(self):
        csv_data = "a,a \n" "1,1\n" "2,2\n"

        df = pd.read_csv(StringIO(csv_data))
        assert list(df.columns) == ["a", "a "]

        expected = [{"bad_column": "a ", "filename": "file", "same_value": True}]
        assert check_duplicate_columns(df, "file") == expected

    def test_returns_False_if_space_columns_have_similiar_names_but_different_values(
        self,
    ):
        csv_data = "a,a \n" "1,3\n" "2,4\n"

        df = pd.read_csv(StringIO(csv_data))
        assert list(df.columns) == ["a", "a "]

        expected = [{"bad_column": "a ", "filename": "file", "same_value": False}]
        assert check_duplicate_columns(df, "file") == expected

    def test_returns_empty_list_if_space_columns_have_differnt_names(self):
        csv_data = "a,b \n" "1,1\n" "2,2\n"
        df = pd.read_csv(StringIO(csv_data))

        assert list(df.columns) == ["a", "b "]
        assert check_duplicate_columns(df, "file") == []


class TestDeleteDuplicateColumns:
    def test_deletes_columns_with_same_names_and_same_values(self):
        csv_data = "a,a,a,b\n" "1,1,1,1\n" "2,2,2,2\n"
        df = pd.read_csv(StringIO(csv_data))
        csv_data2 = "a,b\n" "1,1\n" "2,2\n"
        expected = pd.read_csv(StringIO(csv_data2))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b"]
        assert_frame_equal(df, expected)

    def test_deletes_multiple_columns_with_same_names_and_same_values(self):
        csv_data = "a,b,a,b\n" "1,3,1,3\n" "2,4,2,4\n"
        df = pd.read_csv(StringIO(csv_data))
        csv_data2 = "a,b\n" "1,3\n" "2,4\n"
        expected = pd.read_csv(StringIO(csv_data2))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b"]
        assert_frame_equal(df, expected)

    def test_deletes_columns_with_same_names_and_same_values_with_nan(self):
        csv_data = "a,a,a,b\n" "1,1,1,1\n" f"{np.nan},{np.nan},{np.nan},2\n"
        df = pd.read_csv(StringIO(csv_data))
        csv_data2 = "a,b\n" f"1,1\n" f"{np.nan},2\n"
        expected = pd.read_csv(StringIO(csv_data2))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b"]
        assert_frame_equal(df, expected)

    def test_deletes_columns_with_same_names_and_all_nan(self):
        csv_data = (
            "a,a,a,b\n"
            f"{np.nan},{np.nan},{np.nan},1\n"
            f"{np.nan},{np.nan},{np.nan},2\n"
        )
        df = pd.read_csv(StringIO(csv_data))
        csv_data2 = "a,b\n" f"{np.nan},1\n" f"{np.nan},2\n"
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

    def test_ignores_columns_with_different_names_and_same_values(self):
        csv_data = "a,b\n" "1,1\n" "2,2\n"
        df = pd.read_csv(StringIO(csv_data))
        expected = pd.read_csv(StringIO(csv_data))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b"]
        assert_frame_equal(df, expected)

    @pytest.mark.parametrize(
        "csv_data",
        [
            "a,a , a,b\n" "1,1,1,1\n" "2,2,2,2\n",
            "a, a,a ,b\n" "1,1,1,1\n" "2,2,2,2\n",
            " a,a,a ,b\n" "1,1,1,1\n" "2,2,2,2\n",
            "a ,a, a,b\n" "1,1,1,1\n" "2,2,2,2\n",
        ],
    )
    def test_deletes_columns_with_surrounding_spaces_and_same_names_and_values(
        self, csv_data
    ):
        df = pd.read_csv(StringIO(csv_data))
        csv_data2 = "a,b\n" "1,1\n" "2,2\n"
        expected = pd.read_csv(StringIO(csv_data2))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b"]
        assert_frame_equal(df, expected)

    def test_deletes_multiple_columns_with_spaces_and_same_names_and_same_values(
        self,
    ):
        csv_data = "a,b ,a ,b\n" "1,3,1,3\n" "2,4,2,4\n"
        df = pd.read_csv(StringIO(csv_data))
        csv_data2 = "a,b\n" "1,3\n" "2,4\n"
        expected = pd.read_csv(StringIO(csv_data2))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b"]
        assert_frame_equal(df, expected)

    def test_deletes_columns_with_spaces_and_same_names_and_same_values_with_nan(self):
        csv_data = "a, a, a,b\n" "1,1,1,1\n" f"{np.nan},{np.nan},{np.nan},2\n"
        df = pd.read_csv(StringIO(csv_data))
        csv_data2 = "a,b\n" f"1,1\n" f"{np.nan},2\n"
        expected = pd.read_csv(StringIO(csv_data2))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b"]
        assert_frame_equal(df, expected)

    def test_deletes_columns_with_spaces_and_same_names_and_all_nan(self):
        csv_data = (
            "a, a, a,b\n"
            f"{np.nan},{np.nan},{np.nan},1\n"
            f"{np.nan},{np.nan},{np.nan},2\n"
        )
        df = pd.read_csv(StringIO(csv_data))
        csv_data2 = "a,b\n" f"{np.nan},1\n" f"{np.nan},2\n"
        expected = pd.read_csv(StringIO(csv_data2))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "b"]
        assert_frame_equal(df, expected)

    def test_ignores_columns_with_spaces_and_same_names_but_different_values(
        self,
    ):
        csv_data = "a,a , a,b\n" "1,2,3,1\n" "4,5,6,2\n"
        df = pd.read_csv(StringIO(csv_data))
        expected = pd.read_csv(StringIO(csv_data))

        delete_duplicate_columns(df)

        assert list(df.columns) == ["a", "a ", " a", "b"]
        assert_frame_equal(df, expected)

    def test_ignores_columns_with_surrounding_spaces_different_names_and_same_values(
        self,
    ):
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


class TestRemoveBracketText:
    def test_removes_text_within_brackets_at_end_of_cell(self):
        df = pd.DataFrame(["aa [A]", "bb [BB]", "cc [C] ", "dd  [dd]  "])
        expected = pd.DataFrame(["aa", "bb", "cc", "dd"])

        remove_bracket_text(df)

        assert_frame_equal(df, expected)

    def test_does_not_remove_text_within_brackets_at_start_of_cell(self):
        df = pd.DataFrame(["[A] aa", "[BB] bb", "[C] cc ", "  [dd]  dd "])
        expected = df.copy()

        remove_bracket_text(df)

        assert_frame_equal(df, expected)

    def test_does_not_remove_text_within_brackets_in_middle_of_cell(self):
        df = pd.DataFrame(["aa [A] aa", "bb [BB] bb", " cc [C] cc ", " dd  [dd]  dd "])
        expected = df.copy()

        remove_bracket_text(df)

        assert_frame_equal(df, expected)

    def test_removes_letters_numbers_punctuation_within_brackets(self):
        df = pd.DataFrame(["aa [A A]", "bb [BB 123]", "cc [123-456.] "])
        expected = pd.DataFrame(["aa", "bb", "cc"])

        remove_bracket_text(df)

        assert_frame_equal(df, expected)


class TestRemoveEmptyUnnamedColumns:
    def test_remove_unnamed_columns_with_no_content(self):
        data = {"A": [1, 2, 3], "B": ["a", "b", "c"], "Unnamed: 12": [None, None, None]}
        df = pd.DataFrame(data)
        data = {"A": [1, 2, 3], "B": ["a", "b", "c"]}
        expected = pd.DataFrame(data)

        remove_empty_unnamed_columns(df)

        assert_frame_equal(df, expected)

    def test_does_change_named_columns_without_content(self):
        data = {"A": [1, 2, 3], "B": ["a", "b", "c"], "C": [None, None, None]}
        df = pd.DataFrame(data)
        expected = pd.DataFrame(data)

        remove_empty_unnamed_columns(df)

        assert_frame_equal(df, expected)

    def test_does_change_unnamed_columns_with_content(self):
        data = {"A": [1, 2, 3], "B": ["a", "b", "c"], "Unnamed: 12": ["a", None, None]}
        df = pd.DataFrame(data)
        expected = pd.DataFrame(data)

        remove_empty_unnamed_columns(df)

        assert_frame_equal(df, expected)


class TestNormalizeAbundanceCodes:
    def create_df(self):
        return pd.DataFrame(
            [
                {"Exp": "1", "taxon A": "a"},
                {"Exp": "1", "taxon A": np.nan},
                {"Exp": "1", "taxon A": "aa"},
            ]
        )

    def create_multi_df(self):
        return pd.DataFrame(
            [
                {"Exp": "1", "taxon A": "a", "taxon B": np.nan, "taxon C": "cc"},
                {"Exp": "1", "taxon A": np.nan, "taxon B": "bb", "taxon C": "c"},
                {"Exp": "1", "taxon A": "aa", "taxon B": "b", "taxon C": np.nan},
            ]
        )

    def test_no_changes_if_original_and_normalized_abundances_are_the_same(
        self,
    ):
        file_taxon_group = "group 2"
        codes_data = [
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "a",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "aa",
            },
        ]
        codes_df = pd.DataFrame(codes_data)
        verbatim_names_taxon_groups = {"taxon A": ["group 1"]}

        expected_df = self.create_df()

        result = normalize_abundance_codes(
            self.create_df(),
            file_taxon_group,
            codes_df,
            verbatim_names_taxon_groups,
        )

        assert result["changed"] == False
        assert_frame_equal(result["df"], expected_df)

    def test_change_abundances_if_different_abundances_same_expedition_same_group(
        self,
    ):
        file_taxon_group = "group 2"
        codes_data = [
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "z",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "aa",
            },
        ]
        codes_df = pd.DataFrame(codes_data)
        verbatim_names_taxon_groups = {"taxon A": ["group 1"]}

        expected_df = pd.DataFrame(
            [
                {"Exp": "1", "taxon A": "z"},
                {"Exp": "1", "taxon A": np.nan},
                {"Exp": "1", "taxon A": "aa"},
            ]
        )

        result = normalize_abundance_codes(
            self.create_df(),
            file_taxon_group,
            codes_df,
            verbatim_names_taxon_groups,
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected_df)

    def test_ignore_normalized_abundances_from_different_expeditions(self):
        file_taxon_group = "group 2"
        codes_data = [
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "z",
            },
            {
                "original_abundance": "a",
                "expedition": "10",
                "taxon_group": "group 1",
                "normalized_abundance": "y",
            },
            {
                "original_abundance": "aa",
                "expedition": "10",
                "taxon_group": "group 1",
                "normalized_abundance": "yy",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "aa",
            },
        ]
        codes_df = pd.DataFrame(codes_data)
        verbatim_names_taxon_groups = {"taxon A": ["group 1"]}

        expected_df = pd.DataFrame(
            [
                {"Exp": "1", "taxon A": "z"},
                {"Exp": "1", "taxon A": np.nan},
                {"Exp": "1", "taxon A": "aa"},
            ]
        )

        result = normalize_abundance_codes(
            self.create_df(),
            file_taxon_group,
            codes_df,
            verbatim_names_taxon_groups,
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected_df)

    def test_ignore_normalized_abundances_from_different_taxon_group(self):
        file_taxon_group = "group 1"
        codes_data = [
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "z",
            },
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 2",
                "normalized_abundance": "y",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 2",
                "normalized_abundance": "yy",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "aa",
            },
        ]
        codes_df = pd.DataFrame(codes_data)
        verbatim_names_taxon_groups = {"taxon A": ["group 1"]}

        expected_df = pd.DataFrame(
            [
                {"Exp": "1", "taxon A": "z"},
                {"Exp": "1", "taxon A": np.nan},
                {"Exp": "1", "taxon A": "aa"},
            ]
        )

        result = normalize_abundance_codes(
            self.create_df(),
            file_taxon_group,
            codes_df,
            verbatim_names_taxon_groups,
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected_df)

    def test_uses_taxon_group_from_verbatim_names_taxon_groups_if_taxon_has_one_group(
        self,
    ):
        file_taxon_group = "group 2"
        codes_data = [
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 2",
                "normalized_abundance": "y",
            },
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "z",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "aa",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 2",
                "normalized_abundance": "yy",
            },
        ]
        codes_df = pd.DataFrame(codes_data)
        verbatim_names_taxon_groups = {"taxon A": ["group 1"]}

        expected_df = pd.DataFrame(
            [
                {"Exp": "1", "taxon A": "z"},
                {"Exp": "1", "taxon A": np.nan},
                {"Exp": "1", "taxon A": "aa"},
            ]
        )

        result = normalize_abundance_codes(
            self.create_df(),
            file_taxon_group,
            codes_df,
            verbatim_names_taxon_groups,
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected_df)

    def test_uses_taxon_group_from_file_if_taxon_has_multiple_groups(self):
        file_taxon_group = "group 1"
        codes_data = [
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 2",
                "normalized_abundance": "y",
            },
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "z",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "aa",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 2",
                "normalized_abundance": "yy",
            },
        ]
        codes_df = pd.DataFrame(codes_data)
        verbatim_names_taxon_groups = {"taxon A": ["group 2", "group 1"]}

        expected_df = pd.DataFrame(
            [
                {"Exp": "1", "taxon A": "z"},
                {"Exp": "1", "taxon A": np.nan},
                {"Exp": "1", "taxon A": "aa"},
            ]
        )

        result = normalize_abundance_codes(
            self.create_df(),
            file_taxon_group,
            codes_df,
            verbatim_names_taxon_groups,
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected_df)

    def test_handles_multiple_taxa_and_taxon_groups(self):
        file_taxon_group = "group 2"
        codes_data = [
            {
                "original_abundance": "b",
                "expedition": "1",
                "taxon_group": "group 2",
                "normalized_abundance": "b",
            },
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "z",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "aa",
            },
            {
                "original_abundance": "bb",
                "expedition": "1",
                "taxon_group": "group 2",
                "normalized_abundance": "yy",
            },
            {
                "original_abundance": "c",
                "expedition": "1",
                "taxon_group": "group 3",
                "normalized_abundance": "c",
            },
            {
                "original_abundance": "cc",
                "expedition": "1",
                "taxon_group": "group 3",
                "normalized_abundance": "cc",
            },
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 3",
                "normalized_abundance": "x",
            },
        ]
        codes_df = pd.DataFrame(codes_data)
        verbatim_names_taxon_groups = {
            "taxon A": ["group 1"],
            "taxon B": ["group 2"],
            "taxon C": ["group 3"],
        }

        expected_df = pd.DataFrame(
            [
                {"Exp": "1", "taxon A": "z", "taxon B": np.nan, "taxon C": "cc"},
                {"Exp": "1", "taxon A": np.nan, "taxon B": "yy", "taxon C": "c"},
                {"Exp": "1", "taxon A": "aa", "taxon B": "b", "taxon C": np.nan},
            ]
        )

        result = normalize_abundance_codes(
            self.create_multi_df(),
            file_taxon_group,
            codes_df,
            verbatim_names_taxon_groups,
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected_df)

    def test_return_original_df_if_taxa_not_in_verbatim_names(self):
        file_taxon_group = "group 2"
        codes_data = [
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "a",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "aa",
            },
        ]
        codes_df = pd.DataFrame(codes_data)
        verbatim_names_taxon_groups = {"taxon C": ["group 1"]}
        expected = self.create_df()

        result = normalize_abundance_codes(
            self.create_df(),
            file_taxon_group,
            codes_df,
            verbatim_names_taxon_groups,
        )

        assert result["changed"] == False
        assert_frame_equal(result["df"], expected)

    def test_raise_error_if_df_has_taxon_does_not_have_taxon_groups(self):
        demo_df = pd.DataFrame(
            [
                {"Exp": "1", "taxon A": "a"},
                {"Exp": "1", "taxon A": np.nan},
                {"Exp": "1", "taxon A": "aa"},
            ]
        )
        file_taxon_group = "group 2"
        codes_data = [
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "a",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "aa",
            },
        ]
        codes_df = pd.DataFrame(codes_data)
        verbatim_names_taxon_groups = {"taxon A": []}

        message = "taxon A does not have taxon groups."
        with pytest.raises(ValueError, match=message):
            normalize_abundance_codes(
                demo_df,
                file_taxon_group,
                codes_df,
                verbatim_names_taxon_groups,
            )

    def test_raise_error_if_file_taxon_group_does_not_match_taxa_taxon_groups(self):
        demo_df = pd.DataFrame(
            [
                {"Exp": "1", "taxon A": "a"},
                {"Exp": "1", "taxon A": np.nan},
                {"Exp": "1", "taxon A": "aa"},
            ]
        )
        file_taxon_group = "group 2"
        codes_data = [
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "a",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 1",
                "normalized_abundance": "aa",
            },
            {
                "original_abundance": "a",
                "expedition": "1",
                "taxon_group": "group 2",
                "normalized_abundance": "z",
            },
            {
                "original_abundance": "aa",
                "expedition": "1",
                "taxon_group": "group 2",
                "normalized_abundance": "zz",
            },
        ]
        codes_df = pd.DataFrame(codes_data)
        verbatim_names_taxon_groups = {"taxon A": ["group 1", "group 3"]}

        message = "taxon A does not belong to group 2."
        with pytest.raises(ValueError, match=message):
            normalize_abundance_codes(
                demo_df,
                file_taxon_group,
                codes_df,
                verbatim_names_taxon_groups,
            )


class TestNormalizeAbundanceCodesGroup:
    def create_df(self):
        return pd.DataFrame(
            [
                {"Exp": "1", "header1": "a"},
                {"Exp": "1", "header1": np.nan},
                {"Exp": "1", "header1": "b"},
            ]
        )

    def test_no_changes_if_original_and_normalized_abundances_are_the_same(self):
        df = self.create_df()
        path = "file.csv"
        codes_df = pd.DataFrame(
            [
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "abundance_code": "a",
                    "harmonized_code": "a",
                    "file": path,
                },
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "abundance_code": "b",
                    "harmonized_code": "b",
                    "file": path,
                },
            ]
        )

        taxon_group = "taxon1"
        expected = df

        result = normalize_abundance_codes_group(df, codes_df, taxon_group, path)

        assert result["changed"] == False
        assert_frame_equal(result["df"], expected)

    def test_changes_abundance_if_same_expedition_and_taxon_group(self):
        df = self.create_df()
        path = "file.csv"
        codes_df = pd.DataFrame(
            [
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "abundance_code": "a",
                    "harmonized_code": "AA",
                    "file": path,
                },
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "abundance_code": "b",
                    "harmonized_code": "BB",
                    "file": path,
                },
            ]
        )

        taxon_group = "taxon1"
        expected = pd.DataFrame(
            [
                {"Exp": "1", "header1": "AA"},
                {"Exp": "1", "header1": np.nan},
                {"Exp": "1", "header1": "BB"},
            ]
        )

        result = normalize_abundance_codes_group(df, codes_df, taxon_group, path)

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected)

    def test_ignore_normalized_abundances_from_different_expeditions(self):
        df = self.create_df()
        path = "file.csv"
        codes_df = pd.DataFrame(
            [
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "abundance_code": "a",
                    "harmonized_code": "AA",
                    "file": path,
                },
                {
                    "Exp": "100",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "abundance_code": "b",
                    "harmonized_code": "BB",
                    "file": path,
                },
            ]
        )

        taxon_group = "taxon1"
        expected = pd.DataFrame(
            [
                {"Exp": "1", "header1": "AA"},
                {"Exp": "1", "header1": np.nan},
                {"Exp": "1", "header1": "b"},
            ]
        )

        result = normalize_abundance_codes_group(df, codes_df, taxon_group, path)

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected)

    def test_ignore_normalized_abundances_from_different_taxon_group(self):
        df = self.create_df()
        path = "file.csv"
        codes_df = pd.DataFrame(
            [
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "abundance_code": "a",
                    "harmonized_code": "AA",
                    "file": path,
                },
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon2",
                    "abundance_code": "b",
                    "harmonized_code": "BB",
                    "file": path,
                },
            ]
        )

        taxon_group = "taxon1"
        expected = pd.DataFrame(
            [
                {"Exp": "1", "header1": "AA"},
                {"Exp": "1", "header1": np.nan},
                {"Exp": "1", "header1": "b"},
            ]
        )

        result = normalize_abundance_codes_group(df, codes_df, taxon_group, path)

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected)

    def test_handles_multiple_columns(self):
        df = pd.DataFrame(
            [
                {"Exp": "1", "header1": "a", "header2": "c"},
                {"Exp": "1", "header1": np.nan, "header2": "d"},
                {"Exp": "1", "header1": "b", "header2": np.nan},
            ]
        )
        path = "file.csv"
        codes_df = pd.DataFrame(
            [
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "abundance_code": "a",
                    "harmonized_code": "AA",
                    "file": path,
                },
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "abundance_code": "b",
                    "harmonized_code": "BB",
                    "file": path,
                },
                {
                    "Exp": "1",
                    "original_header": "header2",
                    "taxon_group": "taxon1",
                    "abundance_code": "c",
                    "harmonized_code": "CC",
                    "file": path,
                },
                {
                    "Exp": "1",
                    "original_header": "header2",
                    "taxon_group": "taxon1",
                    "abundance_code": "d",
                    "harmonized_code": "d",
                    "file": path,
                },
            ]
        )
        taxon_group = "taxon1"
        expected = pd.DataFrame(
            [
                {"Exp": "1", "header1": "AA", "header2": "CC"},
                {"Exp": "1", "header1": np.nan, "header2": "d"},
                {"Exp": "1", "header1": "BB", "header2": np.nan},
            ]
        )

        result = normalize_abundance_codes_group(df, codes_df, taxon_group, path)

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected)


class TestNormalizeSwitchedAbundancePreservation:
    def create_df(self):
        return pd.DataFrame(
            [
                {"Exp": "1", "header1": "a", "header2": "c"},
                {"Exp": "1", "header1": np.nan, "header2": "d"},
                {"Exp": "1", "header1": "b", "header2": np.nan},
            ]
        )

    def create_fixed_df(self):
        return pd.DataFrame(
            [
                {"Exp": "1", "header1": "AA", "header2": "CC"},
                {"Exp": "1", "header1": np.nan, "header2": "DD"},
                {"Exp": "1", "header1": "BB", "header2": np.nan},
            ]
        )

    def test_set_values_for_original_header_with_values_from_fixed_df(self):
        df = self.create_df()
        fixed_df = self.create_fixed_df()
        path = "file.csv"
        codes_df = pd.DataFrame(
            [
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "file": path,
                },
            ]
        )

        taxon_group = "taxon1"
        expected = pd.DataFrame(
            [
                {"Exp": "1", "header1": "AA", "header2": "c"},
                {"Exp": "1", "header1": np.nan, "header2": "d"},
                {"Exp": "1", "header1": "BB", "header2": np.nan},
            ]
        )

        result = normalize_switched_abundance_preservation(
            df, codes_df, taxon_group, fixed_df, path
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected)

    def test_handles_file_with_multiple_values(self):
        df = self.create_df()
        fixed_df = self.create_fixed_df()
        path = "file.csv"
        codes_df = pd.DataFrame(
            [
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "file": f"{path}; file2.csv",
                },
            ]
        )

        taxon_group = "taxon1"
        expected = pd.DataFrame(
            [
                {"Exp": "1", "header1": "AA", "header2": "c"},
                {"Exp": "1", "header1": np.nan, "header2": "d"},
                {"Exp": "1", "header1": "BB", "header2": np.nan},
            ]
        )

        result = normalize_switched_abundance_preservation(
            df, codes_df, taxon_group, fixed_df, path
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected)

    def test_ignore_original_header_from_different_expeditions(self):
        df = self.create_df()
        fixed_df = self.create_fixed_df()
        path = "file.csv"
        codes_df = pd.DataFrame(
            [
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "file": path,
                },
                {
                    "Exp": "100",
                    "original_header": "header2",
                    "taxon_group": "taxon1",
                    "file": path,
                },
            ]
        )
        taxon_group = "taxon1"
        path = "file.csv"
        expected = pd.DataFrame(
            [
                {"Exp": "1", "header1": "AA", "header2": "c"},
                {"Exp": "1", "header1": np.nan, "header2": "d"},
                {"Exp": "1", "header1": "BB", "header2": np.nan},
            ]
        )

        result = normalize_switched_abundance_preservation(
            df, codes_df, taxon_group, fixed_df, path
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected)

    def test_ignore_original_header_from_different_taxon_group(self):
        df = self.create_df()
        fixed_df = self.create_fixed_df()
        path = "file.csv"
        codes_df = pd.DataFrame(
            [
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "file": path,
                },
                {
                    "Exp": "1",
                    "original_header": "header2",
                    "taxon_group": "taxon2",
                    "file": path,
                },
            ]
        )
        taxon_group = "taxon1"
        expected = pd.DataFrame(
            [
                {"Exp": "1", "header1": "AA", "header2": "c"},
                {"Exp": "1", "header1": np.nan, "header2": "d"},
                {"Exp": "1", "header1": "BB", "header2": np.nan},
            ]
        )

        result = normalize_switched_abundance_preservation(
            df, codes_df, taxon_group, fixed_df, path
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected)

    def test_ignore_original_header_for_different_file(self):
        df = self.create_df()
        fixed_df = self.create_fixed_df()
        path = "file.csv"
        codes_df = pd.DataFrame(
            [
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "file": path,
                },
                {
                    "Exp": "1",
                    "original_header": "header2",
                    "taxon_group": "taxon1",
                    "file": "file2.csv; file3.csv",
                },
            ]
        )
        taxon_group = "taxon1"
        expected = pd.DataFrame(
            [
                {"Exp": "1", "header1": "AA", "header2": "c"},
                {"Exp": "1", "header1": np.nan, "header2": "d"},
                {"Exp": "1", "header1": "BB", "header2": np.nan},
            ]
        )

        result = normalize_switched_abundance_preservation(
            df, codes_df, taxon_group, fixed_df, path
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected)

    def test_handles_multiple_original_header(self):
        df = self.create_df()
        fixed_df = self.create_fixed_df()
        path = "file.csv"

        codes_df = pd.DataFrame(
            [
                {
                    "Exp": "1",
                    "original_header": "header1",
                    "taxon_group": "taxon1",
                    "file": path,
                },
                {
                    "Exp": "1",
                    "original_header": "header2",
                    "taxon_group": "taxon1",
                    "file": path,
                },
            ]
        )
        taxon_group = "taxon1"
        expected = pd.DataFrame(
            [
                {"Exp": "1", "header1": "AA", "header2": "CC"},
                {"Exp": "1", "header1": np.nan, "header2": "DD"},
                {"Exp": "1", "header1": "BB", "header2": np.nan},
            ]
        )

        result = normalize_switched_abundance_preservation(
            df, codes_df, taxon_group, fixed_df, path
        )

        assert result["changed"] == True
        assert_frame_equal(result["df"], expected)
