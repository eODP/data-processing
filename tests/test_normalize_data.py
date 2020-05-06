from scripts.normalize_data import (
    tablerize,
    convert_column_names,
    get_expedition_from_csv,
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
