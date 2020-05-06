from scripts.normalize_data import (
    tablerize,
    convert_column_names,
    normalize_sample_col,
    get_expedition_from_csv,
    create_sample_name,
)
import pandas as pd
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
