from scripts.normalize_data import (
    tablerize,
    convert_column_names,
    normalize_sample_col,
    get_expedition_from_csv,
    create_sample_name,
    normalize_expedition_section_cols,
    extract_sample_parts,
    restore_integer_columns,
    update_metadata,
    replace_unnamed_xx_columns,
)
import pandas as pd
import numpy as np

from pandas._testing import assert_frame_equal
import pytest


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


class TestGetExpeditionFromCsv:
    def test_returns_expedition_from_Label_ID(self):
        df = pd.DataFrame({"Label ID": ["123-U4567A-1H-1-A"]})

        assert get_expedition_from_csv(df) == "123"

    def test_returns_expedition_from_Sample(self):
        df = pd.DataFrame({"Sample": ["123-U4567A-1H-1-A"]})

        assert get_expedition_from_csv(df) == "123"

    def test_returns_expedition_from_Exp(self):
        df = pd.DataFrame({"Exp": ["123-U4567A-1H-1-A"]})

        assert get_expedition_from_csv(df) == "123"

    def test_otherwise_raise_error(self):
        df = pd.DataFrame({"foo": ["123-U4567A-1H-1-A"]})

        message = "File does not expedition info."
        with pytest.raises(ValueError, match=message):
            get_expedition_from_csv(df)


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

    def test_no_data(self):
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


class TestExtractSampleParts:
    def test_extracts_sample_parts_from_a_valid_string(self):
        data = {
            "Label ID": ["1-U1h-2t-3-a", "10-U2H-20T-3-A"],
        }
        df = pd.DataFrame(data)

        data = {
            "Exp": ["1", "10"],
            "Site": ["U1", "U2"],
            "Hole": ["h", "H"],
            "Core": ["2", "20"],
            "Type": ["t", "T"],
            "Section": ["3", "3"],
            "A/W": ["a", "A"],
        }
        expected = pd.DataFrame(data)

        df = extract_sample_parts(df["Label ID"])
        assert_frame_equal(df, expected)

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

        df = extract_sample_parts(df["Label ID"])
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

        df = extract_sample_parts(df["Sample"])
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

        df = extract_sample_parts(df["Sample"])
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

        df = extract_sample_parts(df["Sample"])
        assert_frame_equal(df, expected)

    def test_rejects_exp_site_string(self):
        data = {
            "Sample": ["1-U1", "10-U2"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            df = extract_sample_parts(df["Sample"])

    def test_rejects_exp_string(self):
        data = {
            "Sample": ["1", "10"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            df = extract_sample_parts(df["Sample"])

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

        df = extract_sample_parts(df["Sample"])
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

        df = extract_sample_parts(df["Sample"])
        assert_frame_equal(df, expected)

    def test_otherwise_raise_error(self):
        data = {
            "Sample": ["AAA", "BBB"],
        }
        df = pd.DataFrame(data)

        message = "Sample name uses wrong format."
        with pytest.raises(ValueError, match=message):
            extract_sample_parts(df["Sample"])

class TestRestoreIntColumns:
    def test_integer_columns_are_changed_to_integers(self):
        df = pd.read_csv('./tests/data/missing_values.csv')
        assert isinstance(df['int'][0], np.float64)
        assert str(df['int'][0]) == '1.0'
        assert str(df['int'][1]) == '2.0'
        assert str(df['int'][2]) == '3.0'

        df = restore_integer_columns(df)

        assert isinstance(df['int'][0], np.int64)
        assert str(df['int'][0]) == '1'
        assert str(df['int'][1]) == '2'
        assert str(df['int'][2]) == '3'

    def test_integer_null_columns_are_changed_to_integers(self):
        df = pd.read_csv('./tests/data/missing_values.csv')
        assert isinstance(df['int null'][0], np.float64)
        assert str(df['int null'][0]) == '1.0'

        df = restore_integer_columns(df)

        assert isinstance(df['int null'][0], np.int64)
        assert str(df['int null'][0]) == '1'

    def test_integer_float_columns_remain_floats(self):
        df = pd.read_csv('./tests/data/missing_values.csv')
        assert isinstance(df['int float'][0], np.float64)
        assert str(df['int float'][0]) == '1.0'
        assert str(df['int float'][1]) == '2.0'
        assert str(df['int float'][2]) == '3.1'

        df = restore_integer_columns(df)

        assert isinstance(df['int float'][0], np.float64)
        assert str(df['int float'][0]) == '1.0'
        assert str(df['int float'][1]) == '2.0'
        assert str(df['int float'][2]) == '3.1'

class TestUpdateMetadata:
    def test_adds_new_column_to_dataframe_if_column_does_not_exists(self):
        metadata = pd.DataFrame({"a": [1,2]})
        dict = {"b": [3, 4]}
        new_metadata = update_metadata(metadata, dict)

        expected =  pd.DataFrame({"a": [1,2], "b": [3, 4]})

        assert_frame_equal(new_metadata, expected)

    def test_adds_new_column_to_dataframe_if_column_does_not_exists(self):
        metadata = pd.DataFrame({"a": [1,2], "b": [3, 4]})
        dict = {"b": [5, 6]}
        new_metadata = update_metadata(metadata, dict)

        expected =  pd.DataFrame({"a": [1,2], "b": [3, 4]})

        assert_frame_equal(new_metadata, expected)


class TestReplaceUnnamedXXColumns:
    def test_replace_unnamed_xx_with_empty_string(self):
        df = pd.DataFrame({
            "a": [1],
            "Unnamed: 1": [1],
            "Unnamed: 10": [1],
            "Unnamed: 1000": [1],
            "b": [1]
        })

        new_df = replace_unnamed_xx_columns(df)

        assert len(df.columns) == len(new_df.columns)
        assert new_df.columns[0] == 'a'
        assert new_df.columns[1] == ''
        assert new_df.columns[3] == ''
        assert new_df.columns[4] == 'b'

    def test_leaves_other_columns_unchanged(self):
        df = pd.DataFrame({
            "a": [1],
            "Bb": [1],
            "CC CC": [1]
        })

        new_df = replace_unnamed_xx_columns(df)

        assert len(df.columns) == len(new_df.columns)
        assert new_df.columns[0] == 'a'
        assert new_df.columns[1] == 'Bb'
        assert new_df.columns[2] == 'CC CC'
