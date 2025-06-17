import sys
import unittest

from py65.devices.mpu65c02 import MPU as MPU65C02
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
from py65.utils.addressing import AddressParser


def _dont_test_disassemble_wraps_after_top_of_mem():
    """
    TODO: This test fails with IndexError.  We should fix this
    so that it does not attempt to index memory out of range.
    It does not affect most Py65 users because py65mon uses
    ObservableMemory, which does not raise IndexError.
    """
    mpu = MPU()
    mpu.memory[0xFFFF] = 0x20  # JSR
    mpu.memory[0x0000] = 0xD2  #
    mpu.memory[0x0001] = 0xFF  # $FFD2

    dis = Disassembler(mpu)
    length, disasm = dis.instruction_at(0xFFFF)
    assert 3 == length
    assert "JSR $ffd2" == disasm


def test_disassembles_00():
    length, disasm = disassemble([0x00])
    assert 1 == length
    assert "BRK" == disasm


def test_disassembles_01():
    length, disasm = disassemble([0x01, 0x44])
    assert 2 == length
    assert "ORA ($44,X)" == disasm


def test_disassembles_02():
    length, disasm = disassemble([0x02])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_03():
    length, disasm = disassemble([0x03])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_04():
    length, disasm = disassemble([0x04])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_05():
    length, disasm = disassemble([0x05, 0x44])
    assert 2 == length
    assert "ORA $44" == disasm


def test_disassembles_06():
    length, disasm = disassemble([0x06, 0x44])
    assert 2 == length
    assert "ASL $44" == disasm


def test_disassembles_07_6502():
    length, disasm = disassemble([0x07])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_07_65c02():
    mpu = MPU65C02()
    length, disasm = disassemble([0x07, 0x42], 0x0000, mpu)
    assert 2 == length
    assert "RMB0 $42" == disasm


def test_disassembles_08():
    length, disasm = disassemble([0x08])
    assert 1 == length
    assert "PHP" == disasm


def test_disassembles_09():
    length, disasm = disassemble([0x09, 0x44])
    assert 2 == length
    assert "ORA #$44" == disasm


def test_disassembles_0a():
    length, disasm = disassemble([0x0A])
    assert 1 == length
    assert "ASL A" == disasm


def test_disassembles_0b():
    length, disasm = disassemble([0x0B])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_0c():
    length, disasm = disassemble([0x0C])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_0d():
    length, disasm = disassemble([0x0D, 0x00, 0x44])
    assert 3 == length
    assert "ORA $4400" == disasm


def test_disassembles_0e():
    length, disasm = disassemble([0x0E, 0x00, 0x44])
    assert 3 == length
    assert "ASL $4400" == disasm


def test_disassembles_0f():
    length, disasm = disassemble([0x0F])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_10():
    length, disasm = disassemble([0x10, 0x44])
    assert 2 == length
    assert "BPL $0046" == disasm


def test_disassembles_11():
    length, disasm = disassemble([0x11, 0x44])
    assert 2 == length
    assert "ORA ($44),Y" == disasm


def test_disassembles_12():
    length, disasm = disassemble([0x12])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_13():
    length, disasm = disassemble([0x13])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_14():
    length, disasm = disassemble([0x14])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_15():
    length, disasm = disassemble([0x15, 0x44])
    assert 2 == length
    assert "ORA $44,X" == disasm


def test_disassembles_16():
    length, disasm = disassemble([0x16, 0x44])
    assert 2 == length
    assert "ASL $44,X" == disasm


def test_disassembles_17():
    length, disasm = disassemble([0x17])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_18():
    length, disasm = disassemble([0x18])
    assert 1 == length
    assert "CLC" == disasm


def test_disassembles_19():
    length, disasm = disassemble([0x19, 0x00, 0x44])
    assert 3 == length
    assert "ORA $4400,Y" == disasm


def test_disassembles_1a():
    length, disasm = disassemble([0x1A])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_1b():
    length, disasm = disassemble([0x1B])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_1c():
    length, disasm = disassemble([0x1C])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_1d():
    length, disasm = disassemble([0x1D, 0x00, 0x44])
    assert 3 == length
    assert "ORA $4400,X" == disasm


def test_disassembles_1e():
    length, disasm = disassemble([0x1E, 0x00, 0x44])
    assert 3 == length
    assert "ASL $4400,X" == disasm


def test_disassembles_1f():
    length, disasm = disassemble([0x1F])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_20():
    length, disasm = disassemble([0x20, 0x97, 0x55])
    assert 3 == length
    assert "JSR $5597" == disasm


def test_disassembles_21():
    length, disasm = disassemble([0x21, 0x44])
    assert 2 == length
    assert "AND ($44,X)" == disasm


def test_disassembles_22():
    length, disasm = disassemble([0x22])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_23():
    length, disasm = disassemble([0x23])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_24():
    length, disasm = disassemble([0x24, 0x44])
    assert 2 == length
    assert "BIT $44" == disasm


def test_disassembles_25():
    length, disasm = disassemble([0x25, 0x44])
    assert 2 == length
    assert "AND $44" == disasm


def test_disassembles_26():
    length, disasm = disassemble([0x26, 0x44])
    assert 2 == length
    assert "ROL $44" == disasm


def test_disassembles_27():
    length, disasm = disassemble([0x27])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_28():
    length, disasm = disassemble([0x28])
    assert 1 == length
    assert "PLP" == disasm


def test_disassembles_29():
    length, disasm = disassemble([0x29, 0x44])
    assert 2 == length
    assert "AND #$44" == disasm


def test_disassembles_2a():
    length, disasm = disassemble([0x2A])
    assert 1 == length
    assert "ROL A" == disasm


def test_disassembles_2b():
    length, disasm = disassemble([0x2B])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_2c():
    length, disasm = disassemble([0x2C, 0x00, 0x44])
    assert 3 == length
    assert "BIT $4400" == disasm


def test_disassembles_2d():
    length, disasm = disassemble([0x2D, 0x00, 0x44])
    assert 3 == length
    assert "AND $4400" == disasm


def test_disassembles_2e():
    length, disasm = disassemble([0x2E, 0x00, 0x44])
    assert 3 == length
    assert "ROL $4400" == disasm


def test_disassembles_2f():
    length, disasm = disassemble([0x2F])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_30():
    length, disasm = disassemble([0x30, 0x44])
    assert 2 == length
    assert "BMI $0046" == disasm


def test_disassembles_31():
    length, disasm = disassemble([0x31, 0x44])
    assert 2 == length
    assert "AND ($44),Y" == disasm


def test_disassembles_32():
    length, disasm = disassemble([0x32])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_33():
    length, disasm = disassemble([0x33])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_34():
    length, disasm = disassemble([0x34])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_35():
    length, disasm = disassemble([0x35, 0x44])
    assert 2 == length
    assert "AND $44,X" == disasm


def test_disassembles_36():
    length, disasm = disassemble([0x36, 0x44])
    assert 2 == length
    assert "ROL $44,X" == disasm


def test_disassembles_37():
    length, disasm = disassemble([0x37])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_38():
    length, disasm = disassemble([0x38])
    assert 1 == length
    assert "SEC" == disasm


def test_disassembles_39():
    length, disasm = disassemble([0x39, 0x00, 0x44])
    assert 3 == length
    assert "AND $4400,Y" == disasm


def test_disassembles_3a():
    length, disasm = disassemble([0x3A])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_3b():
    length, disasm = disassemble([0x3B])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_3c():
    length, disasm = disassemble([0x3C])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_3d():
    length, disasm = disassemble([0x3D, 0x00, 0x44])
    assert 3 == length
    assert "AND $4400,X" == disasm


def test_disassembles_3e():
    length, disasm = disassemble([0x3E, 0x00, 0x44])
    assert 3 == length
    assert "ROL $4400,X" == disasm


def test_disassembles_3f():
    length, disasm = disassemble([0x3F])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_40():
    length, disasm = disassemble([0x40])
    assert 1 == length
    assert "RTI" == disasm


def test_disassembles_41():
    length, disasm = disassemble([0x41, 0x44])
    assert 2 == length
    assert "EOR ($44,X)" == disasm


def test_disassembles_42():
    length, disasm = disassemble([0x42])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_43():
    length, disasm = disassemble([0x43])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_44():
    length, disasm = disassemble([0x44])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_45():
    length, disasm = disassemble([0x45, 0x44])
    assert 2 == length
    assert "EOR $44" == disasm


def test_disassembles_46():
    length, disasm = disassemble([0x46, 0x44])
    assert 2 == length
    assert "LSR $44" == disasm


def test_disassembles_47():
    length, disasm = disassemble([0x47])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_48():
    length, disasm = disassemble([0x48])
    assert 1 == length
    assert "PHA" == disasm


def test_disassembles_49():
    length, disasm = disassemble([0x49, 0x44])
    assert 2 == length
    assert "EOR #$44" == disasm


def test_disassembles_4a():
    length, disasm = disassemble([0x4A])
    assert 1 == length
    assert "LSR A" == disasm


def test_disassembles_4b():
    length, disasm = disassemble([0x4B])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_4c():
    length, disasm = disassemble([0x4C, 0x97, 0x55])
    assert 3 == length
    assert "JMP $5597" == disasm


def test_disassembles_4d():
    length, disasm = disassemble([0x4D, 0x00, 0x44])
    assert 3 == length
    assert "EOR $4400" == disasm


def test_disassembles_4e():
    length, disasm = disassemble([0x4E, 0x00, 0x44])
    assert 3 == length
    assert "LSR $4400" == disasm


def test_disassembles_4f():
    length, disasm = disassemble([0x4F])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_50():
    length, disasm = disassemble([0x50, 0x44])
    assert 2 == length
    assert "BVC $0046" == disasm


def test_disassembles_51():
    length, disasm = disassemble([0x51, 0x44])
    assert 2 == length
    assert "EOR ($44),Y" == disasm


def test_disassembles_52():
    length, disasm = disassemble([0x52])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_53():
    length, disasm = disassemble([0x53])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_54():
    length, disasm = disassemble([0x54])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_55():
    length, disasm = disassemble([0x55, 0x44])
    assert 2 == length
    assert "EOR $44,X" == disasm


def test_disassembles_56():
    length, disasm = disassemble([0x56, 0x44])
    assert 2 == length
    assert "LSR $44,X" == disasm


def test_disassembles_57():
    length, disasm = disassemble([0x57])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_58():
    length, disasm = disassemble([0x58])
    assert 1 == length
    assert "CLI" == disasm


def test_disassembles_59():
    length, disasm = disassemble([0x59, 0x00, 0x44])
    assert 3 == length
    assert "EOR $4400,Y" == disasm


def test_disassembles_5a():
    length, disasm = disassemble([0x5A])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_5b():
    length, disasm = disassemble([0x5B])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_5c():
    length, disasm = disassemble([0x5C])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_5d():
    length, disasm = disassemble([0x5D, 0x00, 0x44])
    assert 3 == length
    assert "EOR $4400,X" == disasm


def test_disassembles_5e():
    length, disasm = disassemble([0x5E, 0x00, 0x44])
    assert 3 == length
    assert "LSR $4400,X" == disasm


def test_disassembles_5f():
    length, disasm = disassemble([0x5F])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_60():
    length, disasm = disassemble([0x60])
    assert 1 == length
    assert "RTS" == disasm


def test_disassembles_61():
    length, disasm = disassemble([0x61, 0x44])
    assert 2 == length
    assert "ADC ($44,X)" == disasm


def test_disassembles_62():
    length, disasm = disassemble([0x62])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_63():
    length, disasm = disassemble([0x63])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_64():
    length, disasm = disassemble([0x64])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_64_65c02():
    mpu = MPU65C02()
    length, disasm = disassemble([0x64, 0x12], 0x0000, mpu)
    assert 2 == length
    assert "STZ $12" == disasm


def test_disassembles_65():
    length, disasm = disassemble([0x65, 0x44])
    assert 2 == length
    assert "ADC $44" == disasm


def test_disassembles_66():
    length, disasm = disassemble([0x66, 0x44])
    assert 2 == length
    assert "ROR $44" == disasm


def test_disassembles_67():
    length, disasm = disassemble([0x67])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_68():
    length, disasm = disassemble([0x68])
    assert 1 == length
    assert "PLA" == disasm


def test_disassembles_69():
    length, disasm = disassemble([0x69, 0x44])
    assert 2 == length
    assert "ADC #$44" == disasm


def test_disassembles_6a():
    length, disasm = disassemble([0x6A])
    assert 1 == length
    assert "ROR A" == disasm


def test_disassembles_6b():
    length, disasm = disassemble([0x6B])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_6c():
    length, disasm = disassemble([0x6C, 0x97, 0x55])
    assert 3 == length
    assert "JMP ($5597)" == disasm


def test_disassembles_6d():
    length, disasm = disassemble([0x6D, 0x00, 0x44])
    assert 3 == length
    assert "ADC $4400" == disasm


def test_disassembles_6e():
    length, disasm = disassemble([0x6E, 0x00, 0x44])
    assert 3 == length
    assert "ROR $4400" == disasm


def test_disassembles_6f():
    length, disasm = disassemble([0x6F])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_70():
    length, disasm = disassemble([0x70, 0x44])
    assert 2 == length
    assert "BVS $0046" == disasm


def test_disassembles_71():
    length, disasm = disassemble([0x71, 0x44])
    assert 2 == length
    assert "ADC ($44),Y" == disasm


def test_disassembles_72():
    length, disasm = disassemble([0x72])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_73():
    length, disasm = disassemble([0x73])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_74():
    length, disasm = disassemble([0x74])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_75():
    length, disasm = disassemble([0x75, 0x44])
    assert 2 == length
    assert "ADC $44,X" == disasm


def test_disassembles_76():
    length, disasm = disassemble([0x76, 0x44])
    assert 2 == length
    assert "ROR $44,X" == disasm


def test_disassembles_77():
    length, disasm = disassemble([0x77])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_78():
    length, disasm = disassemble([0x78])
    assert 1 == length
    assert "SEI" == disasm


def test_disassembles_79():
    length, disasm = disassemble([0x79, 0x00, 0x44])
    assert 3 == length
    assert "ADC $4400,Y" == disasm


def test_disassembles_7a():
    length, disasm = disassemble([0x7A])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_7b():
    length, disasm = disassemble([0x7B])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_7c_6502():
    length, disasm = disassemble([0x7C])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_7c_65c02():
    mpu = MPU65C02()
    length, disasm = disassemble([0x7C, 0x34, 0x12], 0x0000, mpu)
    assert 3 == length
    assert "JMP ($1234,X)" == disasm


def test_disassembles_7d():
    length, disasm = disassemble([0x7D, 0x00, 0x44])
    assert 3 == length
    assert "ADC $4400,X" == disasm


def test_disassembles_7e():
    length, disasm = disassemble([0x7E, 0x00, 0x44])
    assert 3 == length
    assert "ROR $4400,X" == disasm


def test_disassembles_7f():
    length, disasm = disassemble([0x7F])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_80():
    length, disasm = disassemble([0x80])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_81():
    length, disasm = disassemble([0x81, 0x44])
    assert 2 == length
    assert "STA ($44,X)" == disasm


def test_disassembles_82():
    length, disasm = disassemble([0x82])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_83():
    length, disasm = disassemble([0x83])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_84():
    length, disasm = disassemble([0x84, 0x44])
    assert 2 == length
    assert "STY $44" == disasm


def test_disassembles_85():
    length, disasm = disassemble([0x85, 0x44])
    assert 2 == length
    assert "STA $44" == disasm


def test_disassembles_86():
    length, disasm = disassemble([0x86, 0x44])
    assert 2 == length
    assert "STX $44" == disasm


def test_disassembles_87():
    length, disasm = disassemble([0x87])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_88():
    length, disasm = disassemble([0x88])
    assert 1 == length
    assert "DEY" == disasm


def test_disassembles_89():
    length, disasm = disassemble([0x89])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_8a():
    length, disasm = disassemble([0x8A])
    assert 1 == length
    assert "TXA" == disasm


def test_disassembles_8b():
    length, disasm = disassemble([0x8B])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_8c():
    length, disasm = disassemble([0x8C, 0x00, 0x44])
    assert 3 == length
    assert "STY $4400" == disasm


def test_disassembles_8d():
    length, disasm = disassemble([0x8D, 0x00, 0x44])
    assert 3 == length
    assert "STA $4400" == disasm


def test_disassembles_8e():
    length, disasm = disassemble([0x8E, 0x00, 0x44])
    assert 3 == length
    assert "STX $4400" == disasm


def test_disassembles_8f():
    length, disasm = disassemble([0x8F])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_90():
    length, disasm = disassemble([0x90, 0x44])
    assert 2 == length
    assert "BCC $0046" == disasm


def test_disassembles_91():
    length, disasm = disassemble([0x91, 0x44])
    assert 2 == length
    assert "STA ($44),Y" == disasm


def test_disassembles_92():
    length, disasm = disassemble([0x92])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_92_65c02():
    mpu = MPU65C02()
    length, disasm = disassemble([0x92, 0x12], 0x0000, mpu)
    assert 2 == length
    assert "STA ($12)" == disasm


def test_disassembles_93():
    length, disasm = disassemble([0x93])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_94():
    length, disasm = disassemble([0x94, 0x44])
    assert 2 == length
    assert "STY $44,X" == disasm


def test_disassembles_95():
    length, disasm = disassemble([0x95, 0x44])
    assert 2 == length
    assert "STA $44,X" == disasm


def test_disassembles_96():
    length, disasm = disassemble([0x96, 0x44])
    assert 2 == length
    assert "STX $44,Y" == disasm


def test_disassembles_97():
    length, disasm = disassemble([0x97])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_98():
    length, disasm = disassemble([0x98])
    assert 1 == length
    assert "TYA" == disasm


def test_disassembles_99():
    length, disasm = disassemble([0x99, 0x00, 0x44])
    assert 3 == length
    assert "STA $4400,Y" == disasm


def test_disassembles_9a():
    length, disasm = disassemble([0x9A])
    assert 1 == length
    assert "TXS" == disasm


def test_disassembles_9b():
    length, disasm = disassemble([0x9B])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_9c():
    length, disasm = disassemble([0x9C])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_9d():
    length, disasm = disassemble([0x9D, 0x00, 0x44])
    assert 3 == length
    assert "STA $4400,X" == disasm


def test_disassembles_9e():
    length, disasm = disassemble([0x9E])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_9f():
    length, disasm = disassemble([0x9F])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_a0():
    length, disasm = disassemble([0xA0, 0x44])
    assert 2 == length
    assert "LDY #$44" == disasm


def test_disassembles_a1():
    length, disasm = disassemble([0xA1, 0x44])
    assert 2 == length
    assert "LDA ($44,X)" == disasm


def test_disassembles_a2():
    length, disasm = disassemble([0xA2, 0x44])
    assert 2 == length
    assert "LDX #$44" == disasm


def test_disassembles_a3():
    length, disasm = disassemble([0xA3])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_a4():
    length, disasm = disassemble([0xA4, 0x44])
    assert 2 == length
    assert "LDY $44" == disasm


def test_disassembles_a5():
    length, disasm = disassemble([0xA5, 0x44])
    assert 2 == length
    assert "LDA $44" == disasm


def test_disassembles_a6():
    length, disasm = disassemble([0xA6, 0x44])
    assert 2 == length
    assert "LDX $44" == disasm


def test_disassembles_a7():
    length, disasm = disassemble([0xA7])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_a8():
    length, disasm = disassemble([0xA8])
    assert 1 == length
    assert "TAY" == disasm


def test_disassembles_a9():
    length, disasm = disassemble([0xA9, 0x44])
    assert 2 == length
    assert "LDA #$44" == disasm


def test_disassembles_aa():
    length, disasm = disassemble([0xAA])
    assert 1 == length
    assert "TAX" == disasm


def test_disassembles_ab():
    length, disasm = disassemble([0xAB])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_ac():
    length, disasm = disassemble([0xAC, 0x00, 0x44])
    assert 3 == length
    assert "LDY $4400" == disasm


def test_disassembles_ad():
    length, disasm = disassemble([0xAD, 0x00, 0x44])
    assert 3 == length
    assert "LDA $4400" == disasm


def test_disassembles_ae():
    length, disasm = disassemble([0xAE, 0x00, 0x44])
    assert 3 == length
    assert "LDX $4400" == disasm


def test_disassembles_af():
    length, disasm = disassemble([0xAF])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_b0():
    length, disasm = disassemble([0xB0, 0x44])
    assert 2 == length
    assert "BCS $0046" == disasm


def test_disassembles_b1():
    length, disasm = disassemble([0xB1, 0x44])
    assert 2 == length
    assert "LDA ($44),Y" == disasm


def test_disassembles_b2():
    length, disasm = disassemble([0xB2])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_b3():
    length, disasm = disassemble([0xB3])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_b4():
    length, disasm = disassemble([0xB4, 0x44])
    assert 2 == length
    assert "LDY $44,X" == disasm


def test_disassembles_b5():
    length, disasm = disassemble([0xB5, 0x44])
    assert 2 == length
    assert "LDA $44,X" == disasm


def test_disassembles_b6():
    length, disasm = disassemble([0xB6, 0x44])
    assert 2 == length
    assert "LDX $44,Y" == disasm


def test_disassembles_b7():
    length, disasm = disassemble([0xB7])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_b8():
    length, disasm = disassemble([0xB8])
    assert 1 == length
    assert "CLV" == disasm


def test_disassembles_b9():
    length, disasm = disassemble([0xB9, 0x00, 0x44])
    assert 3 == length
    assert "LDA $4400,Y" == disasm


def test_disassembles_ba():
    length, disasm = disassemble([0xBA])
    assert 1 == length
    assert "TSX" == disasm


def test_disassembles_bb():
    length, disasm = disassemble([0xBB])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_bc():
    length, disasm = disassemble([0xBC, 0x00, 0x44])
    assert 3 == length
    assert "LDY $4400,X" == disasm


def test_disassembles_bd():
    length, disasm = disassemble([0xBD, 0x00, 0x44])
    assert 3 == length
    assert "LDA $4400,X" == disasm


def test_disassembles_be():
    length, disasm = disassemble([0xBE, 0x00, 0x44])
    assert 3 == length
    assert "LDX $4400,Y" == disasm


def test_disassembles_bf():
    length, disasm = disassemble([0xBF])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_c0():
    length, disasm = disassemble([0xC0, 0x44])
    assert 2 == length
    assert "CPY #$44" == disasm


def test_disassembles_c1():
    length, disasm = disassemble([0xC1, 0x44])
    assert 2 == length
    assert "CMP ($44,X)" == disasm


def test_disassembles_c2():
    length, disasm = disassemble([0xC2])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_c3():
    length, disasm = disassemble([0xC3])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_c4():
    length, disasm = disassemble([0xC4, 0x44])
    assert 2 == length
    assert "CPY $44" == disasm


def test_disassembles_c5():
    length, disasm = disassemble([0xC5, 0x44])
    assert 2 == length
    assert "CMP $44" == disasm


def test_disassembles_c6():
    length, disasm = disassemble([0xC6, 0x44])
    assert 2 == length
    assert "DEC $44" == disasm


def test_disassembles_c7():
    length, disasm = disassemble([0xC7])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_c8():
    length, disasm = disassemble([0xC8])
    assert 1 == length
    assert "INY" == disasm


def test_disassembles_c9():
    length, disasm = disassemble([0xC9, 0x44])
    assert 2 == length
    assert "CMP #$44" == disasm


def test_disassembles_ca():
    length, disasm = disassemble([0xCA])
    assert 1 == length
    assert "DEX" == disasm


def test_disassembles_cb():
    length, disasm = disassemble([0xCB])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_cc():
    length, disasm = disassemble([0xCC, 0x00, 0x44])
    assert 3 == length
    assert "CPY $4400" == disasm


def test_disassembles_cd():
    length, disasm = disassemble([0xCD, 0x00, 0x44])
    assert 3 == length
    assert "CMP $4400" == disasm


def test_disassembles_ce():
    length, disasm = disassemble([0xCE, 0x00, 0x44])
    assert 3 == length
    assert "DEC $4400" == disasm


def test_disassembles_cf():
    length, disasm = disassemble([0xCF])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_d0():
    length, disasm = disassemble([0xD0, 0x44])
    assert 2 == length
    assert "BNE $0046" == disasm


def test_disassembles_d1():
    length, disasm = disassemble([0xD1, 0x44])
    assert 2 == length
    assert "CMP ($44),Y" == disasm


def test_disassembles_d2():
    length, disasm = disassemble([0xD2])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_d3():
    length, disasm = disassemble([0xD3])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_d4():
    length, disasm = disassemble([0xD4])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_d5():
    length, disasm = disassemble([0xD5, 0x44])
    assert 2 == length
    assert "CMP $44,X" == disasm


def test_disassembles_d6():
    length, disasm = disassemble([0xD6, 0x44])
    assert 2 == length
    assert "DEC $44,X" == disasm


def test_disassembles_d7():
    length, disasm = disassemble([0xD7])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_d8():
    length, disasm = disassemble([0xD8])
    assert 1 == length
    assert "CLD" == disasm


def test_disassembles_d9():
    length, disasm = disassemble([0xD9, 0x00, 0x44])
    assert 3 == length
    assert "CMP $4400,Y" == disasm


def test_disassembles_da():
    length, disasm = disassemble([0xDA])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_db():
    length, disasm = disassemble([0xDB])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_dc():
    length, disasm = disassemble([0xDC])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_dd():
    length, disasm = disassemble([0xDD, 0x00, 0x44])
    assert 3 == length
    assert "CMP $4400,X" == disasm


def test_disassembles_de():
    length, disasm = disassemble([0xDE, 0x00, 0x44])
    assert 3 == length
    assert "DEC $4400,X" == disasm


def test_disassembles_df():
    length, disasm = disassemble([0xDF])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_e0():
    length, disasm = disassemble([0xE0, 0x44])
    assert 2 == length
    assert "CPX #$44" == disasm


def test_disassembles_e1():
    length, disasm = disassemble([0xE1, 0x44])
    assert 2 == length
    assert "SBC ($44,X)" == disasm


def test_disassembles_e2():
    length, disasm = disassemble([0xE2])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_e3():
    length, disasm = disassemble([0xE3])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_e4():
    length, disasm = disassemble([0xE4, 0x44])
    assert 2 == length
    assert "CPX $44" == disasm


def test_disassembles_e5():
    length, disasm = disassemble([0xE5, 0x44])
    assert 2 == length
    assert "SBC $44" == disasm


def test_disassembles_e6():
    length, disasm = disassemble([0xE6, 0x44])
    assert 2 == length
    assert "INC $44" == disasm


def test_disassembles_e7():
    length, disasm = disassemble([0xE7])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_e8():
    length, disasm = disassemble([0xE8])
    assert 1 == length
    assert "INX" == disasm


def test_disassembles_e9():
    length, disasm = disassemble([0xE9, 0x44])
    assert 2 == length
    assert "SBC #$44" == disasm


def test_disassembles_ea():
    length, disasm = disassemble([0xEA])
    assert 1 == length
    assert "NOP" == disasm


def test_disassembles_eb():
    length, disasm = disassemble([0xEB])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_ec():
    length, disasm = disassemble([0xEC, 0x00, 0x44])
    assert 3 == length
    assert "CPX $4400" == disasm


def test_disassembles_ed():
    length, disasm = disassemble([0xED, 0x00, 0x44])
    assert 3 == length
    assert "SBC $4400" == disasm


def test_disassembles_ee():
    length, disasm = disassemble([0xEE, 0x00, 0x44])
    assert 3 == length
    assert "INC $4400" == disasm


def test_disassembles_ef():
    length, disasm = disassemble([0xEF])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_f0_forward():
    length, disasm = disassemble([0xF0, 0x44])
    assert 2 == length
    assert "BEQ $0046" == disasm


def test_disassembled_f0_backward():
    length, disasm = disassemble([0xF0, 0xFC], pc=0xC000)
    assert 2 == length
    assert "BEQ $bffe" == disasm


def test_disassembles_f1():
    length, disasm = disassemble([0xF1, 0x44])
    assert 2 == length
    assert "SBC ($44),Y" == disasm


def test_disassembles_f2():
    length, disasm = disassemble([0xF2])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_f3():
    length, disasm = disassemble([0xF3])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_f4():
    length, disasm = disassemble([0xF4])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_f5():
    length, disasm = disassemble([0xF5, 0x44])
    assert 2 == length
    assert "SBC $44,X" == disasm


def test_disassembles_f6():
    length, disasm = disassemble([0xF6, 0x44])
    assert 2 == length
    assert "INC $44,X" == disasm


def test_disassembles_f7():
    length, disasm = disassemble([0xF7])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_f8():
    length, disasm = disassemble([0xF8])
    assert 1 == length
    assert "SED" == disasm


def test_disassembles_f9():
    length, disasm = disassemble([0xF9, 0x00, 0x44])
    assert 3 == length
    assert "SBC $4400,Y" == disasm


def test_disassembles_fa():
    length, disasm = disassemble([0xFA])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_fb():
    length, disasm = disassemble([0xFB])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_fc():
    length, disasm = disassemble([0xFC])
    assert 1 == length
    assert "???" == disasm


def test_disassembles_fd():
    length, disasm = disassemble([0xFD, 0x00, 0x44])
    assert 3 == length
    assert "SBC $4400,X" == disasm


def test_disassembles_fe():
    length, disasm = disassemble([0xFE, 0x00, 0x44])
    assert 3 == length
    assert "INC $4400,X" == disasm


def test_disassembles_ff():
    length, disasm = disassemble([0xFF])
    assert 1 == length
    assert "???" == disasm


# Test Helpers


def disassemble(bytes, pc=0, mpu=None):
    if mpu is None:
        mpu = MPU()
    address_parser = AddressParser()
    disasm = Disassembler(mpu, address_parser)
    mpu.memory[pc : len(bytes) - 81] = bytes
    return disasm.instruction_at(pc)
