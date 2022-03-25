from scripts.space_delim import (
    get_headers,
    is_standard_header,
    convert_space_delim_file,
)


class TestIsStandardHeader:
    def test_returns_true_for_Age_From_oldest(self):
        header1 = "Age "
        header2 = "From (oldest) "
        assert is_standard_header(header1, header2) is True

    def test_returns_true_for_Age_To_youngest(self):
        header1 = "Age "
        header2 = "To (youngest) "
        assert is_standard_header(header1, header2) is True

    def test_returns_true_for_Zone_From_bottom(self):
        header1 = "Zone "
        header2 = "From (bottom) "
        assert is_standard_header(header1, header2) is True

    def test_returns_true_for_Zone_To_top(self):
        header1 = "Zone "
        header2 = "To (top) "
        assert is_standard_header(header1, header2) is True

    def test_returns_true_for_Fossil_Group(self):
        header1 = "Fossil "
        header2 = "Group "
        assert is_standard_header(header1, header2) is True

    def test_returns_true_for_Group_Abundance(self):
        header1 = "Group "
        header2 = "Abundance "
        assert is_standard_header(header1, header2) is True

    def test_returns_true_for_Group_Preservation(self):
        header1 = "Group "
        header2 = "Preservation "
        assert is_standard_header(header1, header2) is True

    def test_handles_extra_spaces(self):
        header1 = "    Zone     "
        header2 = "    To    (top)    "
        assert is_standard_header(header1, header2) is True

    def test_handles_no_trailing_spaces(self):
        header1 = "Zone"
        header2 = "To (top)"
        assert is_standard_header(header1, header2) is True

    def test_otherwise_returns_false(self):
        header1 = "Foo"
        header2 = "Bar"
        assert is_standard_header(header1, header2) is False


class TestGetHeaders:
    def test_converts_string_into_list_of_phrases_based_on_capitialized_letters(self):
        header_string = "Header one Header (two) three A 1 header"
        expected = [
            "Header one ",
            "Header (two) three ",
            "A 1 header",
        ]

        assert get_headers(header_string) == expected

    def test_returns_standard_headers(selg):
        header_string = "Age From (oldest) Age To (youngest) Foo1 Fossil Group Foo2"
        expected = [
            "Age From (oldest) ",
            "Age To (youngest) ",
            "Foo1 ",
            "Fossil Group ",
            "Foo2",
        ]

        assert get_headers(header_string) == expected

    def test_handles_headers_with_extra_spaces(selg):
        header_string = "Age To   (youngest)   Foo1   Fossil   Group   Foo2"
        expected = [
            "Age To   (youngest)   ",
            "Foo1   ",
            "Fossil   Group   ",
            "Foo2",
        ]

        assert get_headers(header_string) == expected

    def test_handles_headers_with_paranthesis(selg):
        header_string = "Header (One 1 Aaa 1) 1 Header b Header (Three) c "
        expected = ["Header (One 1 Aaa 1) 1 ", "Header b ", "Header (Three) c "]

        assert get_headers(header_string) == expected

    def test_handles_headers_with_species_modifiers(selg):
        header_string = "Genus species Genus sp. A Genus Genus sp. G. species "
        expected = ["Genus species ", "Genus sp. A ", "Genus ", "Genus sp. G. species "]

        assert get_headers(header_string) == expected

    def test_handles_headers_when_one_letter(selg):
        header_string = "Header1 A Site H Cor T "
        expected = ["Header1 ", "A ", "Site ", "H ", "Cor ", "T "]

        assert get_headers(header_string) == expected

    def test_handles_headers_when_Xxxx_Form_X(self):
        header_string = "Header1 one Genus species Form A Header 2 two "
        expected = ["Header1 one ", "Genus species Form A ", "Header 2 two "]

        assert get_headers(header_string) == expected


class TestConvertSpaceDelimFile:
    def test_ignores_Abbreviated_View_and_blank_lines_to_form_headers(self):
        path = "./tests/data/space_delim.txt"
        df = convert_space_delim_file(path)

        expected_columns = [
            "Data",
            "Age From (oldest)",
            "Age To (youngest)",
            "Zone From (bottom)",
            "Zone To (top)",
            "Leg",
            "Site",
            "H",
            "Cor",
            "T",
            "Sc",
            "Top(cm)",
            "Depth (mbsf)",
            "Scientist",
            "Fossil Group",
            "Group Abundance",
            "Group Preservation",
            "Cibicidoides spp. A",
            "Elphidium excavatum Form A",
            "Elphidium excavatum (Terquem Terquem) forma",
            "Comment",
        ]

        assert list(df.columns) == expected_columns

    def test_returns_dataframe_of_right_size(self):
        path = "./tests/data/space_delim.txt"
        df = convert_space_delim_file(path)

        assert df.shape == (3, 21)

    def test_returns_dataframe_with_right_data(self):
        path = "./tests/data/space_delim.txt"
        df = convert_space_delim_file(path)

        assert df["Age From (oldest)"].to_list() == ["", "", ""]

        assert df["Age To (youngest)"].to_list() == [
            "",
            "Pleistocene",
            "Pleistocene",
        ]

        assert df["Zone From (bottom)"].to_list() == [
            "",
            "",
            "",
        ]

        assert df["Zone To (top)"].to_list() == [
            "",
            "",
            "",
        ]

        assert df["Leg"].to_list() == [
            "100",
            "100",
            "100",
        ]

        assert df["Site"].to_list() == [
            "2000",
            "2000",
            "2000",
        ]

        assert df["H"].to_list() == [
            "B",
            "B",
            "B",
        ]

        assert df["Cor"].to_list() == [
            "2",
            "3",
            "4",
        ]

        assert df["T"].to_list() == [
            "X",
            "X",
            "X",
        ]

        assert df["Sc"].to_list() == [
            "CC",
            "CC",
            "CC",
        ]

        assert df["Top(cm)"].to_list() == [
            "0.00",
            "10.00",
            "0.00",
        ]

        assert df["Depth (mbsf)"].to_list() == [
            "41.8500",
            "49.7400",
            "53.4600",
        ]

        assert df["Scientist"].to_list() == [
            "Doe",
            "Doe",
            "Doe",
        ]

        assert df["Fossil Group"].to_list() == [
            "Benthic Foraminifers",
            "Benthic Foraminifers",
            "Benthic Foraminifers",
        ]

        assert df["Group Abundance"].to_list() == [
            "A",
            "F",
            "C",
        ]

        assert df["Group Preservation"].to_list() == [
            "",
            "",
            "VG",
        ]

        assert df["Cibicidoides spp. A"].to_list() == [
            "C",
            "",
            "",
        ]

        assert df["Elphidium excavatum Form A"].to_list() == [
            "",
            "",
            "C",
        ]

        assert df["Elphidium excavatum (Terquem Terquem) forma"].to_list() == [
            "A",
            "A",
            "A",
        ]

        assert df["Comment"].to_list() == [
            "Labore aaa sint labore ex irure commodo.",
            "Labore bbb sint labore ex irure commodo.",
            "Labore ccc sint labore ex irure commodo.",
        ]
