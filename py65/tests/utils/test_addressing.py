import pytest

from py65.utils.addressing import AddressParser


def test_maxwidth_can_be_set_in_constructor():
    parser = AddressParser(maxwidth=24)
    assert 24 == parser.maxwidth
    assert 0xFFFFFF == parser._maxaddr


def test_maxwidth_defaults_to_16_bits():
    parser = AddressParser()
    assert 16 == parser.maxwidth
    assert 0xFFFF == parser._maxaddr


def test_maxwidth_setter():
    parser = AddressParser()
    parser.maxwidth = 24
    assert 24 == parser.maxwidth
    assert 0xFFFFFF == parser._maxaddr


# number


def test_number_hex_literal():
    parser = AddressParser()
    assert 49152 == parser.number("$c000")


def test_number_dec_literal():
    parser = AddressParser()
    assert 49152 == parser.number("+49152")


def test_number_bin_literal():
    parser = AddressParser()
    assert 129 == parser.number("%10000001")


def test_number_default_radix():
    parser = AddressParser()
    parser.radix = 10
    assert 10 == parser.number("10")
    parser.radix = 16
    assert 16 == parser.number("10")


def test_number_label():
    parser = AddressParser()
    parser.labels = {"foo": 0xC000}
    assert 0xC000 == parser.number("foo")


def test_number_bad_label():
    parser = AddressParser()
    try:
        parser.number("bad_label")
        assert False, "Expected a KeyError!"
    except KeyError as exc:
        assert "Label not found: bad_label" == exc.args[0]


def test_number_label_hex_offset():
    parser = AddressParser()
    parser.labels = {"foo": 0xC000}
    assert 0xC003 == parser.number("foo+$3")
    assert 0xBFFD == parser.number("foo-$3")
    assert 0xC003 == parser.number("foo + $3")
    assert 0xBFFD == parser.number("foo - $3")


def test_number_label_dec_offset():
    parser = AddressParser()
    parser.labels = {"foo": 0xC000}
    assert 0xC003 == parser.number("foo++3")
    assert 0xBFFD == parser.number("foo-+3")
    assert 0xC003 == parser.number("foo + +3")
    assert 0xBFFD == parser.number("foo - +3")


def test_number_label_bin_offset():
    parser = AddressParser()
    parser.labels = {"foo": 0xC000}
    assert 0xC003 == parser.number("foo+%00000011")
    assert 0xBFFD == parser.number("foo-%00000011")
    assert 0xC003 == parser.number("foo + %00000011")
    assert 0xBFFD == parser.number("foo - %00000011")


def test_number_label_offset_default_radix():
    parser = AddressParser()
    parser.labels = {"foo": 0xC000}
    parser.radix = 16
    assert 0xC010 == parser.number("foo+10")
    assert 0xBFF0 == parser.number("foo-10")
    assert 0xC010 == parser.number("foo + 10")
    assert 0xBFF0 == parser.number("foo - 10")
    parser.radix = 10
    assert 0xC00A == parser.number("foo+10")
    assert 0xBFF6 == parser.number("foo-10")
    assert 0xC00A == parser.number("foo + 10")
    assert 0xBFF6 == parser.number("foo - 10")


def test_number_bad_label_with_offset():
    parser = AddressParser()
    try:
        parser.number("bad_label+3")
        assert False, "Expected a KeyError!"
    except KeyError as exc:
        assert "Label not found: bad_label" == exc.args[0]


def test_number_bad_label_syntax():
    parser = AddressParser()
    parser.labels = {"foo": 0xFFFF}
    try:
        parser.number("#$foo")
        assert False, "Expected a KeyError!"
    except KeyError as exc:
        assert "Label not found: #$foo" == exc.args[0]


def test_number_constrains_address_at_zero_or_above():
    parser = AddressParser()
    with pytest.raises(OverflowError):
        parser.number("-1")


def test_number_constrains_address_at_maxwidth_16():
    parser = AddressParser()
    parser.labels = {"foo": 0xFFFF}
    with pytest.raises(OverflowError):
        parser.number("foo+5")


def test_number_constrains_address_at_maxwidth_24():
    parser = AddressParser()
    parser.maxwidth = 24
    parser.labels = {"foo": 0xFFFFFF}
    with pytest.raises(OverflowError):
        parser.number("foo+5")


# address_for


def test_address_for_returns_address():
    parser = AddressParser(labels={"chrout": 0xFFD2})
    assert 0xFFD2 == parser.address_for("chrout")


def test_address_for_returns_none_by_default():
    parser = AddressParser(labels={})
    assert None == parser.address_for("chrout")


def test_adderss_for_returns_alternate_default():
    parser = AddressParser(labels={})
    assert "foo" == parser.address_for("chrout", "foo")


# label_for


def test_label_for_returns_label():
    parser = AddressParser(labels={"chrout": 0xFFD2})
    assert "chrout" == parser.label_for(0xFFD2)


def test_label_for_returns_none_by_default():
    parser = AddressParser(labels={})
    assert None == parser.label_for(0xFFD2)


def test_label_for_returns_alternate_default():
    parser = AddressParser(labels={})
    assert "foo" == parser.label_for(0xFFD2, "foo")


# range


def test_range_one_number():
    parser = AddressParser(labels={})
    assert (0xFFD2, 0xFFD2) == parser.range("ffd2")


def test_range_one_label():
    parser = AddressParser(labels={"chrout": 0xFFD2})
    assert (0xFFD2, 0xFFD2) == parser.range("chrout")


def test_range_two_numbers():
    parser = AddressParser(labels={})
    assert (0xFFD2, 0xFFD4) == parser.range("ffd2:ffd4")


def test_range_mixed():
    parser = AddressParser(labels={"chrout": 0xFFD2})
    assert (0xFFD2, 0xFFD4) == parser.range("chrout:ffd4")


def test_range_start_exceeds_end():
    parser = AddressParser(labels={})
    assert (0xFFD2, 0xFFD4) == parser.range("ffd4:ffd2")
