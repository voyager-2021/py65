import pytest

from py65.assembler import Assembler
from py65.devices.mpu65c02 import MPU as MPU65C02
from py65.devices.mpu6502 import MPU
from py65.utils.addressing import AddressParser


def test_ctor_uses_provided_mpu_and_address_parser():
    mpu = MPU()
    address_parser = AddressParser()
    asm = Assembler(mpu, address_parser)
    assert asm._mpu is mpu
    assert asm._address_parser is address_parser


def test_ctor_optionally_creates_address_parser():
    mpu = MPU()
    asm = Assembler(mpu)
    assert asm._address_parser is not None


def test_assemble_bad_syntax_raises_syntaxerror():
    with pytest.raises(SyntaxError):
        assemble("foo")
    with pytest.raises(SyntaxError):
        assemble("lda #")
    with pytest.raises(SyntaxError):
        assemble('lda #"')


def test_assemble_bad_label_raises_keyerror():
    with pytest.raises(KeyError):
        assemble("lda foo")


def test_assemble_tolerates_extra_whitespace():
    assemble("   lda   #$00   ")  # should not raise


def test_assemble_bad_number_raises_overflowerror():
    with pytest.raises(OverflowError):
        assemble("lda #$fff")


def test_assemble_1_byte_at_top_of_mem_should_not_overflow():
    assemble("nop", pc=0xFFFF)  # should not raise


def test_assemble_3_bytes_at_top_of_mem_should_not_overflow():
    assemble("jmp $1234", pc=0xFFFD)  # should not raise


def test_assemble_should_overflow_if_over_top_of_mem():
    # jmp $1234 requires 3 bytes but there's only 2 at $FFFE-FFFF
    with pytest.raises(OverflowError):
        assemble("jmp $1234", pc=0xFFFE)


def test_assembles_00():
    assert [0x00] == assemble("BRK")


def test_assembles_01():
    assert [0x01, 0x44] == assemble("ORA ($44,X)")


def dont_test_assembles_02():
    pass


def dont_test_assembles_03():
    pass


def dont_test_assembles_04():
    pass


def test_assembles_04_65c02():
    mpu = MPU65C02()
    assert [0x04, 0x42] == assemble("TSB $42", 0x0000, mpu)


def test_assembles_05():
    assert [0x05, 0x44] == assemble("ORA $44")


def test_assembles_06():
    assert [0x06, 0x44] == assemble("ASL $44")


def test_assembles_07():
    with pytest.raises(SyntaxError):
        assemble("RMB0 $42")


def test_assembles_07_65c02():
    mpu = MPU65C02()
    assert [0x07, 0x42] == assemble("RMB0 $42", 0x0000, mpu)


def test_assembles_08():
    assert [0x08] == assemble("PHP")


def test_assembles_09():
    assert [0x09, 0x44] == assemble("ORA #$44")


def test_assembles_0a():
    assert [0x0A] == assemble("ASL A")


def dont_test_assembles_0b():
    pass


def dont_test_assembles_0c():
    pass


def test_assembles_0c_65c02():
    mpu = MPU65C02()
    assert [0x0C, 0x34, 0x12] == assemble("TSB $1234", 0x0000, mpu)


def test_assembles_0d():
    assert [0x0D, 0x00, 0x44] == assemble("ORA $4400")


def test_assembles_0e():
    assert [0x0E, 0x00, 0x44] == assemble("ASL $4400")


def dont_test_assembles_0f():
    pass


def test_assembles_10():
    assert [0x10, 0x44] == assemble("BPL $0046")


def test_assembles_11():
    assert [0x11, 0x44] == assemble("ORA ($44),Y")


def dont_test_assembles_12():
    pass


def test_assembles_12_65c02():
    mpu = MPU65C02()
    assert [0x12, 0x44] == assemble("ORA ($44)", 0x0000, mpu)


def dont_test_assembles_13():
    pass


def dont_test_assembles_14():
    pass


def test_assembles_14_65c02():
    mpu = MPU65C02()
    assert [0x14, 0x42] == assemble("TRB $42", 0x0000, mpu)


def test_assembles_15():
    assert [0x15, 0x44] == assemble("ORA $44,X")


def test_assembles_16():
    assert [0x16, 0x44] == assemble("ASL $44,X")


def dont_test_assembles_17():
    pass


def test_assembles_17_65c02():
    mpu = MPU65C02()
    assert [0x17, 0x42] == assemble("RMB1 $42", 0x0000, mpu)


def test_assembles_18():
    assert [0x18] == assemble("CLC")


def test_assembles_19():
    assert [0x19, 0x00, 0x44] == assemble("ORA $4400,Y")


def dont_test_assembles_1a():
    pass


def test_assembles_1a_65c02():
    mpu = MPU65C02()
    assert [0x1A] == assemble("INC", 0x0000, mpu)


def dont_test_assembles_1b():
    pass


def test_assembles_1c():
    pass


def test_assembles_1c_65c02():
    mpu = MPU65C02()
    assert [0x1C, 0x34, 0x12] == assemble("TRB $1234", 0x0000, mpu)


def test_assembles_1d():
    assert [0x1D, 0x00, 0x44] == assemble("ORA $4400,X")


def test_assembles_1e():
    assert [0x1E, 0x00, 0x44] == assemble("ASL $4400,X")


def dont_test_assembles_1f():
    pass


def test_assembles_20():
    assert [0x20, 0x97, 0x55] == assemble("JSR $5597")


def test_assembles_21():
    assert [0x21, 0x44] == assemble("AND ($44,X)")


def dont_test_assembles_22():
    pass


def dont_test_assembles_23():
    pass


def test_assembles_24():
    assert [0x24, 0x44] == assemble("BIT $44")


def test_assembles_25():
    assert [0x25, 0x44] == assemble("AND $44")


def test_assembles_26():
    assert [0x26, 0x44] == assemble("ROL $44")


def dont_test_assembles_27():
    pass


def test_assembles_27_65c02():
    mpu = MPU65C02()
    assert [0x27, 0x42] == assemble("RMB2 $42", 0x0000, mpu)


def test_assembles_28():
    assert [0x28] == assemble("PLP")


def test_assembles_29():
    assert [0x29, 0x44] == assemble("AND #$44")


def test_assembles_2a():
    assert [0x2A] == assemble("ROL A")


def dont_test_assembles_2b():
    pass


def test_assembles_2c():
    assert [0x2C, 0x00, 0x44] == assemble("BIT $4400")


def test_assembles_2d():
    assert [0x2D, 0x00, 0x44] == assemble("AND $4400")


def test_assembles_2e():
    assert [0x2E, 0x00, 0x44] == assemble("ROL $4400")


def dont_test_assembles_2f():
    pass


def test_assembles_30():
    assert [0x30, 0x44] == assemble("BMI $0046")


def test_assembles_31():
    assert [0x31, 0x44] == assemble("AND ($44),Y")


def dont_test_assembles_32():
    pass


def test_assembles_32_65c02():
    mpu = MPU65C02()
    assert [0x32, 0x44] == assemble("AND ($44)", 0x0000, mpu)


def dont_test_assembles_33():
    pass


def dont_test_assembles_34():
    pass


def test_assembles_34_65c02():
    mpu = MPU65C02()
    assert [0x34, 0x44] == assemble("BIT $44,X", 0x0000, mpu)


def test_assembles_35():
    assert [0x35, 0x44] == assemble("AND $44,X")


def test_assembles_36():
    assert [0x36, 0x44] == assemble("ROL $44,X")


def dont_test_assembles_37():
    pass


def test_assembles_37_65c02():
    mpu = MPU65C02()
    assert [0x37, 0x42] == assemble("RMB3 $42", 0x0000, mpu)


def test_assembles_38():
    assert [0x38] == assemble("SEC")


def test_assembles_39():
    assert [0x39, 0x00, 0x44] == assemble("AND $4400,Y")


def dont_test_assembles_3a():
    pass


def test_assembles_3a_65c02():
    mpu = MPU65C02()
    assert [0x3A] == assemble("DEC", 0x0000, mpu)


def dont_test_assembles_3b():
    pass


def dont_test_assembles_3c():
    pass


def test_assembles_3c_65c02():
    mpu = MPU65C02()
    assert [0x3C, 0x34, 0x12] == assemble("BIT $1234,X", 0x0000, mpu)


def test_assembles_3d():
    assert [0x3D, 0x00, 0x44] == assemble("AND $4400,X")


def test_assembles_3e():
    assert [0x3E, 0x00, 0x44] == assemble("ROL $4400,X")


def dont_test_assembles_3f():
    pass


def test_assembles_40():
    assert [0x40] == assemble("RTI")


def test_assembles_41():
    assert [0x41, 0x44] == assemble("EOR ($44,X)")


def dont_test_assembles_42():
    pass


def dont_test_assembles_43():
    pass


def dont_test_assembles_44():
    pass


def test_assembles_45():
    assert [0x45, 0x44] == assemble("EOR $44")


def test_assembles_46():
    assert [0x46, 0x44] == assemble("LSR $44")


def dont_test_assembles_47():
    pass


def test_assembles_47_65c02():
    mpu = MPU65C02()
    assert [0x47, 0x42] == assemble("RMB4 $42", 0x0000, mpu)


def test_assembles_48():
    assert [0x48] == assemble("PHA")


def test_assembles_49():
    assert [0x49, 0x44] == assemble("EOR #$44")


def test_assembles_4a():
    assert [0x4A] == assemble("LSR A")


def dont_test_assembles_4b():
    pass


def test_assembles_4c():
    assert [0x4C, 0x97, 0x55] == assemble("JMP $5597")


def test_assembles_4d():
    assert [0x4D, 0x00, 0x44] == assemble("EOR $4400")


def test_assembles_4e():
    assert [0x4E, 0x00, 0x44] == assemble("LSR $4400")


def dont_test_assembles_4f():
    pass


def test_assembles_50():
    assert [0x50, 0x44] == assemble("BVC $0046")


def test_assembles_51():
    assert [0x51, 0x44] == assemble("EOR ($44),Y")


def dont_test_assembles_52():
    pass


def test_assembles_52_65c02():
    mpu = MPU65C02()
    assert [0x52, 0x44] == assemble("EOR ($44)", 0x0000, mpu)


def dont_test_assembles_53():
    pass


def dont_test_assembles_54():
    pass


def test_assembles_55():
    assert [0x55, 0x44] == assemble("EOR $44,X")


def test_assembles_56():
    assert [0x56, 0x44] == assemble("LSR $44,X")


def dont_test_assembles_57():
    pass


def test_assembles_57_65c02():
    mpu = MPU65C02()
    assert [0x57, 0x42] == assemble("RMB5 $42", 0x0000, mpu)


def test_assembles_58():
    assert [0x58] == assemble("CLI")


def test_assembles_59():
    assert [0x59, 0x00, 0x44] == assemble("EOR $4400,Y")


def dont_test_assembles_5a():
    pass


def test_assembles_5a_65c02():
    mpu = MPU65C02()
    assert [0x5A] == assemble("PHY", 0x0000, mpu)


def dont_test_assembles_5b():
    pass


def dont_test_assembles_5c():
    pass


def test_assembles_5d():
    assert [0x5D, 0x00, 0x44] == assemble("EOR $4400,X")


def test_assembles_5e():
    assert [0x5E, 0x00, 0x44] == assemble("LSR $4400,X")


def dont_test_assembles_5f():
    pass


def test_assembles_60():
    assert [0x60] == assemble("RTS")


def test_assembles_61():
    assert [0x61, 0x44] == assemble("ADC ($44,X)")


def dont_test_assembles_62():
    pass


def dont_test_assembles_63():
    pass


def dont_test_assembles_64():
    pass


def test_assembles_64_65c02():
    mpu = MPU65C02()
    assert [0x64, 0x12] == assemble("STZ $12", 0x0000, mpu)


def test_assembles_65():
    assert [0x65, 0x44] == assemble("ADC $44")


def test_assembles_66():
    assert [0x66, 0x44] == assemble("ROR $44")


def dont_test_assembles_67():
    pass


def test_assembles_67_65c02():
    mpu = MPU65C02()
    assert [0x67, 0x42] == assemble("RMB6 $42", 0x0000, mpu)


def test_assembles_68():
    assert [0x68] == assemble("PLA")


def test_assembles_69():
    assert [0x69, 0x44] == assemble("ADC #$44")


def test_assembles_6a():
    assert [0x6A] == assemble("ROR A")


def dont_test_assembles_6b():
    pass


def test_assembles_6c():
    assert [0x6C, 0x97, 0x55] == assemble("JMP ($5597)")


def test_assembles_6d():
    assert [0x6D, 0x00, 0x44] == assemble("ADC $4400")


def test_assembles_6e():
    assert [0x6E, 0x00, 0x44] == assemble("ROR $4400")


def dont_test_assembles_6f():
    pass


def test_assembles_70():
    assert [0x70, 0x44] == assemble("BVS $0046")


def test_assembles_71():
    assert [0x71, 0x44] == assemble("ADC ($44),Y")


def dont_test_assembles_72():
    pass


def test_assembles_72_65c02():
    mpu = MPU65C02()
    assert [0x72, 0x44] == assemble("ADC ($44)", 0x0000, mpu)


def dont_test_assembles_73():
    pass


def dont_test_assembles_74():
    pass


def test_assembles_74_65c02():
    mpu = MPU65C02()
    assert [0x74, 0x44] == assemble("STZ $44,X", 0x0000, mpu)


def test_assembles_75():
    assert [0x75, 0x44] == assemble("ADC $44,X")


def test_assembles_76():
    assert [0x76, 0x44] == assemble("ROR $44,X")


def test_assembles_77():
    pass


def test_assembles_77_65c02():
    mpu = MPU65C02()
    assert [0x77, 0x42] == assemble("RMB7 $42", 0x0000, mpu)


def test_assembles_78():
    assert [0x78] == assemble("SEI")


def test_assembles_79():
    assert [0x79, 0x00, 0x44] == assemble("ADC $4400,Y")


def dont_test_assembles_7a():
    pass


def test_assembles_7a_65c02():
    mpu = MPU65C02()
    assert [0x7A] == assemble("PLY", 0x0000, mpu)


def dont_test_assembles_7b():
    pass


def test_assembles_7c_6502():
    with pytest.raises(SyntaxError):
        assemble("JMP ($1234,X)")


def test_assembles_7c_65c02():
    mpu = MPU65C02()
    assert [0x7C, 0x34, 0x12] == assemble("JMP ($1234,X)", 0x0000, mpu)


def test_assembles_7d():
    assert [0x7D, 0x00, 0x44] == assemble("ADC $4400,X")


def test_assembles_7e():
    assert [0x7E, 0x00, 0x44] == assemble("ROR $4400,X")


def dont_test_assembles_7f():
    pass


def dont_test_assembles_80():
    pass


def test_assembles_80_65c02():
    mpu = MPU65C02()
    assert [0x80, 0x44] == assemble("BRA $0046", 0x0000, mpu)


def test_assembles_81():
    assert [0x81, 0x44] == assemble("STA ($44,X)")


def dont_test_assembles_82():
    pass


def dont_test_assembles_83():
    pass


def test_assembles_84():
    assert [0x84, 0x44] == assemble("STY $44")


def test_assembles_85():
    assert [0x85, 0x44] == assemble("STA $44")


def test_assembles_86():
    assert [0x86, 0x44] == assemble("STX $44")


def dont_test_assembles_87():
    pass


def test_assembles_87_65c02():
    mpu = MPU65C02()
    assert [0x87, 0x42] == assemble("SMB0 $42", 0x0000, mpu)


def test_assembles_88():
    assert [0x88] == assemble("DEY")


def dont_test_assembles_89():
    pass


def test_assembles_89_65c02():
    mpu = MPU65C02()
    assert [0x89, 0x42] == assemble("BIT #$42", 0x0000, mpu)


def test_assembles_8a():
    assert [0x8A] == assemble("TXA")


def dont_test_assembles_8b():
    pass


def test_assembles_8c():
    assert [0x8C, 0x00, 0x44] == assemble("STY $4400")


def test_assembles_8d():
    assert [0x8D, 0x00, 0x44] == assemble("STA $4400")


def test_assembles_8e():
    assert [0x8E, 0x00, 0x44] == assemble("STX $4400")


def dont_test_assembles_8f():
    pass


def test_assembles_90():
    assert [0x90, 0x44] == assemble("BCC $0046")


def test_assembles_91():
    assert [0x91, 0x44] == assemble("STA ($44),Y")


def dont_test_assembles_92():
    pass


def test_assembles_92_65c02():
    mpu = MPU65C02()
    assert [0x92, 0x44] == assemble("STA ($44)", 0x0000, mpu)


def dont_test_assembles_93():
    pass


def test_assembles_94():
    assert [0x94, 0x44] == assemble("STY $44,X")


def test_assembles_95():
    assert [0x95, 0x44] == assemble("STA $44,X")


def test_assembles_96():
    assert [0x96, 0x44] == assemble("STX $44,Y")


def dont_test_assembles_97():
    pass


def test_assembles_97_65c02():
    mpu = MPU65C02()
    assert [0x97, 0x42] == assemble("SMB1 $42", 0x0000, mpu)


def test_assembles_98():
    assert [0x98] == assemble("TYA")


def test_assembles_99():
    assert [0x99, 0x00, 0x44] == assemble("STA $4400,Y")


def test_assembles_9a():
    assert [0x9A] == assemble("TXS")


def dont_test_assembles_9b():
    pass


def dont_test_assembles_9c():
    pass


def test_assembles_9c_65c02():
    mpu = MPU65C02()
    assert [0x9C, 0x34, 0x12] == assemble("STZ $1234", 0x0000, mpu)


def test_assembles_9d():
    assert [0x9D, 0x00, 0x44] == assemble("STA $4400,X")


def dont_test_assembles_9e():
    pass


def test_assembles_9e_65c02():
    mpu = MPU65C02()
    assert [0x9E, 0x34, 0x12] == assemble("STZ $1234,X", 0x0000, mpu)


def dont_test_assembles_9f():
    pass


def test_assembles_a0():
    assert [0xA0, 0x44] == assemble("LDY #$44")


def test_assembles_a1():
    assert [0xA1, 0x44] == assemble("LDA ($44,X)")


def test_assembles_a2():
    assert [0xA2, 0x44] == assemble("LDX #$44")


def dont_test_assembles_a3():
    pass


def test_assembles_a4():
    assert [0xA4, 0x44] == assemble("LDY $44")


def test_assembles_a5():
    assert [0xA5, 0x44] == assemble("LDA $44")


def test_assembles_a6():
    assert [0xA6, 0x44] == assemble("LDX $44")


def dont_test_assembles_a7():
    pass


def test_assembles_a7_65c02():
    mpu = MPU65C02()
    assert [0xA7, 0x42] == assemble("SMB2 $42", 0x0000, mpu)


def test_assembles_a8():
    assert [0xA8] == assemble("TAY")


def test_assembles_a9():
    assert [0xA9, 0x44] == assemble("LDA #$44")


def test_assembles_a9_ascii():
    assert [0xA9, 0x48] == assemble("LDA #'H")
    assert [0xA9, 0x49] == assemble('LDA #"I')


def test_assembles_aa():
    assert [0xAA] == assemble("TAX")


def dont_test_assembles_ab():
    pass


def test_assembles_ac():
    assert [0xAC, 0x00, 0x44] == assemble("LDY $4400")


def test_assembles_ad():
    assert [0xAD, 0x00, 0x44] == assemble("LDA $4400")


def test_assembles_ae():
    assert [0xAE, 0x00, 0x44] == assemble("LDX $4400")


def dont_test_assembles_af():
    pass


def test_assembles_b0():
    assert [0xB0, 0x44] == assemble("BCS $0046")


def test_assembles_b1():
    assert [0xB1, 0x44] == assemble("LDA ($44),Y")


def dont_test_assembles_b2():
    pass


def test_assembles_b2_65c02():
    mpu = MPU65C02()
    assert [0xB2, 0x44] == assemble("LDA ($44)", 0x0000, mpu)


def dont_test_assembles_b3():
    pass


def test_assembles_b4():
    assert [0xB4, 0x44] == assemble("LDY $44,X")


def test_assembles_b5():
    assert [0xB5, 0x44] == assemble("LDA $44,X")


def test_assembles_b6():
    assert [0xB6, 0x44] == assemble("LDX $44,Y")


def dont_test_assembles_b7():
    pass


def test_assembles_b7_65c02():
    mpu = MPU65C02()
    assert [0xB7, 0x42] == assemble("SMB3 $42", 0x0000, mpu)


def test_assembles_b8():
    assert [0xB8] == assemble("CLV")


def test_assembles_b9():
    assert [0xB9, 0x00, 0x44] == assemble("LDA $4400,Y")


def test_assembles_ba():
    assert [0xBA] == assemble("TSX")


def dont_test_assembles_bb():
    pass


def test_assembles_bc():
    assert [0xBC, 0x00, 0x44] == assemble("LDY $4400,X")


def test_assembles_bd():
    assert [0xBD, 0x00, 0x44] == assemble("LDA $4400,X")


def test_assembles_be():
    assert [0xBE, 0x00, 0x44] == assemble("LDX $4400,Y")


def dont_test_assembles_bf():
    pass


def test_assembles_c0():
    assert [0xC0, 0x44] == assemble("CPY #$44")


def test_assembles_c1():
    assert [0xC1, 0x44] == assemble("CMP ($44,X)")


def dont_test_assembles_c2():
    pass


def dont_test_assembles_c3():
    pass


def test_assembles_c4():
    assert [0xC4, 0x44] == assemble("CPY $44")


def test_assembles_c5():
    assert [0xC5, 0x44] == assemble("CMP $44")


def test_assembles_c6():
    assert [0xC6, 0x44] == assemble("DEC $44")


def dont_test_assembles_c7():
    pass


def test_assembles_c7_65c02():
    mpu = MPU65C02()
    assert [0xC7, 0x42] == assemble("SMB4 $42", 0x0000, mpu)


def test_assembles_c8():
    assert [0xC8] == assemble("INY")


def test_assembles_c9():
    assert [0xC9, 0x44] == assemble("CMP #$44")


def test_assembles_ca():
    assert [0xCA] == assemble("DEX")


def dont_test_assembles_cb():
    pass


def test_assembles_cb_65c02():
    mpu = MPU65C02()
    assert [0xCB] == assemble("WAI", 0x0000, mpu)


def test_assembles_cc():
    assert [0xCC, 0x00, 0x44] == assemble("CPY $4400")


def test_assembles_cd():
    assert [0xCD, 0x00, 0x44] == assemble("CMP $4400")


def test_assembles_ce():
    assert [0xCE, 0x00, 0x44] == assemble("DEC $4400")


def dont_test_assembles_cf():
    pass


def test_assembles_d0():
    assert [0xD0, 0x44] == assemble("BNE $0046")


def test_assembles_d1():
    assert [0xD1, 0x44] == assemble("CMP ($44),Y")


def dont_test_assembles_d2():
    pass


def test_assembles_d2_65c02():
    mpu = MPU65C02()
    assert [0xD2, 0x42] == assemble("CMP ($42)", 0x0000, mpu)


def dont_test_assembles_d3():
    pass


def dont_test_assembles_d4():
    pass


def test_assembles_d5():
    assert [0xD5, 0x44] == assemble("CMP $44,X")


def test_assembles_d6():
    assert [0xD6, 0x44] == assemble("DEC $44,X")


def dont_test_assembles_d7():
    pass


def test_assembles_d7_65c02():
    mpu = MPU65C02()
    assert [0xD7, 0x42] == assemble("SMB5 $42", 0x0000, mpu)


def test_assembles_d8():
    assert [0xD8] == assemble("CLD")


def dont_test_assembles_da():
    pass


def test_assembles_da_65c02():
    mpu = MPU65C02()
    assert [0xDA] == assemble("PHX", 0x0000, mpu)


def dont_test_assembles_db():
    pass


def dont_test_assembles_dc():
    pass


def test_assembles_dd():
    assert [0xDD, 0x00, 0x44] == assemble("CMP $4400,X")


def test_assembles_de():
    assert [0xDE, 0x00, 0x44] == assemble("DEC $4400,X")


def dont_test_assembles_df():
    pass


def test_assembles_e0():
    assert [0xE0, 0x44] == assemble("CPX #$44")


def test_assembles_e1():
    assert [0xE1, 0x44] == assemble("SBC ($44,X)")


def dont_test_assembles_e2():
    pass


def dont_test_assembles_e3():
    pass


def test_assembles_e4():
    assert [0xE4, 0x44] == assemble("CPX $44")


def test_assembles_e5():
    assert [0xE5, 0x44] == assemble("SBC $44")


def test_assembles_e6():
    assert [0xE6, 0x44] == assemble("INC $44")


def dont_test_assembles_e7():
    pass


def test_assembles_e7_65c02():
    mpu = MPU65C02()
    assert [0xE7, 0x42] == assemble("SMB6 $42", 0x0000, mpu)


def test_assembles_e8():
    assert [0xE8] == assemble("INX")


def test_assembles_e9():
    assert [0xE9, 0x44] == assemble("SBC #$44")


def test_assembles_ea():
    assert [0xEA] == assemble("NOP")


def dont_test_assembles_eb():
    pass


def test_assembles_ec():
    assert [0xEC, 0x00, 0x44] == assemble("CPX $4400")


def test_assembles_ed():
    assert [0xED, 0x00, 0x44] == assemble("SBC $4400")


def test_assembles_ee():
    assert [0xEE, 0x00, 0x44] == assemble("INC $4400")


def dont_test_assembles_ef():
    pass


def test_assembles_f0_forward():
    assert [0xF0, 0x44] == assemble("BEQ $0046")


def test_assembles_f0_backward():
    assert [0xF0, 0xFC] == assemble("BEQ $BFFE", pc=0xC000)


def test_assembles_f1():
    assert [0xF1, 0x44] == assemble("SBC ($44),Y")


def dont_test_assembles_f2():
    pass


def test_assembles_f2_65c02():
    mpu = MPU65C02()
    assert [0xF2, 0x42] == assemble("SBC ($42)", 0x0000, mpu)


def dont_test_assembles_f3():
    pass


def dont_test_assembles_f4():
    pass


def test_assembles_f5():
    assert [0xF5, 0x44] == assemble("SBC $44,X")


def test_assembles_f6():
    assert [0xF6, 0x44] == assemble("INC $44,X")


def dont_test_assembles_f7():
    pass


def test_assembles_f7_65c02():
    mpu = MPU65C02()
    assert [0xF7, 0x42] == assemble("SMB7 $42", 0x0000, mpu)


def test_assembles_f8():
    assert [0xF8] == assemble("SED")


def test_assembles_f9():
    assert [0xF9, 0x00, 0x44] == assemble("SBC $4400,Y")


def dont_test_assembles_fa():
    pass


def test_assembles_fa_65c02():
    mpu = MPU65C02()
    assert [0xFA] == assemble("PLX", 0x0000, mpu)


def dont_test_assembles_fb():
    pass


def dont_test_assembles_fc():
    pass


def test_assembles_fd():
    assert [0xFD, 0x00, 0x44] == assemble("SBC $4400,X")


def test_assembles_fe():
    assert [0xFE, 0x00, 0x44] == assemble("INC $4400,X")


def dont_test_assembles_ff():
    pass


# Test Helpers


def assemble(statement, pc=0000, mpu=None):
    if mpu is None:
        mpu = MPU()
    address_parser = AddressParser()
    assembler = Assembler(mpu, address_parser)
    return assembler.assemble(statement, pc)
