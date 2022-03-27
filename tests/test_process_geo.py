import pytest

from scripts.process_geo import ddm2dec


class Testddm2dec:
    def test_returns_decimal_degree_fof_degree_decimal_minute(self):
        string = "25 51.498 N"
        assert ddm2dec(string) == 25.8583

    def test_works_with_decimal(self):
        string = "25 .498 N"
        assert ddm2dec(string) == 25.0083

    def test_works_with_integer(self):
        string = "25 20 N"
        assert ddm2dec(string) == 25.333333333333332

    def test_works_with_direction_first(self):
        string = "N 25 51.498"
        assert ddm2dec(string) == 25.8583

    @pytest.mark.parametrize(
        "string,result", [("25° 51.498'N", 25.8583), ("25°51.498'N", 25.8583)]
    )
    def test_works_with_degree_minute_notation(self, string, result):
        assert ddm2dec(string) == result

    @pytest.mark.parametrize(
        "string,result",
        [
            ("25 51.498 e", 25.8583),
            ("25 51.498 w", -25.8583),
            ("25 51.498 S", -25.8583),
            ("25 51.498 n", 25.8583),
        ],
    )
    def test_adds_correct_sign_for_direction(self, string, result):
        assert ddm2dec(string) == result
