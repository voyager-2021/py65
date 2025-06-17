import pytest

from py65.utils.conversions import convert_to_bcd, convert_to_bin, itoa


def test_itoa_decimal_output():
    assert "10" == itoa(10, base=10)
    assert "-10" == itoa(-10, base=10)


def test_itoa_hex_output():
    assert "a" == itoa(10, base=16)
    assert "-a" == itoa(-10, base=16)


def test_itoa_bin_output():
    assert "1010" == itoa(10, base=2)
    assert "-1010" == itoa(-10, base=2)


def test_itoa_unsupported_base():
    with pytest.raises(ValueError):
        itoa(0, base=17)


def test_convert_to_bin():
    assert 0 == convert_to_bin(0)
    assert 99 == convert_to_bin(0x99)


def test_convert_to_bcd():
    assert 0 == convert_to_bcd(0)
    assert 0x99 == convert_to_bcd(99)
