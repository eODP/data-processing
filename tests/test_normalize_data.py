from scripts.normalize_data import tablerize, convert_column_names


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
