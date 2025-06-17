import py65.assembler
import py65.devices.mpu6502

# Reset


def test_reset_sets_registers_to_initial_states():
    mpu = _make_mpu()
    mpu.reset()
    assert 0xFF == mpu.sp
    assert 0 == mpu.a
    assert 0 == mpu.x
    assert 0 == mpu.y
    assert mpu.BREAK | mpu.UNUSED == mpu.p


def test_reset_sets_pc_to_0_by_default():
    mpu = _make_mpu()
    mpu.reset()
    assert mpu.pc == 0


def test_reset_sets_pc_to_start_pc_if_not_None():
    mpu = _make_mpu(pc=0x1234)
    mpu.reset()
    assert mpu.pc == 0x1234


def test_reset_reads_reset_vector_if_start_pc_is_None():
    mpu = _make_mpu(pc=None)
    target = 0xABCD
    mpu.memory[mpu.RESET + 0] = target & 0xFF
    mpu.memory[mpu.RESET + 1] = target >> 8
    mpu.reset()
    assert mpu.pc == 0xABCD


# ADC Absolute


def test_adc_bcd_off_absolute_carry_clear_in_accumulator_zeroes():
    mpu = _make_mpu()
    mpu.a = 0
    # $0000 ADC $C000
    _write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
    assert 0x10000 == len(mpu.memory)

    mpu.memory[0xC000] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_adc_bcd_off_absolute_carry_set_in_accumulator_zero():
    mpu = _make_mpu()
    mpu.a = 0
    mpu.p |= mpu.CARRY
    # $0000 ADC $C000
    _write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
    mpu.memory[0xC000] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x01 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY != mpu.p & mpu.CARRY


def test_adc_bcd_off_absolute_carry_clear_in_no_carry_clear_out():
    mpu = _make_mpu()
    mpu.a = 0x01
    # $0000 ADC $C000
    _write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
    mpu.memory[0xC000] = 0xFE
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_absolute_carry_clear_in_carry_set_out():
    mpu = _make_mpu()
    mpu.a = 0x02
    # $0000 ADC $C000
    _write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
    mpu.memory[0xC000] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x01 == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_absolute_overflow_clr_no_carry_01_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    # $0000 ADC $C000
    _write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
    mpu.memory[0xC000] = 0x01
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x02 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_absolute_overflow_clr_no_carry_01_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    # $0000 ADC $C000
    _write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
    mpu.memory[0xC000] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_absolute_overflow_set_no_carry_7f_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x7F
    # $0000 ADC $C000
    _write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
    mpu.memory[0xC000] = 0x01
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_absolute_overflow_set_no_carry_80_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x80
    # $0000 ADC $C000
    _write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
    mpu.memory[0xC000] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x7F == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_absolute_overflow_set_on_40_plus_40():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.OVERFLOW)
    mpu.a = 0x40
    # $0000 ADC $C000
    _write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
    mpu.memory[0xC000] = 0x40
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO


# ADC Zero Page


def test_adc_bcd_off_zp_carry_clear_in_accumulator_zeroes():
    mpu = _make_mpu()
    mpu.a = 0
    # $0000 ADC $00B0
    _write(mpu.memory, 0x0000, (0x65, 0xB0))
    mpu.memory[0x00B0] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_adc_bcd_off_zp_carry_set_in_accumulator_zero():
    mpu = _make_mpu()
    mpu.a = 0
    mpu.p |= mpu.CARRY
    # $0000 ADC $00B0
    _write(mpu.memory, 0x0000, (0x65, 0xB0))
    mpu.memory[0x00B0] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY != mpu.p & mpu.CARRY


def test_adc_bcd_off_zp_carry_clear_in_no_carry_clear_out():
    mpu = _make_mpu()
    mpu.a = 0x01
    # $0000 ADC $00B0
    _write(mpu.memory, 0x0000, (0x65, 0xB0))
    mpu.memory[0x00B0] = 0xFE
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_zp_carry_clear_in_carry_set_out():
    mpu = _make_mpu()
    mpu.a = 0x02
    # $0000 ADC $00B0
    _write(mpu.memory, 0x0000, (0x65, 0xB0))
    mpu.memory[0x00B0] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_zp_overflow_clr_no_carry_01_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    # $0000 ADC $00B0
    _write(mpu.memory, 0x0000, (0x65, 0xB0))
    mpu.memory[0x00B0] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x02 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_zp_overflow_clr_no_carry_01_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    # $0000 ADC $00B0
    _write(mpu.memory, 0x0000, (0x65, 0xB0))
    mpu.memory[0x00B0] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_zp_overflow_set_no_carry_7f_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x7F
    # $0000 ADC $00B0
    _write(mpu.memory, 0x0000, (0x65, 0xB0))
    mpu.memory[0x00B0] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_zp_overflow_set_no_carry_80_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x80
    # $0000 ADC $00B0
    _write(mpu.memory, 0x0000, (0x65, 0xB0))
    mpu.memory[0x00B0] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x7F == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_zp_overflow_set_on_40_plus_40():
    mpu = _make_mpu()
    mpu.a = 0x40
    mpu.p &= ~(mpu.OVERFLOW)
    # $0000 ADC $00B0
    _write(mpu.memory, 0x0000, (0x65, 0xB0))
    mpu.memory[0x00B0] = 0x40
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO


# ADC Immediate


def test_adc_bcd_off_immediate_carry_clear_in_accumulator_zeroes():
    mpu = _make_mpu()
    mpu.a = 0
    # $0000 ADC #$00
    _write(mpu.memory, 0x0000, (0x69, 0x00))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_adc_bcd_off_immediate_carry_set_in_accumulator_zero():
    mpu = _make_mpu()
    mpu.a = 0
    mpu.p |= mpu.CARRY
    # $0000 ADC #$00
    _write(mpu.memory, 0x0000, (0x69, 0x00))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY != mpu.p & mpu.CARRY


def test_adc_bcd_off_immediate_carry_clear_in_no_carry_clear_out():
    mpu = _make_mpu()
    mpu.a = 0x01
    # $0000 ADC #$FE
    _write(mpu.memory, 0x0000, (0x69, 0xFE))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_immediate_carry_clear_in_carry_set_out():
    mpu = _make_mpu()
    mpu.a = 0x02
    # $0000 ADC #$FF
    _write(mpu.memory, 0x0000, (0x69, 0xFF))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_immediate_overflow_clr_no_carry_01_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    # $0000 ADC #$01
    _write(mpu.memory, 0x000, (0x69, 0x01))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x02 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_immediate_overflow_clr_no_carry_01_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    # $0000 ADC #$FF
    _write(mpu.memory, 0x000, (0x69, 0xFF))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_immediate_overflow_set_no_carry_7f_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x7F
    # $0000 ADC #$01
    _write(mpu.memory, 0x000, (0x69, 0x01))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_immediate_overflow_set_no_carry_80_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x80
    # $0000 ADC #$FF
    _write(mpu.memory, 0x000, (0x69, 0xFF))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x7F == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_immediate_overflow_set_on_40_plus_40():
    mpu = _make_mpu()
    mpu.a = 0x40
    # $0000 ADC #$40
    _write(mpu.memory, 0x0000, (0x69, 0x40))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_on_immediate_79_plus_00_carry_set():
    mpu = _make_mpu()
    mpu.p |= mpu.DECIMAL
    mpu.p |= mpu.CARRY
    mpu.a = 0x79
    # $0000 ADC #$00
    _write(mpu.memory, 0x0000, (0x69, 0x00))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY


def test_adc_bcd_on_immediate_6f_plus_00_carry_set():
    mpu = _make_mpu()
    mpu.p |= mpu.DECIMAL
    mpu.p |= mpu.CARRY
    mpu.a = 0x6F
    # $0000 ADC #$00
    _write(mpu.memory, 0x0000, (0x69, 0x00))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x76 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY


def test_adc_bcd_on_immediate_9c_plus_9d():
    mpu = _make_mpu()
    mpu.p |= mpu.DECIMAL
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x9C
    # $0000 ADC #$9d
    # $0002 ADC #$9d
    _write(mpu.memory, 0x0000, (0x69, 0x9D))
    _write(mpu.memory, 0x0002, (0x69, 0x9D))
    mpu.step()
    assert 0x9F == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY
    mpu.step()
    assert 0x0004 == mpu.pc
    assert 0x93 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ADC Absolute, X-Indexed


def test_adc_bcd_off_abs_x_carry_clear_in_accumulator_zeroes():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 ADC $C000,X
    _write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_adc_bcd_off_abs_x_carry_set_in_accumulator_zero():
    mpu = _make_mpu()
    mpu.a = 0
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ADC $C000,X
    _write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x01 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY != mpu.p & mpu.CARRY


def test_adc_bcd_off_abs_x_carry_clear_in_no_carry_clear_out():
    mpu = _make_mpu()
    mpu.a = 0x01
    mpu.x = 0x03
    # $0000 ADC $C000,X
    _write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.x] = 0xFE
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_abs_x_carry_clear_in_carry_set_out():
    mpu = _make_mpu()
    mpu.a = 0x02
    mpu.x = 0x03
    # $0000 ADC $C000,X
    _write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x01 == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_abs_x_overflow_clr_no_carry_01_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    # $0000 ADC $C000,X
    _write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.x] = 0x01
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x02 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_abs_x_overflow_clr_no_carry_01_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    # $0000 ADC $C000,X
    _write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_abs_x_overflow_set_no_carry_7f_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x7F
    # $0000 ADC $C000,X
    _write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.x] = 0x01
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_abs_x_overflow_set_no_carry_80_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x80
    # $0000 ADC $C000,X
    _write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x7F == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_abs_x_overflow_set_on_40_plus_40():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.OVERFLOW)
    mpu.a = 0x40
    mpu.x = 0x03
    # $0000 ADC $C000,X
    _write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.x] = 0x40
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO


# ADC Absolute, Y-Indexed


def test_adc_bcd_off_abs_y_carry_clear_in_accumulator_zeroes():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.y = 0x03
    # $0000 ADC $C000,Y
    _write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.y] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_adc_bcd_off_abs_y_carry_set_in_accumulator_zero():
    mpu = _make_mpu()
    mpu.a = 0
    mpu.y = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ADC $C000,Y
    _write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.y] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x01 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY != mpu.p & mpu.CARRY


def test_adc_bcd_off_abs_y_carry_clear_in_no_carry_clear_out():
    mpu = _make_mpu()
    mpu.a = 0x01
    mpu.y = 0x03
    # $0000 ADC $C000,Y
    _write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.y] = 0xFE
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_abs_y_carry_clear_in_carry_set_out():
    mpu = _make_mpu()
    mpu.a = 0x02
    mpu.y = 0x03
    # $0000 ADC $C000,Y
    _write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.y] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x01 == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_abs_y_overflow_clr_no_carry_01_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    # $0000 ADC $C000,Y
    _write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.y] = 0x01
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x02 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_abs_y_overflow_clr_no_carry_01_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    # $0000 ADC $C000,Y
    _write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.y] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_abs_y_overflow_set_no_carry_7f_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x7F
    # $0000 ADC $C000,Y
    _write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.y] = 0x01
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_abs_y_overflow_set_no_carry_80_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x80
    # $0000 ADC $C000,Y
    _write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.y] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x7F == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_abs_y_overflow_set_on_40_plus_40():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.OVERFLOW)
    mpu.a = 0x40
    mpu.y = 0x03
    # $0000 ADC $C000,Y
    _write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
    mpu.memory[0xC000 + mpu.y] = 0x40
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO


# ADC Zero Page, X-Indexed


def test_adc_bcd_off_zp_x_carry_clear_in_accumulator_zeroes():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 ADC $0010,X
    _write(mpu.memory, 0x0000, (0x75, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_adc_bcd_off_zp_x_carry_set_in_accumulator_zero():
    mpu = _make_mpu()
    mpu.a = 0
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ADC $0010,X
    _write(mpu.memory, 0x0000, (0x75, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY != mpu.p & mpu.CARRY


def test_adc_bcd_off_zp_x_carry_clear_in_no_carry_clear_out():
    mpu = _make_mpu()
    mpu.a = 0x01
    mpu.x = 0x03
    # $0000 ADC $0010,X
    _write(mpu.memory, 0x0000, (0x75, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xFE
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_zp_x_carry_clear_in_carry_set_out():
    mpu = _make_mpu()
    mpu.a = 0x02
    mpu.x = 0x03
    # $0000 ADC $0010,X
    _write(mpu.memory, 0x0000, (0x75, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_zp_x_overflow_clr_no_carry_01_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    mpu.x = 0x03
    # $0000 ADC $0010,X
    _write(mpu.memory, 0x0000, (0x75, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x02 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_zp_x_overflow_clr_no_carry_01_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    mpu.x = 0x03
    # $0000 ADC $0010,X
    _write(mpu.memory, 0x0000, (0x75, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_zp_x_overflow_set_no_carry_7f_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x7F
    mpu.x = 0x03
    # $0000 ADC $0010,X
    _write(mpu.memory, 0x0000, (0x75, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_zp_x_overflow_set_no_carry_80_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x80
    mpu.x = 0x03
    # $0000 ADC $0010,X
    _write(mpu.memory, 0x0000, (0x75, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x7F == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_zp_x_overflow_set_on_40_plus_40():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.OVERFLOW)
    mpu.a = 0x40
    mpu.x = 0x03
    # $0000 ADC $0010,X
    _write(mpu.memory, 0x0000, (0x75, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x40
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO


# ADC Indirect, Indexed (X)


def test_adc_bcd_off_ind_indexed_carry_clear_in_accumulator_zeroes():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 ADC ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x61, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_adc_bcd_off_ind_indexed_carry_set_in_accumulator_zero():
    mpu = _make_mpu()
    mpu.a = 0
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ADC ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x61, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY != mpu.p & mpu.CARRY


def test_adc_bcd_off_ind_indexed_carry_clear_in_no_carry_clear_out():
    mpu = _make_mpu()
    mpu.a = 0x01
    mpu.x = 0x03
    # $0000 ADC ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x61, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFE
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_ind_indexed_carry_clear_in_carry_set_out():
    mpu = _make_mpu()
    mpu.a = 0x02
    mpu.x = 0x03
    # $0000 ADC ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x61, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_ind_indexed_overflow_clr_no_carry_01_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    mpu.x = 0x03
    # $0000 ADC ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x61, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x02 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_ind_indexed_overflow_clr_no_carry_01_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    mpu.x = 0x03
    # $0000 ADC ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x61, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_ind_indexed_overflow_set_no_carry_7f_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x7F
    mpu.x = 0x03
    # $0000 ADC ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x61, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_ind_indexed_overflow_set_no_carry_80_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x80
    mpu.x = 0x03
    # $0000 ADC ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x61, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x7F == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_ind_indexed_overflow_set_on_40_plus_40():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.OVERFLOW)
    mpu.a = 0x40
    mpu.x = 0x03
    # $0000 ADC ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x61, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x40
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO


# ADC Indexed, Indirect (Y)


def test_adc_bcd_off_indexed_ind_carry_clear_in_accumulator_zeroes():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.y = 0x03
    # $0000 ADC ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x71, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_adc_bcd_off_indexed_ind_carry_set_in_accumulator_zero():
    mpu = _make_mpu()
    mpu.a = 0
    mpu.y = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ADC ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x71, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY != mpu.p & mpu.CARRY


def test_adc_bcd_off_indexed_ind_carry_clear_in_no_carry_clear_out():
    mpu = _make_mpu()
    mpu.a = 0x01
    mpu.y = 0x03
    # $0000 ADC ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x71, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0xFE
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_indexed_ind_carry_clear_in_carry_set_out():
    mpu = _make_mpu()
    mpu.a = 0x02
    mpu.y = 0x03
    # $0000 ADC ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x71, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_adc_bcd_off_indexed_ind_overflow_clr_no_carry_01_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    mpu.y = 0x03
    # $0000 $0000 ADC ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x71, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x02 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_indexed_ind_overflow_clr_no_carry_01_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x01
    mpu.y = 0x03
    # $0000 ADC ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x71, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_indexed_ind_overflow_set_no_carry_7f_plus_01():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x7F
    mpu.y = 0x03
    # $0000 ADC ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x71, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_indexed_ind_overflow_set_no_carry_80_plus_ff():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.a = 0x80
    mpu.y = 0x03
    # $0000 $0000 ADC ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x71, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x7F == mpu.a
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_adc_bcd_off_indexed_ind_overflow_set_on_40_plus_40():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.OVERFLOW)
    mpu.a = 0x40
    mpu.y = 0x03
    # $0000 ADC ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x71, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x40
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO


# AND (Absolute)


def test_and_absolute_all_zeros_setting_zero_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    # $0000 AND $ABCD
    _write(mpu.memory, 0x0000, (0x2D, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_and_absolute_zeros_and_ones_setting_negative_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    # $0000 AND $ABCD
    _write(mpu.memory, 0x0000, (0x2D, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xAA
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xAA == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# AND (Absolute)


def test_and_zp_all_zeros_setting_zero_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    # $0000 AND $0010
    _write(mpu.memory, 0x0000, (0x25, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_and_zp_zeros_and_ones_setting_negative_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    # $0000 AND $0010
    _write(mpu.memory, 0x0000, (0x25, 0x10))
    mpu.memory[0x0010] = 0xAA
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xAA == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# AND (Immediate)


def test_and_immediate_all_zeros_setting_zero_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    # $0000 AND #$00
    _write(mpu.memory, 0x0000, (0x29, 0x00))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_and_immediate_zeros_and_ones_setting_negative_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    # $0000 AND #$AA
    _write(mpu.memory, 0x0000, (0x29, 0xAA))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xAA == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# AND (Absolute, X-Indexed)


def test_and_abs_x_all_zeros_setting_zero_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.x = 0x03
    # $0000 AND $ABCD,X
    _write(mpu.memory, 0x0000, (0x3D, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_and_abs_x_zeros_and_ones_setting_negative_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.x = 0x03
    # $0000 AND $ABCD,X
    _write(mpu.memory, 0x0000, (0x3D, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0xAA
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xAA == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# AND (Absolute, Y-Indexed)


def test_and_abs_y_all_zeros_setting_zero_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.y = 0x03
    # $0000 AND $ABCD,X
    _write(mpu.memory, 0x0000, (0x39, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_and_abs_y_zeros_and_ones_setting_negative_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.y = 0x03
    # $0000 AND $ABCD,X
    _write(mpu.memory, 0x0000, (0x39, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0xAA
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xAA == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# AND Indirect, Indexed (X)


def test_and_ind_indexed_x_all_zeros_setting_zero_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.x = 0x03
    # $0000 AND ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x21, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_and_ind_indexed_x_zeros_and_ones_setting_negative_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.x = 0x03
    # $0000 AND ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x21, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xAA
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xAA == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# AND Indexed, Indirect (Y)


def test_and_indexed_ind_y_all_zeros_setting_zero_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.y = 0x03
    # $0000 AND ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x31, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_and_indexed_ind_y_zeros_and_ones_setting_negative_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.y = 0x03
    # $0000 AND ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x31, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0xAA
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xAA == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# AND Zero Page, X-Indexed


def test_and_zp_x_all_zeros_setting_zero_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.x = 0x03
    # $0000 AND $0010,X
    _write(mpu.memory, 0x0000, (0x35, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_and_zp_x_all_zeros_and_ones_setting_negative_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.x = 0x03
    # $0000 AND $0010,X
    _write(mpu.memory, 0x0000, (0x35, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xAA
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xAA == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# ASL Accumulator


def test_asl_accumulator_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    # $0000 ASL A
    mpu.memory[0x0000] = 0x0A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_asl_accumulator_sets_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x40
    # $0000 ASL A
    mpu.memory[0x0000] = 0x0A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_asl_accumulator_shifts_out_zero():
    mpu = _make_mpu()
    mpu.a = 0x7F
    # $0000 ASL A
    mpu.memory[0x0000] = 0x0A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xFE == mpu.a
    assert 0 == mpu.p & mpu.CARRY


def test_asl_accumulator_shifts_out_one():
    mpu = _make_mpu()
    mpu.a = 0xFF
    # $0000 ASL A
    mpu.memory[0x0000] = 0x0A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xFE == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY


def test_asl_accumulator_80_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0x80
    mpu.p &= ~(mpu.ZERO)
    # $0000 ASL A
    mpu.memory[0x0000] = 0x0A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO


# ASL Absolute


def test_asl_absolute_sets_z_flag():
    mpu = _make_mpu()
    # $0000 ASL $ABCD
    _write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_asl_absolute_sets_n_flag():
    mpu = _make_mpu()
    # $0000 ASL $ABCD
    _write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x40
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.memory[0xABCD]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_asl_absolute_shifts_out_zero():
    mpu = _make_mpu()
    mpu.a = 0xAA
    # $0000 ASL $ABCD
    _write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x7F
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xAA == mpu.a
    assert 0xFE == mpu.memory[0xABCD]
    assert 0 == mpu.p & mpu.CARRY


def test_asl_absolute_shifts_out_one():
    mpu = _make_mpu()
    mpu.a = 0xAA
    # $0000 ASL $ABCD
    _write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xAA == mpu.a
    assert 0xFE == mpu.memory[0xABCD]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ASL Zero Page


def test_asl_zp_sets_z_flag():
    mpu = _make_mpu()
    # $0000 ASL $0010
    _write(mpu.memory, 0x0000, (0x06, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_asl_zp_sets_n_flag():
    mpu = _make_mpu()
    # $0000 ASL $0010
    _write(mpu.memory, 0x0000, (0x06, 0x10))
    mpu.memory[0x0010] = 0x40
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.memory[0x0010]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_asl_zp_shifts_out_zero():
    mpu = _make_mpu()
    mpu.a = 0xAA
    # $0000 ASL $0010
    _write(mpu.memory, 0x0000, (0x06, 0x10))
    mpu.memory[0x0010] = 0x7F
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xAA == mpu.a
    assert 0xFE == mpu.memory[0x0010]
    assert 0 == mpu.p & mpu.CARRY


def test_asl_zp_shifts_out_one():
    mpu = _make_mpu()
    mpu.a = 0xAA
    # $0000 ASL $0010
    _write(mpu.memory, 0x0000, (0x06, 0x10))
    mpu.memory[0x0010] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xAA == mpu.a
    assert 0xFE == mpu.memory[0x0010]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ASL Absolute, X-Indexed


def test_asl_abs_x_indexed_sets_z_flag():
    mpu = _make_mpu()
    mpu.x = 0x03
    # $0000 ASL $ABCD,X
    _write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_asl_abs_x_indexed_sets_n_flag():
    mpu = _make_mpu()
    mpu.x = 0x03
    # $0000 ASL $ABCD,X
    _write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x40
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.memory[0xABCD + mpu.x]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_asl_abs_x_indexed_shifts_out_zero():
    mpu = _make_mpu()
    mpu.a = 0xAA
    mpu.x = 0x03
    # $0000 ASL $ABCD,X
    _write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x7F
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xAA == mpu.a
    assert 0xFE == mpu.memory[0xABCD + mpu.x]
    assert 0 == mpu.p & mpu.CARRY


def test_asl_abs_x_indexed_shifts_out_one():
    mpu = _make_mpu()
    mpu.a = 0xAA
    mpu.x = 0x03
    # $0000 ASL $ABCD,X
    _write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xAA == mpu.a
    assert 0xFE == mpu.memory[0xABCD + mpu.x]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ASL Zero Page, X-Indexed


def test_asl_zp_x_indexed_sets_z_flag():
    mpu = _make_mpu()
    mpu.x = 0x03
    # $0000 ASL $0010,X
    _write(mpu.memory, 0x0000, (0x16, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010 + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_asl_zp_x_indexed_sets_n_flag():
    mpu = _make_mpu()
    mpu.x = 0x03
    # $0000 ASL $0010,X
    _write(mpu.memory, 0x0000, (0x16, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x40
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.memory[0x0010 + mpu.x]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_asl_zp_x_indexed_shifts_out_zero():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.a = 0xAA
    # $0000 ASL $0010,X
    _write(mpu.memory, 0x0000, (0x16, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x7F
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xAA == mpu.a
    assert 0xFE == mpu.memory[0x0010 + mpu.x]
    assert 0 == mpu.p & mpu.CARRY


def test_asl_zp_x_indexed_shifts_out_one():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.a = 0xAA
    # $0000 ASL $0010,X
    _write(mpu.memory, 0x0000, (0x16, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xAA == mpu.a
    assert 0xFE == mpu.memory[0x0010 + mpu.x]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# BCC


def test_bcc_carry_clear_branches_relative_forward():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    # $0000 BCC +6
    _write(mpu.memory, 0x0000, (0x90, 0x06))
    mpu.step()
    assert 0x0002 + 0x06 == mpu.pc


def test_bcc_carry_clear_branches_relative_backward():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.pc = 0x0050
    rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
    # $0000 BCC -6
    _write(mpu.memory, 0x0050, (0x90, rel))
    mpu.step()
    assert 0x0052 - 0x06 == mpu.pc


def test_bcc_carry_set_does_not_branch():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 BCC +6
    _write(mpu.memory, 0x0000, (0x90, 0x06))
    mpu.step()
    assert 0x0002 == mpu.pc


# BCS


def test_bcs_carry_set_branches_relative_forward():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 BCS +6
    _write(mpu.memory, 0x0000, (0xB0, 0x06))
    mpu.step()
    assert 0x0002 + 0x06 == mpu.pc


def test_bcs_carry_set_branches_relative_backward():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    mpu.pc = 0x0050
    rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
    # $0000 BCS -6
    _write(mpu.memory, 0x0050, (0xB0, rel))
    mpu.step()
    assert 0x0052 - 0x06 == mpu.pc


def test_bcs_carry_clear_does_not_branch():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    # $0000 BCS +6
    _write(mpu.memory, 0x0000, (0xB0, 0x06))
    mpu.step()
    assert 0x0002 == mpu.pc


# BEQ


def test_beq_zero_set_branches_relative_forward():
    mpu = _make_mpu()
    mpu.p |= mpu.ZERO
    # $0000 BEQ +6
    _write(mpu.memory, 0x0000, (0xF0, 0x06))
    mpu.step()
    assert 0x0002 + 0x06 == mpu.pc


def test_beq_zero_set_branches_relative_backward():
    mpu = _make_mpu()
    mpu.p |= mpu.ZERO
    mpu.pc = 0x0050
    rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
    # $0000 BEQ -6
    _write(mpu.memory, 0x0050, (0xF0, rel))
    mpu.step()
    assert 0x0052 - 0x06 == mpu.pc


def test_beq_zero_clear_does_not_branch():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    # $0000 BEQ +6
    _write(mpu.memory, 0x0000, (0xF0, 0x06))
    mpu.step()
    assert 0x0002 == mpu.pc


# BIT (Absolute)


def test_bit_abs_copies_bit_7_of_memory_to_n_flag_when_0():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    # $0000 BIT $FEED
    _write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
    mpu.memory[0xFEED] = 0xFF
    mpu.a = 0xFF
    mpu.step()
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_bit_abs_copies_bit_7_of_memory_to_n_flag_when_1():
    mpu = _make_mpu()
    mpu.p |= mpu.NEGATIVE
    # $0000 BIT $FEED
    _write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
    mpu.memory[0xFEED] = 0x00
    mpu.a = 0xFF
    mpu.step()
    assert 0 == mpu.p & mpu.NEGATIVE


def test_bit_abs_copies_bit_6_of_memory_to_v_flag_when_0():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.OVERFLOW)
    # $0000 BIT $FEED
    _write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
    mpu.memory[0xFEED] = 0xFF
    mpu.a = 0xFF
    mpu.step()
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_bit_abs_copies_bit_6_of_memory_to_v_flag_when_1():
    mpu = _make_mpu()
    mpu.p |= mpu.OVERFLOW
    # $0000 BIT $FEED
    _write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
    mpu.memory[0xFEED] = 0x00
    mpu.a = 0xFF
    mpu.step()
    assert 0 == mpu.p & mpu.OVERFLOW


def test_bit_abs_stores_result_of_and_in_z_preserves_a_when_1():
    mpu = _make_mpu()
    mpu.p &= ~mpu.ZERO
    # $0000 BIT $FEED
    _write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
    mpu.memory[0xFEED] = 0x00
    mpu.a = 0x01
    mpu.step()
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0x01 == mpu.a
    assert 0x00 == mpu.memory[0xFEED]


def test_bit_abs_stores_result_of_and_when_nonzero_in_z_preserves_a():
    mpu = _make_mpu()
    mpu.p |= mpu.ZERO
    # $0000 BIT $FEED
    _write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
    mpu.memory[0xFEED] = 0x01
    mpu.a = 0x01
    mpu.step()
    assert 0 == mpu.p & mpu.ZERO  # result of AND is non-zero
    assert 0x01 == mpu.a
    assert 0x01 == mpu.memory[0xFEED]


def test_bit_abs_stores_result_of_and_when_zero_in_z_preserves_a():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    # $0000 BIT $FEED
    _write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
    mpu.memory[0xFEED] = 0x00
    mpu.a = 0x01
    mpu.step()
    assert mpu.ZERO == mpu.p & mpu.ZERO  # result of AND is zero
    assert 0x01 == mpu.a
    assert 0x00 == mpu.memory[0xFEED]


# BIT (Zero Page)


def test_bit_zp_copies_bit_7_of_memory_to_n_flag_when_0():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    # $0000 BIT $0010
    _write(mpu.memory, 0x0000, (0x24, 0x10))
    mpu.memory[0x0010] = 0xFF
    mpu.a = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 3 == mpu.processorCycles
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_bit_zp_copies_bit_7_of_memory_to_n_flag_when_1():
    mpu = _make_mpu()
    mpu.p |= mpu.NEGATIVE
    # $0000 BIT $0010
    _write(mpu.memory, 0x0000, (0x24, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.a = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 3 == mpu.processorCycles
    assert 0 == mpu.p & mpu.NEGATIVE


def test_bit_zp_copies_bit_6_of_memory_to_v_flag_when_0():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.OVERFLOW)
    # $0000 BIT $0010
    _write(mpu.memory, 0x0000, (0x24, 0x10))
    mpu.memory[0x0010] = 0xFF
    mpu.a = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 3 == mpu.processorCycles
    assert mpu.OVERFLOW == mpu.p & mpu.OVERFLOW


def test_bit_zp_copies_bit_6_of_memory_to_v_flag_when_1():
    mpu = _make_mpu()
    mpu.p |= mpu.OVERFLOW
    # $0000 BIT $0010
    _write(mpu.memory, 0x0000, (0x24, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.a = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 3 == mpu.processorCycles
    assert 0 == mpu.p & mpu.OVERFLOW


def test_bit_zp_stores_result_of_and_in_z_preserves_a_when_1():
    mpu = _make_mpu()
    mpu.p &= ~mpu.ZERO
    # $0000 BIT $0010
    _write(mpu.memory, 0x0000, (0x24, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.a = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 3 == mpu.processorCycles
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0x01 == mpu.a
    assert 0x00 == mpu.memory[0x0010]


def test_bit_zp_stores_result_of_and_when_nonzero_in_z_preserves_a():
    mpu = _make_mpu()
    mpu.p |= mpu.ZERO
    # $0000 BIT $0010
    _write(mpu.memory, 0x0000, (0x24, 0x10))
    mpu.memory[0x0010] = 0x01
    mpu.a = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 3 == mpu.processorCycles
    assert 0 == mpu.p & mpu.ZERO  # result of AND is non-zero
    assert 0x01 == mpu.a
    assert 0x01 == mpu.memory[0x0010]


def test_bit_zp_stores_result_of_and_when_zero_in_z_preserves_a():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    # $0000 BIT $0010
    _write(mpu.memory, 0x0000, (0x24, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.a = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 3 == mpu.processorCycles
    assert mpu.ZERO == mpu.p & mpu.ZERO  # result of AND is zero
    assert 0x01 == mpu.a
    assert 0x00 == mpu.memory[0x0010]


# BMI


def test_bmi_negative_set_branches_relative_forward():
    mpu = _make_mpu()
    mpu.p |= mpu.NEGATIVE
    # $0000 BMI +06
    _write(mpu.memory, 0x0000, (0x30, 0x06))
    mpu.step()
    assert 0x0002 + 0x06 == mpu.pc


def test_bmi_negative_set_branches_relative_backward():
    mpu = _make_mpu()
    mpu.p |= mpu.NEGATIVE
    mpu.pc = 0x0050
    # $0000 BMI -6
    rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
    _write(mpu.memory, 0x0050, (0x30, rel))
    mpu.step()
    assert 0x0052 - 0x06 == mpu.pc


def test_bmi_negative_clear_does_not_branch():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    # $0000 BEQ +6
    _write(mpu.memory, 0x0000, (0x30, 0x06))
    mpu.step()
    assert 0x0002 == mpu.pc


# BNE


def test_bne_zero_clear_branches_relative_forward():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    # $0000 BNE +6
    _write(mpu.memory, 0x0000, (0xD0, 0x06))
    mpu.step()
    assert 0x0002 + 0x06 == mpu.pc


def test_bne_zero_clear_branches_relative_backward():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.pc = 0x0050
    # $0050 BNE -6
    rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
    _write(mpu.memory, 0x0050, (0xD0, rel))
    mpu.step()
    assert 0x0052 - 0x06 == mpu.pc


def test_bne_zero_set_does_not_branch():
    mpu = _make_mpu()
    mpu.p |= mpu.ZERO
    # $0000 BNE +6
    _write(mpu.memory, 0x0000, (0xD0, 0x06))
    mpu.step()
    assert 0x0002 == mpu.pc


# BPL


def test_bpl_negative_clear_branches_relative_forward():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    # $0000 BPL +06
    _write(mpu.memory, 0x0000, (0x10, 0x06))
    mpu.step()
    assert 0x0002 + 0x06 == mpu.pc


def test_bpl_negative_clear_branches_relative_backward():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.pc = 0x0050
    # $0050 BPL -6
    rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
    _write(mpu.memory, 0x0050, (0x10, rel))
    mpu.step()
    assert 0x0052 - 0x06 == mpu.pc


def test_bpl_negative_set_does_not_branch():
    mpu = _make_mpu()
    mpu.p |= mpu.NEGATIVE
    # $0000 BPL +6
    _write(mpu.memory, 0x0000, (0x10, 0x06))
    mpu.step()
    assert 0x0002 == mpu.pc


# BRK


def test_brk_pushes_pc_plus_2_and_status_then_sets_pc_to_irq_vector():
    mpu = _make_mpu()
    mpu.p = mpu.UNUSED
    _write(mpu.memory, 0xFFFE, (0xCD, 0xAB))
    # $C000 BRK
    mpu.memory[0xC000] = 0x00
    mpu.pc = 0xC000
    mpu.step()
    assert 0xABCD == mpu.pc

    assert 0xC0 == mpu.memory[0x1FF]  # PCH
    assert 0x02 == mpu.memory[0x1FE]  # PCL
    assert mpu.BREAK | mpu.UNUSED == mpu.memory[0x1FD]  # Status
    assert 0xFC == mpu.sp

    assert mpu.BREAK | mpu.UNUSED | mpu.INTERRUPT == mpu.p


# IRQ and NMI handling (very similar to BRK)


def test_irq_pushes_pc_and_correct_status_then_sets_pc_to_irq_vector():
    mpu = _make_mpu()
    mpu.p = mpu.UNUSED
    _write(mpu.memory, 0xFFFA, (0x88, 0x77))
    _write(mpu.memory, 0xFFFE, (0xCD, 0xAB))
    mpu.pc = 0xC123
    mpu.irq()
    assert 0xABCD == mpu.pc
    assert 0xC1 == mpu.memory[0x1FF]  # PCH
    assert 0x23 == mpu.memory[0x1FE]  # PCL
    assert mpu.UNUSED == mpu.memory[0x1FD]  # Status
    assert 0xFC == mpu.sp
    assert mpu.UNUSED | mpu.INTERRUPT == mpu.p
    assert 7 == mpu.processorCycles


def test_nmi_pushes_pc_and_correct_status_then_sets_pc_to_nmi_vector():
    mpu = _make_mpu()
    mpu.p = mpu.UNUSED
    _write(mpu.memory, 0xFFFA, (0x88, 0x77))
    _write(mpu.memory, 0xFFFE, (0xCD, 0xAB))
    mpu.pc = 0xC123
    mpu.nmi()
    assert 0x7788 == mpu.pc
    assert 0xC1 == mpu.memory[0x1FF]  # PCH
    assert 0x23 == mpu.memory[0x1FE]  # PCL
    assert mpu.UNUSED == mpu.memory[0x1FD]  # Status
    assert 0xFC == mpu.sp
    assert mpu.UNUSED | mpu.INTERRUPT == mpu.p
    assert 7 == mpu.processorCycles


# BVC


def test_bvc_overflow_clear_branches_relative_forward():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.OVERFLOW)
    # $0000 BVC +6
    _write(mpu.memory, 0x0000, (0x50, 0x06))
    mpu.step()
    assert 0x0002 + 0x06 == mpu.pc


def test_bvc_overflow_clear_branches_relative_backward():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.OVERFLOW)
    mpu.pc = 0x0050
    rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
    # $0050 BVC -6
    _write(mpu.memory, 0x0050, (0x50, rel))
    mpu.step()
    assert 0x0052 - 0x06 == mpu.pc


def test_bvc_overflow_set_does_not_branch():
    mpu = _make_mpu()
    mpu.p |= mpu.OVERFLOW
    # $0000 BVC +6
    _write(mpu.memory, 0x0000, (0x50, 0x06))
    mpu.step()
    assert 0x0002 == mpu.pc


# BVS


def test_bvs_overflow_set_branches_relative_forward():
    mpu = _make_mpu()
    mpu.p |= mpu.OVERFLOW
    # $0000 BVS +6
    _write(mpu.memory, 0x0000, (0x70, 0x06))
    mpu.step()
    assert 0x0002 + 0x06 == mpu.pc


def test_bvs_overflow_set_branches_relative_backward():
    mpu = _make_mpu()
    mpu.p |= mpu.OVERFLOW
    mpu.pc = 0x0050
    rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
    # $0050 BVS -6
    _write(mpu.memory, 0x0050, (0x70, rel))
    mpu.step()
    assert 0x0052 - 0x06 == mpu.pc


def test_bvs_overflow_clear_does_not_branch():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.OVERFLOW)
    # $0000 BVS +6
    _write(mpu.memory, 0x0000, (0x70, 0x06))
    mpu.step()
    assert 0x0002 == mpu.pc


# CLC


def test_clc_clears_carry_flag():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 CLC
    mpu.memory[0x0000] = 0x18
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0 == mpu.p & mpu.CARRY


# CLD


def test_cld_clears_decimal_flag():
    mpu = _make_mpu()
    mpu.p |= mpu.DECIMAL
    # $0000 CLD
    mpu.memory[0x0000] = 0xD8
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0 == mpu.p & mpu.DECIMAL


# CLI


def test_cli_clears_interrupt_mask_flag():
    mpu = _make_mpu()
    mpu.p |= mpu.INTERRUPT
    # $0000 CLI
    mpu.memory[0x0000] = 0x58
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0 == mpu.p & mpu.INTERRUPT


# CLV


def test_clv_clears_overflow_flag():
    mpu = _make_mpu()
    mpu.p |= mpu.OVERFLOW
    # $0000 CLV
    mpu.memory[0x0000] = 0xB8
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0 == mpu.p & mpu.OVERFLOW


# Compare instructions

# See http://6502.org/tutorials/compare_instructions.html
# and http://www.6502.org/tutorials/compare_beyond.html
# Cheat sheet:
#
#    - Comparison is actually subtraction "register - memory"
#    - Z contains equality result (1 equal, 0 not equal)
#    - C contains result of unsigned comparison (0 if A<m, 1 if A>=m)
#    - N holds MSB of subtraction result (*NOT* of signed subtraction)
#    - V is not affected by comparison
#    - D has no effect on comparison

# CMP Immediate


def test_cmp_imm_sets_zero_carry_clears_neg_flags_if_equal():
    """Comparison: A == m"""
    mpu = _make_mpu()
    # $0000 CMP #10 , A will be 10
    _write(mpu.memory, 0x0000, (0xC9, 10))
    mpu.a = 10
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY


def test_cmp_imm_clears_zero_carry_takes_neg_if_less_unsigned():
    """Comparison: A < m (unsigned)"""
    mpu = _make_mpu()
    # $0000 CMP #10 , A will be 1
    _write(mpu.memory, 0x0000, (0xC9, 10))
    mpu.a = 1
    mpu.step()
    assert 0x0002 == mpu.pc
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE  # 0x01-0x0A=0xF7
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY


def test_cmp_imm_clears_zero_sets_carry_takes_neg_if_less_signed():
    """Comparison: A < #nn (signed), A negative"""
    mpu = _make_mpu()
    # $0000 CMP #1, A will be -1 (0xFF)
    _write(mpu.memory, 0x0000, (0xC9, 1))
    mpu.a = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE  # 0xFF-0x01=0xFE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY  # A>m unsigned


def test_cmp_imm_clears_zero_carry_takes_neg_if_less_signed_nega():
    """Comparison: A < m (signed), A and m both negative"""
    mpu = _make_mpu()
    # $0000 CMP #0xFF (-1), A will be -2 (0xFE)
    _write(mpu.memory, 0x0000, (0xC9, 0xFF))
    mpu.a = 0xFE
    mpu.step()
    assert 0x0002 == mpu.pc
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE  # 0xFE-0xFF=0xFF
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY  # A<m unsigned


def test_cmp_imm_clears_zero_sets_carry_takes_neg_if_more_unsigned():
    """Comparison: A > m (unsigned)"""
    mpu = _make_mpu()
    # $0000 CMP #1 , A will be 10
    _write(mpu.memory, 0x0000, (0xC9, 1))
    mpu.a = 10
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0 == mpu.p & mpu.NEGATIVE  # 0x0A-0x01 = 0x09
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY  # A>m unsigned


def test_cmp_imm_clears_zero_carry_takes_neg_if_more_signed():
    """Comparison: A > m (signed), memory negative"""
    mpu = _make_mpu()
    # $0000 CMP #$FF (-1), A will be 2
    _write(mpu.memory, 0x0000, (0xC9, 0xFF))
    mpu.a = 2
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0 == mpu.p & mpu.NEGATIVE  # 0x02-0xFF=0x01
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY  # A<m unsigned


def test_cmp_imm_clears_zero_carry_takes_neg_if_more_signed_nega():
    """Comparison: A > m (signed), A and m both negative"""
    mpu = _make_mpu()
    # $0000 CMP #$FE (-2), A will be -1 (0xFF)
    _write(mpu.memory, 0x0000, (0xC9, 0xFE))
    mpu.a = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0 == mpu.p & mpu.NEGATIVE  # 0xFF-0xFE=0x01
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY  # A>m unsigned


# CPX Immediate


def test_cpx_imm_sets_zero_carry_clears_neg_flags_if_equal():
    """Comparison: X == m"""
    mpu = _make_mpu()
    # $0000 CPX #$20
    _write(mpu.memory, 0x0000, (0xE0, 0x20))
    mpu.x = 0x20
    mpu.step()
    assert 0x0002 == mpu.pc
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


# CPY Immediate


def test_cpy_imm_sets_zero_carry_clears_neg_flags_if_equal():
    """Comparison: Y == m"""
    mpu = _make_mpu()
    # $0000 CPY #$30
    _write(mpu.memory, 0x0000, (0xC0, 0x30))
    mpu.y = 0x30
    mpu.step()
    assert 0x0002 == mpu.pc
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


# DEC Absolute


def test_dec_abs_decrements_memory():
    mpu = _make_mpu()
    # $0000 DEC 0xABCD
    _write(mpu.memory, 0x0000, (0xCE, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x10
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x0F == mpu.memory[0xABCD]
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_dec_abs_below_00_rolls_over_and_sets_negative_flag():
    mpu = _make_mpu()
    # $0000 DEC 0xABCD
    _write(mpu.memory, 0x0000, (0xCE, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.memory[0xABCD]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_dec_abs_sets_zero_flag_when_decrementing_to_zero():
    mpu = _make_mpu()
    # $0000 DEC 0xABCD
    _write(mpu.memory, 0x0000, (0xCE, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x01
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# DEC Zero Page


def test_dec_zp_decrements_memory():
    mpu = _make_mpu()
    # $0000 DEC 0x0010
    _write(mpu.memory, 0x0000, (0xC6, 0x10))
    mpu.memory[0x0010] = 0x10
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x0F == mpu.memory[0x0010]
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_dec_zp_below_00_rolls_over_and_sets_negative_flag():
    mpu = _make_mpu()
    # $0000 DEC 0x0010
    _write(mpu.memory, 0x0000, (0xC6, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.memory[0x0010]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_dec_zp_sets_zero_flag_when_decrementing_to_zero():
    mpu = _make_mpu()
    # $0000 DEC 0x0010
    _write(mpu.memory, 0x0000, (0xC6, 0x10))
    mpu.memory[0x0010] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# DEC Absolute, X-Indexed


def test_dec_abs_x_decrements_memory():
    mpu = _make_mpu()
    # $0000 DEC 0xABCD,X
    _write(mpu.memory, 0x0000, (0xDE, 0xCD, 0xAB))
    mpu.x = 0x03
    mpu.memory[0xABCD + mpu.x] = 0x10
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x0F == mpu.memory[0xABCD + mpu.x]
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_dec_abs_x_below_00_rolls_over_and_sets_negative_flag():
    mpu = _make_mpu()
    # $0000 DEC 0xABCD,X
    _write(mpu.memory, 0x0000, (0xDE, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.memory[0xABCD + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_dec_abs_x_sets_zero_flag_when_decrementing_to_zero():
    mpu = _make_mpu()
    # $0000 DEC 0xABCD,X
    _write(mpu.memory, 0x0000, (0xDE, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x01
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# DEC Zero Page, X-Indexed


def test_dec_zp_x_decrements_memory():
    mpu = _make_mpu()
    # $0000 DEC 0x0010,X
    _write(mpu.memory, 0x0000, (0xD6, 0x10))
    mpu.x = 0x03
    mpu.memory[0x0010 + mpu.x] = 0x10
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x0F == mpu.memory[0x0010 + mpu.x]
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_dec_zp_x_below_00_rolls_over_and_sets_negative_flag():
    mpu = _make_mpu()
    # $0000 DEC 0x0010,X
    _write(mpu.memory, 0x0000, (0xD6, 0x10))
    mpu.x = 0x03
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.memory[0x0010 + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_dec_zp_x_sets_zero_flag_when_decrementing_to_zero():
    mpu = _make_mpu()
    # $0000 DEC 0x0010,X
    _write(mpu.memory, 0x0000, (0xD6, 0x10))
    mpu.x = 0x03
    mpu.memory[0x0010 + mpu.x] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010 + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# DEX


def test_dex_decrements_x():
    mpu = _make_mpu()
    mpu.x = 0x10
    # $0000 DEX
    mpu.memory[0x0000] = 0xCA
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x0F == mpu.x
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_dex_below_00_rolls_over_and_sets_negative_flag():
    mpu = _make_mpu()
    mpu.x = 0x00
    # $0000 DEX
    mpu.memory[0x0000] = 0xCA
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xFF == mpu.x
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_dex_sets_zero_flag_when_decrementing_to_zero():
    mpu = _make_mpu()
    mpu.x = 0x01
    # $0000 DEX
    mpu.memory[0x0000] = 0xCA
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.x
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# DEY


def test_dey_decrements_y():
    mpu = _make_mpu()
    mpu.y = 0x10
    # $0000 DEY
    mpu.memory[0x0000] = 0x88
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x0F == mpu.y
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_dey_below_00_rolls_over_and_sets_negative_flag():
    mpu = _make_mpu()
    mpu.y = 0x00
    # $0000 DEY
    mpu.memory[0x0000] = 0x88
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xFF == mpu.y
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_dey_sets_zero_flag_when_decrementing_to_zero():
    mpu = _make_mpu()
    mpu.y = 0x01
    # $0000 DEY
    mpu.memory[0x0000] = 0x88
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.y
    assert mpu.ZERO == mpu.p & mpu.ZERO


# EOR Absolute


def test_eor_absolute_flips_bits_over_setting_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    _write(mpu.memory, 0x0000, (0x4D, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert 0xFF == mpu.memory[0xABCD]
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_eor_absolute_flips_bits_over_setting_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    _write(mpu.memory, 0x0000, (0x4D, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.a
    assert 0xFF == mpu.memory[0xABCD]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# EOR Zero Page


def test_eor_zp_flips_bits_over_setting_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    _write(mpu.memory, 0x0000, (0x45, 0x10))
    mpu.memory[0x0010] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0xFF == mpu.memory[0x0010]
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_eor_zp_flips_bits_over_setting_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    _write(mpu.memory, 0x0000, (0x45, 0x10))
    mpu.memory[0x0010] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.a
    assert 0xFF == mpu.memory[0x0010]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# EOR Immediate


def test_eor_immediate_flips_bits_over_setting_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    _write(mpu.memory, 0x0000, (0x49, 0xFF))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_eor_immediate_flips_bits_over_setting_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    _write(mpu.memory, 0x0000, (0x49, 0xFF))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# EOR Absolute, X-Indexed


def test_eor_abs_x_indexed_flips_bits_over_setting_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.x = 0x03
    _write(mpu.memory, 0x0000, (0x5D, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert 0xFF == mpu.memory[0xABCD + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_eor_abs_x_indexed_flips_bits_over_setting_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0x03
    _write(mpu.memory, 0x0000, (0x5D, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.a
    assert 0xFF == mpu.memory[0xABCD + mpu.x]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# EOR Absolute, Y-Indexed


def test_eor_abs_y_indexed_flips_bits_over_setting_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.y = 0x03
    _write(mpu.memory, 0x0000, (0x59, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert 0xFF == mpu.memory[0xABCD + mpu.y]
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_eor_abs_y_indexed_flips_bits_over_setting_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.y = 0x03
    _write(mpu.memory, 0x0000, (0x59, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.a
    assert 0xFF == mpu.memory[0xABCD + mpu.y]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# EOR Indirect, Indexed (X)


def test_eor_ind_indexed_x_flips_bits_over_setting_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.x = 0x03
    _write(mpu.memory, 0x0000, (0x41, 0x10))  # => EOR ($0010,X)
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))  # => Vector to $ABCD
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0xFF == mpu.memory[0xABCD]
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_eor_ind_indexed_x_flips_bits_over_setting_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0x03
    _write(mpu.memory, 0x0000, (0x41, 0x10))  # => EOR ($0010,X)
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))  # => Vector to $ABCD
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.a
    assert 0xFF == mpu.memory[0xABCD]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# EOR Indexed, Indirect (Y)


def test_eor_indexed_ind_y_flips_bits_over_setting_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.y = 0x03
    _write(mpu.memory, 0x0000, (0x51, 0x10))  # => EOR ($0010),Y
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))  # => Vector to $ABCD
    mpu.memory[0xABCD + mpu.y] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0xFF == mpu.memory[0xABCD + mpu.y]
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_eor_indexed_ind_y_flips_bits_over_setting_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.y = 0x03
    _write(mpu.memory, 0x0000, (0x51, 0x10))  # => EOR ($0010),Y
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))  # => Vector to $ABCD
    mpu.memory[0xABCD + mpu.y] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.a
    assert 0xFF == mpu.memory[0xABCD + mpu.y]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# EOR Zero Page, X-Indexed


def test_eor_zp_x_indexed_flips_bits_over_setting_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.x = 0x03
    _write(mpu.memory, 0x0000, (0x55, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert 0xFF == mpu.memory[0x0010 + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_eor_zp_x_indexed_flips_bits_over_setting_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0x03
    _write(mpu.memory, 0x0000, (0x55, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.a
    assert 0xFF == mpu.memory[0x0010 + mpu.x]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# INC Absolute


def test_inc_abs_increments_memory():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x09
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x0A == mpu.memory[0xABCD]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_inc_abs_increments_memory_rolls_over_and_sets_zero_flag():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_inc_abs_sets_negative_flag_when_incrementing_above_7F():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x7F
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.memory[0xABCD]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


# INC Zero Page


def test_inc_zp_increments_memory():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xE6, 0x10))
    mpu.memory[0x0010] = 0x09
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x0A == mpu.memory[0x0010]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_inc_zp_increments_memory_rolls_over_and_sets_zero_flag():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xE6, 0x10))
    mpu.memory[0x0010] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_inc_zp_sets_negative_flag_when_incrementing_above_7F():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xE6, 0x10))
    mpu.memory[0x0010] = 0x7F
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.memory[0x0010]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


# INC Absolute, X-Indexed


def test_inc_abs_x_increments_memory():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
    mpu.x = 0x03
    mpu.memory[0xABCD + mpu.x] = 0x09
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x0A == mpu.memory[0xABCD + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_inc_abs_x_increments_memory_rolls_over_and_sets_zero_flag():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
    mpu.x = 0x03
    mpu.memory[0xABCD + mpu.x] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_inc_abs_x_sets_negative_flag_when_incrementing_above_7F():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
    mpu.x = 0x03
    mpu.memory[0xABCD + mpu.x] = 0x7F
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.memory[0xABCD + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


# INC Zero Page, X-Indexed


def test_inc_zp_x_increments_memory():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xF6, 0x10))
    mpu.x = 0x03
    mpu.memory[0x0010 + mpu.x] = 0x09
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x0A == mpu.memory[0x0010 + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_inc_zp_x_increments_memory_rolls_over_and_sets_zero_flag():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xF6, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010 + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_inc_zp_x_sets_negative_flag_when_incrementing_above_7F():
    mpu = _make_mpu()
    _write(mpu.memory, 0x0000, (0xF6, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x7F
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.memory[0x0010 + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


# INX


def test_inx_increments_x():
    mpu = _make_mpu()
    mpu.x = 0x09
    mpu.memory[0x0000] = 0xE8  # => INX
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x0A == mpu.x
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_inx_above_FF_rolls_over_and_sets_zero_flag():
    mpu = _make_mpu()
    mpu.x = 0xFF
    mpu.memory[0x0000] = 0xE8  # => INX
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.x
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_inx_sets_negative_flag_when_incrementing_above_7F():
    mpu = _make_mpu()
    mpu.x = 0x7F
    mpu.memory[0x0000] = 0xE8  # => INX
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x80 == mpu.x
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


# INY


def test_iny_increments_y():
    mpu = _make_mpu()
    mpu.y = 0x09
    mpu.memory[0x0000] = 0xC8  # => INY
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x0A == mpu.y
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_iny_above_FF_rolls_over_and_sets_zero_flag():
    mpu = _make_mpu()
    mpu.y = 0xFF
    mpu.memory[0x0000] = 0xC8  # => INY
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.y
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_iny_sets_negative_flag_when_incrementing_above_7F():
    mpu = _make_mpu()
    mpu.y = 0x7F
    mpu.memory[0x0000] = 0xC8  # => INY
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x80 == mpu.y
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


# JMP Absolute


def test_jmp_abs_jumps_to_absolute_address():
    mpu = _make_mpu()
    # $0000 JMP $ABCD
    _write(mpu.memory, 0x0000, (0x4C, 0xCD, 0xAB))
    mpu.step()
    assert 0xABCD == mpu.pc


# JMP Indirect


def test_jmp_ind_jumps_to_indirect_address():
    mpu = _make_mpu()
    # $0000 JMP ($ABCD)
    _write(mpu.memory, 0x0000, (0x6C, 0x00, 0x02))
    _write(mpu.memory, 0x0200, (0xCD, 0xAB))
    mpu.step()
    assert 0xABCD == mpu.pc


# JSR


def test_jsr_pushes_pc_plus_2_and_sets_pc():
    mpu = _make_mpu()
    # $C000 JSR $FFD2
    _write(mpu.memory, 0xC000, (0x20, 0xD2, 0xFF))
    mpu.pc = 0xC000
    mpu.step()
    assert 0xFFD2 == mpu.pc
    assert 0xFD == mpu.sp
    assert 0xC0 == mpu.memory[0x01FF]  # PCH
    assert 0x02 == mpu.memory[0x01FE]  # PCL+2


# LDA Absolute


def test_lda_absolute_loads_a_sets_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    # $0000 LDA $ABCD
    _write(mpu.memory, 0x0000, (0xAD, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x80
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_lda_absolute_loads_a_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    # $0000 LDA $ABCD
    _write(mpu.memory, 0x0000, (0xAD, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDA Zero Page


def test_lda_zp_loads_a_sets_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    # $0000 LDA $0010
    _write(mpu.memory, 0x0000, (0xA5, 0x10))
    mpu.memory[0x0010] = 0x80
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_lda_zp_loads_a_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    # $0000 LDA $0010
    _write(mpu.memory, 0x0000, (0xA5, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDA Immediate


def test_lda_immediate_loads_a_sets_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    # $0000 LDA #$80
    _write(mpu.memory, 0x0000, (0xA9, 0x80))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_lda_immediate_loads_a_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    # $0000 LDA #$00
    _write(mpu.memory, 0x0000, (0xA9, 0x00))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDA Absolute, X-Indexed


def test_lda_abs_x_indexed_loads_a_sets_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 LDA $ABCD,X
    _write(mpu.memory, 0x0000, (0xBD, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x80
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_lda_abs_x_indexed_loads_a_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.x = 0x03
    # $0000 LDA $ABCD,X
    _write(mpu.memory, 0x0000, (0xBD, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lda_abs_x_indexed_does_not_page_wrap():
    mpu = _make_mpu()
    mpu.a = 0
    mpu.x = 0xFF
    # $0000 LDA $0080,X
    _write(mpu.memory, 0x0000, (0xBD, 0x80, 0x00))
    mpu.memory[0x0080 + mpu.x] = 0x42
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x42 == mpu.a


# LDA Absolute, Y-Indexed


def test_lda_abs_y_indexed_loads_a_sets_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.y = 0x03
    # $0000 LDA $ABCD,Y
    _write(mpu.memory, 0x0000, (0xB9, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x80
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_lda_abs_y_indexed_loads_a_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.y = 0x03
    # $0000 LDA $ABCD,Y
    _write(mpu.memory, 0x0000, (0xB9, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lda_abs_y_indexed_does_not_page_wrap():
    mpu = _make_mpu()
    mpu.a = 0
    mpu.y = 0xFF
    # $0000 LDA $0080,X
    _write(mpu.memory, 0x0000, (0xB9, 0x80, 0x00))
    mpu.memory[0x0080 + mpu.y] = 0x42
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x42 == mpu.a


# LDA Indirect, Indexed (X)


def test_lda_ind_indexed_x_loads_a_sets_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 LDA ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0xA1, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x80
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_lda_ind_indexed_x_loads_a_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 LDA ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0xA1, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDA Indexed, Indirect (Y)


def test_lda_indexed_ind_y_loads_a_sets_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.y = 0x03
    # $0000 LDA ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0xB1, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x80
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_lda_indexed_ind_y_loads_a_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.y = 0x03
    # $0000 LDA ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0xB1, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDA Zero Page, X-Indexed


def test_lda_zp_x_indexed_loads_a_sets_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 LDA $10,X
    _write(mpu.memory, 0x0000, (0xB5, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x80
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_lda_zp_x_indexed_loads_a_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.x = 0x03
    # $0000 LDA $10,X
    _write(mpu.memory, 0x0000, (0xB5, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDX Absolute


def test_ldx_absolute_loads_x_sets_n_flag():
    mpu = _make_mpu()
    mpu.x = 0x00
    # $0000 LDX $ABCD
    _write(mpu.memory, 0x0000, (0xAE, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x80
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.x
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_ldx_absolute_loads_x_sets_z_flag():
    mpu = _make_mpu()
    mpu.x = 0xFF
    # $0000 LDX $ABCD
    _write(mpu.memory, 0x0000, (0xAE, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.x
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDX Zero Page


def test_ldx_zp_loads_x_sets_n_flag():
    mpu = _make_mpu()
    mpu.x = 0x00
    # $0000 LDX $0010
    _write(mpu.memory, 0x0000, (0xA6, 0x10))
    mpu.memory[0x0010] = 0x80
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.x
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_ldx_zp_loads_x_sets_z_flag():
    mpu = _make_mpu()
    mpu.x = 0xFF
    # $0000 LDX $0010
    _write(mpu.memory, 0x0000, (0xA6, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.x
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDX Immediate


def test_ldx_immediate_loads_x_sets_n_flag():
    mpu = _make_mpu()
    mpu.x = 0x00
    # $0000 LDX #$80
    _write(mpu.memory, 0x0000, (0xA2, 0x80))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.x
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_ldx_immediate_loads_x_sets_z_flag():
    mpu = _make_mpu()
    mpu.x = 0xFF
    # $0000 LDX #$00
    _write(mpu.memory, 0x0000, (0xA2, 0x00))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.x
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDX Absolute, Y-Indexed


def test_ldx_abs_y_indexed_loads_x_sets_n_flag():
    mpu = _make_mpu()
    mpu.x = 0x00
    mpu.y = 0x03
    # $0000 LDX $ABCD,Y
    _write(mpu.memory, 0x0000, (0xBE, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x80
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.x
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_ldx_abs_y_indexed_loads_x_sets_z_flag():
    mpu = _make_mpu()
    mpu.x = 0xFF
    mpu.y = 0x03
    # $0000 LDX $ABCD,Y
    _write(mpu.memory, 0x0000, (0xBE, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.x
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDX Zero Page, Y-Indexed


def test_ldx_zp_y_indexed_loads_x_sets_n_flag():
    mpu = _make_mpu()
    mpu.x = 0x00
    mpu.y = 0x03
    # $0000 LDX $0010,Y
    _write(mpu.memory, 0x0000, (0xB6, 0x10))
    mpu.memory[0x0010 + mpu.y] = 0x80
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.x
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_ldx_zp_y_indexed_loads_x_sets_z_flag():
    mpu = _make_mpu()
    mpu.x = 0xFF
    mpu.y = 0x03
    # $0000 LDX $0010,Y
    _write(mpu.memory, 0x0000, (0xB6, 0x10))
    mpu.memory[0x0010 + mpu.y] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.x
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDY Absolute


def test_ldy_absolute_loads_y_sets_n_flag():
    mpu = _make_mpu()
    mpu.y = 0x00
    # $0000 LDY $ABCD
    _write(mpu.memory, 0x0000, (0xAC, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x80
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.y
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_ldy_absolute_loads_y_sets_z_flag():
    mpu = _make_mpu()
    mpu.y = 0xFF
    # $0000 LDY $ABCD
    _write(mpu.memory, 0x0000, (0xAC, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.y
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDY Zero Page


def test_ldy_zp_loads_y_sets_n_flag():
    mpu = _make_mpu()
    mpu.y = 0x00
    # $0000 LDY $0010
    _write(mpu.memory, 0x0000, (0xA4, 0x10))
    mpu.memory[0x0010] = 0x80
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.y
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_ldy_zp_loads_y_sets_z_flag():
    mpu = _make_mpu()
    mpu.y = 0xFF
    # $0000 LDY $0010
    _write(mpu.memory, 0x0000, (0xA4, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.y
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDY Immediate


def test_ldy_immediate_loads_y_sets_n_flag():
    mpu = _make_mpu()
    mpu.y = 0x00
    # $0000 LDY #$80
    _write(mpu.memory, 0x0000, (0xA0, 0x80))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.y
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_ldy_immediate_loads_y_sets_z_flag():
    mpu = _make_mpu()
    mpu.y = 0xFF
    # $0000 LDY #$00
    _write(mpu.memory, 0x0000, (0xA0, 0x00))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.y
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDY Absolute, X-Indexed


def test_ldy_abs_x_indexed_loads_x_sets_n_flag():
    mpu = _make_mpu()
    mpu.y = 0x00
    mpu.x = 0x03
    # $0000 LDY $ABCD,X
    _write(mpu.memory, 0x0000, (0xBC, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x80
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.y
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_ldy_abs_x_indexed_loads_x_sets_z_flag():
    mpu = _make_mpu()
    mpu.y = 0xFF
    mpu.x = 0x03
    # $0000 LDY $ABCD,X
    _write(mpu.memory, 0x0000, (0xBC, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.y
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LDY Zero Page, X-Indexed


def test_ldy_zp_x_indexed_loads_x_sets_n_flag():
    mpu = _make_mpu()
    mpu.y = 0x00
    mpu.x = 0x03
    # $0000 LDY $0010,X
    _write(mpu.memory, 0x0000, (0xB4, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x80
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.y
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_ldy_zp_x_indexed_loads_x_sets_z_flag():
    mpu = _make_mpu()
    mpu.y = 0xFF
    mpu.x = 0x03
    # $0000 LDY $0010,X
    _write(mpu.memory, 0x0000, (0xB4, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.y
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


# LSR Accumulator


def test_lsr_accumulator_rotates_in_zero_not_carry():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 LSR A
    mpu.memory[0x0000] = 0x4A
    mpu.a = 0x00
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lsr_accumulator_sets_carry_and_zero_flags_after_rotation():
    mpu = _make_mpu()
    mpu.p &= ~mpu.CARRY
    # $0000 LSR A
    mpu.memory[0x0000] = 0x4A
    mpu.a = 0x01
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lsr_accumulator_rotates_bits_right():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 LSR A
    mpu.memory[0x0000] = 0x4A
    mpu.a = 0x04
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x02 == mpu.a
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


# LSR Absolute


def test_lsr_absolute_rotates_in_zero_not_carry():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 LSR $ABCD
    _write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lsr_absolute_sets_carry_and_zero_flags_after_rotation():
    mpu = _make_mpu()
    mpu.p &= ~mpu.CARRY
    # $0000 LSR $ABCD
    _write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x01
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lsr_absolute_rotates_bits_right():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 LSR $ABCD
    _write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x04
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x02 == mpu.memory[0xABCD]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


# LSR Zero Page


def test_lsr_zp_rotates_in_zero_not_carry():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 LSR $0010
    _write(mpu.memory, 0x0000, (0x46, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lsr_zp_sets_carry_and_zero_flags_after_rotation():
    mpu = _make_mpu()
    mpu.p &= ~mpu.CARRY
    # $0000 LSR $0010
    _write(mpu.memory, 0x0000, (0x46, 0x10))
    mpu.memory[0x0010] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lsr_zp_rotates_bits_right():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 LSR $0010
    _write(mpu.memory, 0x0000, (0x46, 0x10))
    mpu.memory[0x0010] = 0x04
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x02 == mpu.memory[0x0010]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


# LSR Absolute, X-Indexed


def test_lsr_abs_x_indexed_rotates_in_zero_not_carry():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    mpu.x = 0x03
    # $0000 LSR $ABCD,X
    _write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lsr_abs_x_indexed_sets_c_and_z_flags_after_rotation():
    mpu = _make_mpu()
    mpu.p &= ~mpu.CARRY
    mpu.x = 0x03
    # $0000 LSR $ABCD,X
    _write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x01
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lsr_abs_x_indexed_rotates_bits_right():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 LSR $ABCD,X
    _write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x04
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x02 == mpu.memory[0xABCD + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


# LSR Zero Page, X-Indexed


def test_lsr_zp_x_indexed_rotates_in_zero_not_carry():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    mpu.x = 0x03
    # $0000 LSR $0010,X
    _write(mpu.memory, 0x0000, (0x56, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010 + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lsr_zp_x_indexed_sets_carry_and_zero_flags_after_rotation():
    mpu = _make_mpu()
    mpu.p &= ~mpu.CARRY
    mpu.x = 0x03
    # $0000 LSR $0010,X
    _write(mpu.memory, 0x0000, (0x56, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x01
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010 + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


def test_lsr_zp_x_indexed_rotates_bits_right():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    mpu.x = 0x03
    # $0000 LSR $0010,X
    _write(mpu.memory, 0x0000, (0x56, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x04
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x02 == mpu.memory[0x0010 + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY
    assert 0 == mpu.p & mpu.NEGATIVE


# NOP


def test_nop_does_nothing():
    mpu = _make_mpu()
    # $0000 NOP
    mpu.memory[0x0000] = 0xEA
    mpu.step()
    assert 0x0001 == mpu.pc


# ORA Absolute


def test_ora_absolute_zeroes_or_zeros_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.a = 0x00
    # $0000 ORA $ABCD
    _write(mpu.memory, 0x0000, (0x0D, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_ora_absolute_turns_bits_on_sets_n_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.a = 0x03
    # $0000 ORA $ABCD
    _write(mpu.memory, 0x0000, (0x0D, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x82
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x83 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# ORA Zero Page


def test_ora_zp_zeroes_or_zeros_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.a = 0x00
    # $0000 ORA $0010
    _write(mpu.memory, 0x0000, (0x05, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_ora_zp_turns_bits_on_sets_n_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.a = 0x03
    # $0000 ORA $0010
    _write(mpu.memory, 0x0000, (0x05, 0x10))
    mpu.memory[0x0010] = 0x82
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x83 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# ORA Immediate


def test_ora_immediate_zeroes_or_zeros_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.a = 0x00
    # $0000 ORA #$00
    _write(mpu.memory, 0x0000, (0x09, 0x00))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_ora_immediate_turns_bits_on_sets_n_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.a = 0x03
    # $0000 ORA #$82
    _write(mpu.memory, 0x0000, (0x09, 0x82))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x83 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# ORA Absolute, X


def test_ora_abs_x_indexed_zeroes_or_zeros_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 ORA $ABCD,X
    _write(mpu.memory, 0x0000, (0x1D, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_ora_abs_x_indexed_turns_bits_on_sets_n_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.a = 0x03
    mpu.x = 0x03
    # $0000 ORA $ABCD,X
    _write(mpu.memory, 0x0000, (0x1D, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x82
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x83 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# ORA Absolute, Y


def test_ora_abs_y_indexed_zeroes_or_zeros_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.y = 0x03
    # $0000 ORA $ABCD,Y
    _write(mpu.memory, 0x0000, (0x19, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_ora_abs_y_indexed_turns_bits_on_sets_n_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.a = 0x03
    mpu.y = 0x03
    # $0000 ORA $ABCD,Y
    _write(mpu.memory, 0x0000, (0x19, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x82
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x83 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# ORA Indirect, Indexed (X)


def test_ora_ind_indexed_x_zeroes_or_zeros_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 ORA ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x01, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_ora_ind_indexed_x_turns_bits_on_sets_n_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.a = 0x03
    mpu.x = 0x03
    # $0000 ORA ($0010,X)
    # $0013 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x01, 0x10))
    _write(mpu.memory, 0x0013, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x82
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x83 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# ORA Indexed, Indirect (Y)


def test_ora_indexed_ind_y_zeroes_or_zeros_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.y = 0x03
    # $0000 ORA ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x11, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_ora_indexed_ind_y_turns_bits_on_sets_n_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.a = 0x03
    mpu.y = 0x03
    # $0000 ORA ($0010),Y
    # $0010 Vector to $ABCD
    _write(mpu.memory, 0x0000, (0x11, 0x10))
    _write(mpu.memory, 0x0010, (0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x82
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x83 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# ORA Zero Page, X


def test_ora_zp_x_indexed_zeroes_or_zeros_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 ORA $0010,X
    _write(mpu.memory, 0x0000, (0x15, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_ora_zp_x_indexed_turns_bits_on_sets_n_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.a = 0x03
    mpu.x = 0x03
    # $0000 ORA $0010,X
    _write(mpu.memory, 0x0000, (0x15, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x82
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x83 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


# PHA


def test_pha_pushes_a_and_updates_sp():
    mpu = _make_mpu()
    mpu.a = 0xAB
    # $0000 PHA
    mpu.memory[0x0000] = 0x48
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xAB == mpu.a
    assert 0xAB == mpu.memory[0x01FF]
    assert 0xFE == mpu.sp


# PHP


def test_php_pushes_processor_status_and_updates_sp():
    for flags in range(0x100):
        mpu = _make_mpu()
        mpu.p = flags | mpu.BREAK | mpu.UNUSED
        # $0000 PHP
        mpu.memory[0x0000] = 0x08
        mpu.step()
        assert 0x0001 == mpu.pc
        assert (flags | mpu.BREAK | mpu.UNUSED) == mpu.memory[0x1FF]
        assert 0xFE == mpu.sp


# PLA


def test_pla_pulls_top_byte_from_stack_into_a_and_updates_sp():
    mpu = _make_mpu()
    # $0000 PLA
    mpu.memory[0x0000] = 0x68
    mpu.memory[0x01FF] = 0xAB
    mpu.sp = 0xFE
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xAB == mpu.a
    assert 0xFF == mpu.sp


# PLP


def test_plp_pulls_top_byte_from_stack_into_flags_and_updates_sp():
    mpu = _make_mpu()
    # $0000 PLP
    mpu.memory[0x0000] = 0x28
    mpu.memory[0x01FF] = 0xBA  # must have BREAK and UNUSED set
    mpu.sp = 0xFE
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xBA == mpu.p
    assert 0xFF == mpu.sp


# ROL Accumulator


def test_rol_accumulator_zero_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL A
    mpu.memory[0x0000] = 0x2A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_accumulator_80_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0x80
    mpu.p &= ~(mpu.CARRY)
    mpu.p &= ~(mpu.ZERO)
    # $0000 ROL A
    mpu.memory[0x0000] = 0x2A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_accumulator_zero_and_carry_one_clears_z_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.p |= mpu.CARRY
    # $0000 ROL A
    mpu.memory[0x0000] = 0x2A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x01 == mpu.a
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_accumulator_sets_n_flag():
    mpu = _make_mpu()
    mpu.a = 0x40
    mpu.p |= mpu.CARRY
    # $0000 ROL A
    mpu.memory[0x0000] = 0x2A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x81 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_rol_accumulator_shifts_out_zero():
    mpu = _make_mpu()
    mpu.a = 0x7F
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL A
    mpu.memory[0x0000] = 0x2A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xFE == mpu.a
    assert 0 == mpu.p & mpu.CARRY


def test_rol_accumulator_shifts_out_one():
    mpu = _make_mpu()
    mpu.a = 0xFF
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL A
    mpu.memory[0x0000] = 0x2A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xFE == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ROL Absolute


def test_rol_absolute_zero_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL $ABCD
    _write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_absolute_80_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.p &= ~(mpu.ZERO)
    # $0000 ROL $ABCD
    _write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x80
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_absolute_zero_and_carry_one_clears_z_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.p |= mpu.CARRY
    # $0000 ROL $ABCD
    _write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x01 == mpu.memory[0xABCD]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_absolute_sets_n_flag():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 ROL $ABCD
    _write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x40
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x81 == mpu.memory[0xABCD]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_rol_absolute_shifts_out_zero():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL $ABCD
    _write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x7F
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFE == mpu.memory[0xABCD]
    assert 0 == mpu.p & mpu.CARRY


def test_rol_absolute_shifts_out_one():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL $ABCD
    _write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFE == mpu.memory[0xABCD]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ROL Zero Page


def test_rol_zp_zero_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL $0010
    _write(mpu.memory, 0x0000, (0x26, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_zp_80_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.p &= ~(mpu.ZERO)
    # $0000 ROL $0010
    _write(mpu.memory, 0x0000, (0x26, 0x10))
    mpu.memory[0x0010] = 0x80
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_zp_zero_and_carry_one_clears_z_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.p |= mpu.CARRY
    # $0000 ROL $0010
    _write(mpu.memory, 0x0000, (0x26, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.memory[0x0010]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_zp_sets_n_flag():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 ROL $0010
    _write(mpu.memory, 0x0000, (0x26, 0x10))
    mpu.memory[0x0010] = 0x40
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x81 == mpu.memory[0x0010]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_rol_zp_shifts_out_zero():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL $0010
    _write(mpu.memory, 0x0000, (0x26, 0x10))
    mpu.memory[0x0010] = 0x7F
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFE == mpu.memory[0x0010]
    assert 0 == mpu.p & mpu.CARRY


def test_rol_zp_shifts_out_one():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL $0010
    _write(mpu.memory, 0x0000, (0x26, 0x10))
    mpu.memory[0x0010] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFE == mpu.memory[0x0010]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ROL Absolute, X-Indexed


def test_rol_abs_x_indexed_zero_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.x = 0x03
    # $0000 ROL $ABCD,X
    _write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_abs_x_indexed_80_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.p &= ~(mpu.ZERO)
    mpu.x = 0x03
    # $0000 ROL $ABCD,X
    _write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x80
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_abs_x_indexed_zero_and_carry_one_clears_z_flag():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ROL $ABCD,X
    _write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x01 == mpu.memory[0xABCD + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_abs_x_indexed_sets_n_flag():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ROL $ABCD,X
    _write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x40
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x81 == mpu.memory[0xABCD + mpu.x]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_rol_abs_x_indexed_shifts_out_zero():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL $ABCD,X
    _write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x7F
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFE == mpu.memory[0xABCD + mpu.x]
    assert 0 == mpu.p & mpu.CARRY


def test_rol_abs_x_indexed_shifts_out_one():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL $ABCD,X
    _write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFE == mpu.memory[0xABCD + mpu.x]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ROL Zero Page, X-Indexed
def test_rol_zp_x_indexed_zero_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.x = 0x03
    _write(mpu.memory, 0x0000, (0x36, 0x10))
    # $0000 ROL $0010,X
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010 + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_zp_x_indexed_80_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    mpu.p &= ~(mpu.ZERO)
    mpu.x = 0x03
    _write(mpu.memory, 0x0000, (0x36, 0x10))
    # $0000 ROL $0010,X
    mpu.memory[0x0010 + mpu.x] = 0x80
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010 + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_zp_x_indexed_zero_and_carry_one_clears_z_flag():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    _write(mpu.memory, 0x0000, (0x36, 0x10))
    # $0000 ROL $0010,X
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x01 == mpu.memory[0x0010 + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_rol_zp_x_indexed_sets_n_flag():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ROL $0010,X
    _write(mpu.memory, 0x0000, (0x36, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x40
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x81 == mpu.memory[0x0010 + mpu.x]
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO


def test_rol_zp_x_indexed_shifts_out_zero():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL $0010,X
    _write(mpu.memory, 0x0000, (0x36, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x7F
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFE == mpu.memory[0x0010 + mpu.x]
    assert 0 == mpu.p & mpu.CARRY


def test_rol_zp_x_indexed_shifts_out_one():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROL $0010,X
    _write(mpu.memory, 0x0000, (0x36, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFE == mpu.memory[0x0010 + mpu.x]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ROR Accumulator


def test_ror_accumulator_zero_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROR A
    mpu.memory[0x0000] = 0x6A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.a
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_ror_accumulator_zero_and_carry_one_rotates_in_sets_n_flags():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.p |= mpu.CARRY
    # $0000 ROR A
    mpu.memory[0x0000] = 0x6A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x80 == mpu.a
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_ror_accumulator_shifts_out_zero():
    mpu = _make_mpu()
    mpu.a = 0x02
    mpu.p |= mpu.CARRY
    # $0000 ROR A
    mpu.memory[0x0000] = 0x6A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x81 == mpu.a
    assert 0 == mpu.p & mpu.CARRY


def test_ror_accumulator_shifts_out_one():
    mpu = _make_mpu()
    mpu.a = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ROR A
    mpu.memory[0x0000] = 0x6A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x81 == mpu.a
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ROR Absolute


def test_ror_absolute_zero_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROR $ABCD
    _write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_ror_absolute_zero_and_carry_one_rotates_in_sets_n_flags():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 ROR $ABCD
    _write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.memory[0xABCD]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_ror_absolute_shifts_out_zero():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 ROR $ABCD
    _write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x02
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x81 == mpu.memory[0xABCD]
    assert 0 == mpu.p & mpu.CARRY


def test_ror_absolute_shifts_out_one():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 ROR $ABCD
    _write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x03
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x81 == mpu.memory[0xABCD]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ROR Zero Page


def test_ror_zp_zero_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROR $0010
    _write(mpu.memory, 0x0000, (0x66, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_ror_zp_zero_and_carry_one_rotates_in_sets_n_flags():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 ROR $0010
    _write(mpu.memory, 0x0000, (0x66, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.memory[0x0010]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_ror_zp_zero_absolute_shifts_out_zero():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 ROR $0010
    _write(mpu.memory, 0x0000, (0x66, 0x10))
    mpu.memory[0x0010] = 0x02
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x81 == mpu.memory[0x0010]
    assert 0 == mpu.p & mpu.CARRY


def test_ror_zp_shifts_out_one():
    mpu = _make_mpu()
    mpu.p |= mpu.CARRY
    # $0000 ROR $0010
    _write(mpu.memory, 0x0000, (0x66, 0x10))
    mpu.memory[0x0010] = 0x03
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x81 == mpu.memory[0x0010]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ROR Absolute, X-Indexed


def test_ror_abs_x_indexed_zero_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROR $ABCD,X
    _write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_ror_abs_x_indexed_z_and_c_1_rotates_in_sets_n_flags():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ROR $ABCD,X
    _write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x80 == mpu.memory[0xABCD + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_ror_abs_x_indexed_shifts_out_zero():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ROR $ABCD,X
    _write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x02
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x81 == mpu.memory[0xABCD + mpu.x]
    assert 0 == mpu.p & mpu.CARRY


def test_ror_abs_x_indexed_shifts_out_one():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ROR $ABCD,X
    _write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x03
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x81 == mpu.memory[0xABCD + mpu.x]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# ROR Zero Page, X-Indexed


def test_ror_zp_x_indexed_zero_and_carry_zero_sets_z_flag():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p &= ~(mpu.CARRY)
    # $0000 ROR $0010,X
    _write(mpu.memory, 0x0000, (0x76, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010 + mpu.x]
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.NEGATIVE


def test_ror_zp_x_indexed_zero_and_carry_one_rotates_in_sets_n_flags():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ROR $0010,X
    _write(mpu.memory, 0x0000, (0x76, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x80 == mpu.memory[0x0010 + mpu.x]
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_ror_zp_x_indexed_zero_absolute_shifts_out_zero():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ROR $0010,X
    _write(mpu.memory, 0x0000, (0x76, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x02
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x81 == mpu.memory[0x0010 + mpu.x]
    assert 0 == mpu.p & mpu.CARRY


def test_ror_zp_x_indexed_shifts_out_one():
    mpu = _make_mpu()
    mpu.x = 0x03
    mpu.p |= mpu.CARRY
    # $0000 ROR $0010,X
    _write(mpu.memory, 0x0000, (0x76, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x03
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x81 == mpu.memory[0x0010 + mpu.x]
    assert mpu.CARRY == mpu.p & mpu.CARRY


# RTI


def test_rti_restores_status_and_pc_and_updates_sp():
    mpu = _make_mpu()
    # $0000 RTI
    mpu.memory[0x0000] = 0x40
    _write(mpu.memory, 0x01FD, (0xFC, 0x03, 0xC0))  # Status, PCL, PCH
    mpu.sp = 0xFC

    mpu.step()
    assert 0xC003 == mpu.pc
    assert 0xFC == mpu.p
    assert 0xFF == mpu.sp


def test_rti_forces_break_and_unused_flags_high():
    mpu = _make_mpu()
    # $0000 RTI
    mpu.memory[0x0000] = 0x40
    _write(mpu.memory, 0x01FD, (0x00, 0x03, 0xC0))  # Status, PCL, PCH
    mpu.sp = 0xFC

    mpu.step()
    assert mpu.BREAK == mpu.p & mpu.BREAK
    assert mpu.UNUSED == mpu.p & mpu.UNUSED


# RTS


def test_rts_restores_pc_and_increments_then_updates_sp():
    mpu = _make_mpu()
    # $0000 RTS
    mpu.memory[0x0000] = 0x60
    _write(mpu.memory, 0x01FE, (0x03, 0xC0))  # PCL, PCH
    mpu.pc = 0x0000
    mpu.sp = 0xFD

    mpu.step()
    assert 0xC004 == mpu.pc
    assert 0xFF == mpu.sp


def test_rts_wraps_around_top_of_memory():
    mpu = _make_mpu()
    # $1000 RTS
    mpu.memory[0x1000] = 0x60
    _write(mpu.memory, 0x01FE, (0xFF, 0xFF))  # PCL, PCH
    mpu.pc = 0x1000
    mpu.sp = 0xFD

    mpu.step()
    assert 0x0000 == mpu.pc
    assert 0xFF == mpu.sp


# SBC Absolute


def test_sbc_abs_all_zeros_and_no_borrow_is_zero():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x00
    # $0000 SBC $ABCD
    _write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_abs_downto_zero_no_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x01
    # $0000 SBC $ABCD
    _write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x01
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_abs_downto_zero_with_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x01
    # $0000 SBC $ABCD
    _write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_abs_downto_four_with_borrow_clears_z_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x07
    # $0000 SBC $ABCD
    _write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x02
    mpu.step()
    assert 0x04 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.CARRY


# SBC Zero Page


def test_sbc_zp_all_zeros_and_no_borrow_is_zero():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x00
    # $0000 SBC $10
    _write(mpu.memory, 0x0000, (0xE5, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_zp_downto_zero_no_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x01
    # $0000 SBC $10
    _write(mpu.memory, 0x0000, (0xE5, 0x10))
    mpu.memory[0x0010] = 0x01
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_zp_downto_zero_with_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x01
    # => SBC $10
    _write(mpu.memory, 0x0000, (0xE5, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_zp_downto_four_with_borrow_clears_z_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x07
    # => SBC $10
    _write(mpu.memory, 0x0000, (0xE5, 0x10))
    mpu.memory[0x0010] = 0x02
    mpu.step()
    assert 0x04 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.CARRY


# SBC Immediate


def test_sbc_imm_all_zeros_and_no_borrow_is_zero():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x00
    # $0000 SBC #$00
    _write(mpu.memory, 0x0000, (0xE9, 0x00))
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_imm_downto_zero_no_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x01
    # $0000 SBC #$01
    _write(mpu.memory, 0x0000, (0xE9, 0x01))
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_imm_downto_zero_with_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x01
    # $0000 SBC #$00
    _write(mpu.memory, 0x0000, (0xE9, 0x00))
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_imm_downto_four_with_borrow_clears_z_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x07
    # $0000 SBC #$02
    _write(mpu.memory, 0x0000, (0xE9, 0x02))
    mpu.step()
    assert 0x04 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.CARRY


def test_sbc_bcd_on_immediate_0a_minus_00_carry_set():
    mpu = _make_mpu()
    mpu.p |= mpu.DECIMAL
    mpu.p |= mpu.CARRY
    mpu.a = 0x0A
    # $0000 SBC #$00
    _write(mpu.memory, 0x0000, (0xE9, 0x00))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x0A == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY


def test_sbc_bcd_on_immediate_9a_minus_00_carry_set():
    mpu = _make_mpu()
    mpu.p |= mpu.DECIMAL
    mpu.p |= mpu.CARRY
    mpu.a = 0x9A
    # $0000 SBC #$00
    _write(mpu.memory, 0x0000, (0xE9, 0x00))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x9A == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY


def test_sbc_bcd_on_immediate_00_minus_01_carry_set():
    mpu = _make_mpu()
    mpu.p |= mpu.DECIMAL
    mpu.p |= mpu.OVERFLOW
    mpu.p |= mpu.ZERO
    mpu.p |= mpu.CARRY
    mpu.a = 0x00
    # => $0000 SBC #$00
    _write(mpu.memory, 0x0000, (0xE9, 0x01))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x99 == mpu.a
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO
    assert 0 == mpu.p & mpu.CARRY


def test_sbc_bcd_on_immediate_20_minus_0a_carry_unset():
    mpu = _make_mpu()
    mpu.p |= mpu.DECIMAL
    mpu.a = 0x20
    # $0000 SBC #$00
    _write(mpu.memory, 0x0000, (0xE9, 0x0A))
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x1F == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.OVERFLOW
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.p & mpu.CARRY


# SBC Absolute, X-Indexed


def test_sbc_abs_x_all_zeros_and_no_borrow_is_zero():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x00
    # $0000 SBC $FEE0,X
    _write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
    mpu.x = 0x0D
    mpu.memory[0xFEED] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_abs_x_downto_zero_no_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x01
    # $0000 SBC $FEE0,X
    _write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
    mpu.x = 0x0D
    mpu.memory[0xFEED] = 0x01
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_abs_x_downto_zero_with_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x01
    # $0000 SBC $FEE0,X
    _write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
    mpu.x = 0x0D
    mpu.memory[0xFEED] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_abs_x_downto_four_with_borrow_clears_z_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x07
    # $0000 SBC $FEE0,X
    _write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
    mpu.x = 0x0D
    mpu.memory[0xFEED] = 0x02
    mpu.step()
    assert 0x04 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.CARRY


# SBC Absolute, Y-Indexed


def test_sbc_abs_y_all_zeros_and_no_borrow_is_zero():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x00
    # $0000 SBC $FEE0,Y
    _write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
    mpu.y = 0x0D
    mpu.memory[0xFEED] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_abs_y_downto_zero_no_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x01
    # $0000 SBC $FEE0,Y
    _write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
    mpu.y = 0x0D
    mpu.memory[0xFEED] = 0x01
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_abs_y_downto_zero_with_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x01
    # $0000 SBC $FEE0,Y
    _write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
    mpu.y = 0x0D
    mpu.memory[0xFEED] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_abs_y_downto_four_with_borrow_clears_z_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x07
    # $0000 SBC $FEE0,Y
    _write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
    mpu.y = 0x0D
    mpu.memory[0xFEED] = 0x02
    mpu.step()
    assert 0x04 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.CARRY


# SBC Indirect, Indexed (X)


def test_sbc_ind_x_all_zeros_and_no_borrow_is_zero():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x00
    # $0000 SBC ($10,X)
    # $0013 Vector to $FEED
    _write(mpu.memory, 0x0000, (0xE1, 0x10))
    _write(mpu.memory, 0x0013, (0xED, 0xFE))
    mpu.x = 0x03
    mpu.memory[0xFEED] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_ind_x_downto_zero_no_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x01
    # $0000 SBC ($10,X)
    # $0013 Vector to $FEED
    _write(mpu.memory, 0x0000, (0xE1, 0x10))
    _write(mpu.memory, 0x0013, (0xED, 0xFE))
    mpu.x = 0x03
    mpu.memory[0xFEED] = 0x01
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_ind_x_downto_zero_with_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x01
    # $0000 SBC ($10,X)
    # $0013 Vector to $FEED
    _write(mpu.memory, 0x0000, (0xE1, 0x10))
    _write(mpu.memory, 0x0013, (0xED, 0xFE))
    mpu.x = 0x03
    mpu.memory[0xFEED] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_ind_x_downto_four_with_borrow_clears_z_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x07
    # $0000 SBC ($10,X)
    # $0013 Vector to $FEED
    _write(mpu.memory, 0x0000, (0xE1, 0x10))
    _write(mpu.memory, 0x0013, (0xED, 0xFE))
    mpu.x = 0x03
    mpu.memory[0xFEED] = 0x02
    mpu.step()
    assert 0x04 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.CARRY


# SBC Indexed, Indirect (Y)


def test_sbc_ind_y_all_zeros_and_no_borrow_is_zero():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x00
    mpu.y = 0x03
    # $0000 SBC ($10),Y
    # $0010 Vector to $FEED
    _write(mpu.memory, 0x0000, (0xF1, 0x10))
    _write(mpu.memory, 0x0010, (0xED, 0xFE))
    mpu.memory[0xFEED + mpu.y] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_ind_y_downto_zero_no_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x01
    # $0000 SBC ($10),Y
    # $0010 Vector to $FEED
    _write(mpu.memory, 0x0000, (0xF1, 0x10))
    _write(mpu.memory, 0x0010, (0xED, 0xFE))
    mpu.memory[0xFEED + mpu.y] = 0x01
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_ind_y_downto_zero_with_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x01
    # $0000 SBC ($10),Y
    # $0010 Vector to $FEED
    _write(mpu.memory, 0x0000, (0xF1, 0x10))
    _write(mpu.memory, 0x0010, (0xED, 0xFE))
    mpu.memory[0xFEED + mpu.y] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_ind_y_downto_four_with_borrow_clears_z_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x07
    # $0000 SBC ($10),Y
    # $0010 Vector to $FEED
    _write(mpu.memory, 0x0000, (0xF1, 0x10))
    _write(mpu.memory, 0x0010, (0xED, 0xFE))
    mpu.memory[0xFEED + mpu.y] = 0x02
    mpu.step()
    assert 0x04 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.CARRY


# SBC Zero Page, X-Indexed


def test_sbc_zp_x_all_zeros_and_no_borrow_is_zero():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x00
    # $0000 SBC $10,X
    _write(mpu.memory, 0x0000, (0xF5, 0x10))
    mpu.x = 0x0D
    mpu.memory[0x001D] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_zp_x_downto_zero_no_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p |= mpu.CARRY  # borrow = 0
    mpu.a = 0x01
    # $0000 SBC $10,X
    _write(mpu.memory, 0x0000, (0xF5, 0x10))
    mpu.x = 0x0D
    mpu.memory[0x001D] = 0x01
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_zp_x_downto_zero_with_borrow_sets_z_clears_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x01
    # $0000 SBC $10,X
    _write(mpu.memory, 0x0000, (0xF5, 0x10))
    mpu.x = 0x0D
    mpu.memory[0x001D] = 0x00
    mpu.step()
    assert 0x00 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert mpu.CARRY == mpu.CARRY
    assert mpu.ZERO == mpu.p & mpu.ZERO


def test_sbc_zp_x_downto_four_with_borrow_clears_z_n():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    mpu.p &= ~(mpu.CARRY)  # borrow = 1
    mpu.a = 0x07
    # $0000 SBC $10,X
    _write(mpu.memory, 0x0000, (0xF5, 0x10))
    mpu.x = 0x0D
    mpu.memory[0x001D] = 0x02
    mpu.step()
    assert 0x04 == mpu.a
    assert 0 == mpu.p & mpu.NEGATIVE
    assert 0 == mpu.p & mpu.ZERO
    assert mpu.CARRY == mpu.CARRY


# SEC


def test_sec_sets_carry_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.CARRY)
    # $0000 SEC
    mpu.memory[0x0000] = 0x038
    mpu.step()
    assert 0x0001 == mpu.pc
    assert mpu.CARRY == mpu.p & mpu.CARRY


# SED


def test_sed_sets_decimal_mode_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.DECIMAL)
    # $0000 SED
    mpu.memory[0x0000] = 0xF8
    mpu.step()
    assert 0x0001 == mpu.pc
    assert mpu.DECIMAL == mpu.p & mpu.DECIMAL


# SEI


def test_sei_sets_interrupt_disable_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.INTERRUPT)
    # $0000 SEI
    mpu.memory[0x0000] = 0x78
    mpu.step()
    assert 0x0001 == mpu.pc
    assert mpu.INTERRUPT == mpu.p & mpu.INTERRUPT


# STA Absolute


def test_sta_absolute_stores_a_leaves_a_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.a = 0xFF
    # $0000 STA $ABCD
    _write(mpu.memory, 0x0000, (0x8D, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.memory[0xABCD]
    assert 0xFF == mpu.a
    assert flags == mpu.p


def test_sta_absolute_stores_a_leaves_a_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.a = 0x00
    # $0000 STA $ABCD
    _write(mpu.memory, 0x0000, (0x8D, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD]
    assert 0x00 == mpu.a
    assert flags == mpu.p


# STA Zero Page


def test_sta_zp_stores_a_leaves_a_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.a = 0xFF
    # $0000 STA $0010
    _write(mpu.memory, 0x0000, (0x85, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.memory[0x0010]
    assert 0xFF == mpu.a
    assert flags == mpu.p


def test_sta_zp_stores_a_leaves_a_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.a = 0x00
    # $0000 STA $0010
    _write(mpu.memory, 0x0000, (0x85, 0x10))
    mpu.memory[0x0010] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010]
    assert 0x00 == mpu.a
    assert flags == mpu.p


# STA Absolute, X-Indexed


def test_sta_abs_x_indexed_stores_a_leaves_a_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.a = 0xFF
    mpu.x = 0x03
    # $0000 STA $ABCD,X
    _write(mpu.memory, 0x0000, (0x9D, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.memory[0xABCD + mpu.x]
    assert 0xFF == mpu.a
    assert flags == mpu.p


def test_sta_abs_x_indexed_stores_a_leaves_a_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 STA $ABCD,X
    _write(mpu.memory, 0x0000, (0x9D, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.x] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD + mpu.x]
    assert 0x00 == mpu.a
    assert flags == mpu.p


# STA Absolute, Y-Indexed


def test_sta_abs_y_indexed_stores_a_leaves_a_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.a = 0xFF
    mpu.y = 0x03
    # $0000 STA $ABCD,Y
    _write(mpu.memory, 0x0000, (0x99, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.memory[0xABCD + mpu.y]
    assert 0xFF == mpu.a
    assert flags == mpu.p


def test_sta_abs_y_indexed_stores_a_leaves_a_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.y = 0x03
    # $0000 STA $ABCD,Y
    _write(mpu.memory, 0x0000, (0x99, 0xCD, 0xAB))
    mpu.memory[0xABCD + mpu.y] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD + mpu.y]
    assert 0x00 == mpu.a
    assert flags == mpu.p


# STA Indirect, Indexed (X)


def test_sta_ind_indexed_x_stores_a_leaves_a_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.a = 0xFF
    mpu.x = 0x03
    # $0000 STA ($0010,X)
    # $0013 Vector to $FEED
    _write(mpu.memory, 0x0000, (0x81, 0x10))
    _write(mpu.memory, 0x0013, (0xED, 0xFE))
    mpu.memory[0xFEED] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.memory[0xFEED]
    assert 0xFF == mpu.a
    assert flags == mpu.p


def test_sta_ind_indexed_x_stores_a_leaves_a_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 STA ($0010,X)
    # $0013 Vector to $FEED
    _write(mpu.memory, 0x0000, (0x81, 0x10))
    _write(mpu.memory, 0x0013, (0xED, 0xFE))
    mpu.memory[0xFEED] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0xFEED]
    assert 0x00 == mpu.a
    assert flags == mpu.p


# STA Indexed, Indirect (Y)


def test_sta_indexed_ind_y_stores_a_leaves_a_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.a = 0xFF
    mpu.y = 0x03
    # $0000 STA ($0010),Y
    # $0010 Vector to $FEED
    _write(mpu.memory, 0x0000, (0x91, 0x10))
    _write(mpu.memory, 0x0010, (0xED, 0xFE))
    mpu.memory[0xFEED + mpu.y] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.memory[0xFEED + mpu.y]
    assert 0xFF == mpu.a
    assert flags == mpu.p


def test_sta_indexed_ind_y_stores_a_leaves_a_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.y = 0x03
    # $0000 STA ($0010),Y
    # $0010 Vector to $FEED
    _write(mpu.memory, 0x0000, (0x91, 0x10))
    _write(mpu.memory, 0x0010, (0xED, 0xFE))
    mpu.memory[0xFEED + mpu.y] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0xFEED + mpu.y]
    assert 0x00 == mpu.a
    assert flags == mpu.p


# STA Zero Page, X-Indexed


def test_sta_zp_x_indexed_stores_a_leaves_a_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.a = 0xFF
    mpu.x = 0x03
    # $0000 STA $0010,X
    _write(mpu.memory, 0x0000, (0x95, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.memory[0x0010 + mpu.x]
    assert 0xFF == mpu.a
    assert flags == mpu.p


def test_sta_zp_x_indexed_stores_a_leaves_a_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.x = 0x03
    # $0000 STA $0010,X
    _write(mpu.memory, 0x0000, (0x95, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010 + mpu.x]
    assert 0x00 == mpu.a
    assert flags == mpu.p


# STX Absolute


def test_stx_absolute_stores_x_leaves_x_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.x = 0xFF
    # $0000 STX $ABCD
    _write(mpu.memory, 0x0000, (0x8E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.memory[0xABCD]
    assert 0xFF == mpu.x
    assert flags == mpu.p


def test_stx_absolute_stores_x_leaves_x_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.x = 0x00
    # $0000 STX $ABCD
    _write(mpu.memory, 0x0000, (0x8E, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD]
    assert 0x00 == mpu.x
    assert flags == mpu.p


# STX Zero Page


def test_stx_zp_stores_x_leaves_x_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.x = 0xFF
    # $0000 STX $0010
    _write(mpu.memory, 0x0000, (0x86, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.memory[0x0010]
    assert 0xFF == mpu.x
    assert flags == mpu.p


def test_stx_zp_stores_x_leaves_x_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.x = 0x00
    # $0000 STX $0010
    _write(mpu.memory, 0x0000, (0x86, 0x10))
    mpu.memory[0x0010] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010]
    assert 0x00 == mpu.x
    assert flags == mpu.p


# STX Zero Page, Y-Indexed


def test_stx_zp_y_indexed_stores_x_leaves_x_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.x = 0xFF
    mpu.y = 0x03
    # $0000 STX $0010,Y
    _write(mpu.memory, 0x0000, (0x96, 0x10))
    mpu.memory[0x0010 + mpu.y] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.memory[0x0010 + mpu.y]
    assert 0xFF == mpu.x
    assert flags == mpu.p


def test_stx_zp_y_indexed_stores_x_leaves_x_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.x = 0x00
    mpu.y = 0x03
    # $0000 STX $0010,Y
    _write(mpu.memory, 0x0000, (0x96, 0x10))
    mpu.memory[0x0010 + mpu.y] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010 + mpu.y]
    assert 0x00 == mpu.x
    assert flags == mpu.p


# STY Absolute


def test_sty_absolute_stores_y_leaves_y_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.y = 0xFF
    # $0000 STY $ABCD
    _write(mpu.memory, 0x0000, (0x8C, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0xFF == mpu.memory[0xABCD]
    assert 0xFF == mpu.y
    assert flags == mpu.p


def test_sty_absolute_stores_y_leaves_y_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.y = 0x00
    # $0000 STY $ABCD
    _write(mpu.memory, 0x0000, (0x8C, 0xCD, 0xAB))
    mpu.memory[0xABCD] = 0xFF
    mpu.step()
    assert 0x0003 == mpu.pc
    assert 0x00 == mpu.memory[0xABCD]
    assert 0x00 == mpu.y
    assert flags == mpu.p


# STY Zero Page


def test_sty_zp_stores_y_leaves_y_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.y = 0xFF
    # $0000 STY $0010
    _write(mpu.memory, 0x0000, (0x84, 0x10))
    mpu.memory[0x0010] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.memory[0x0010]
    assert 0xFF == mpu.y
    assert flags == mpu.p


def test_sty_zp_stores_y_leaves_y_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.y = 0x00
    # $0000 STY $0010
    _write(mpu.memory, 0x0000, (0x84, 0x10))
    mpu.memory[0x0010] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010]
    assert 0x00 == mpu.y
    assert flags == mpu.p


# STY Zero Page, X-Indexed


def test_sty_zp_x_indexed_stores_y_leaves_y_and_n_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
    mpu.y = 0xFF
    mpu.x = 0x03
    # $0000 STY $0010,X
    _write(mpu.memory, 0x0000, (0x94, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0xFF == mpu.memory[0x0010 + mpu.x]
    assert 0xFF == mpu.y
    assert flags == mpu.p


def test_sty_zp_x_indexed_stores_y_leaves_y_and_z_flag_unchanged():
    mpu = _make_mpu()
    mpu.p = flags = 0xFF & ~(mpu.ZERO)
    mpu.y = 0x00
    mpu.x = 0x03
    # $0000 STY $0010,X
    _write(mpu.memory, 0x0000, (0x94, 0x10))
    mpu.memory[0x0010 + mpu.x] = 0xFF
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x00 == mpu.memory[0x0010 + mpu.x]
    assert 0x00 == mpu.y
    assert flags == mpu.p


# TAX


def test_tax_transfers_accumulator_into_x():
    mpu = _make_mpu()
    mpu.a = 0xAB
    mpu.x = 0x00
    # $0000 TAX
    mpu.memory[0x0000] = 0xAA
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xAB == mpu.a
    assert 0xAB == mpu.x


def test_tax_sets_negative_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.a = 0x80
    mpu.x = 0x00
    # $0000 TAX
    mpu.memory[0x0000] = 0xAA
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x80 == mpu.a
    assert 0x80 == mpu.x
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_tax_sets_zero_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.x = 0xFF
    # $0000 TAX
    mpu.memory[0x0000] = 0xAA
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.a
    assert 0x00 == mpu.x
    assert mpu.ZERO == mpu.p & mpu.ZERO


# TAY


def test_tay_transfers_accumulator_into_y():
    mpu = _make_mpu()
    mpu.a = 0xAB
    mpu.y = 0x00
    # $0000 TAY
    mpu.memory[0x0000] = 0xA8
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xAB == mpu.a
    assert 0xAB == mpu.y


def test_tay_sets_negative_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.a = 0x80
    mpu.y = 0x00
    # $0000 TAY
    mpu.memory[0x0000] = 0xA8
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x80 == mpu.a
    assert 0x80 == mpu.y
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_tay_sets_zero_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.a = 0x00
    mpu.y = 0xFF
    # $0000 TAY
    mpu.memory[0x0000] = 0xA8
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.a
    assert 0x00 == mpu.y
    assert mpu.ZERO == mpu.p & mpu.ZERO


# TSX


def test_tsx_transfers_stack_pointer_into_x():
    mpu = _make_mpu()
    mpu.sp = 0xAB
    mpu.x = 0x00
    # $0000 TSX
    mpu.memory[0x0000] = 0xBA
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xAB == mpu.sp
    assert 0xAB == mpu.x


def test_tsx_sets_negative_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.sp = 0x80
    mpu.x = 0x00
    # $0000 TSX
    mpu.memory[0x0000] = 0xBA
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x80 == mpu.sp
    assert 0x80 == mpu.x
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_tsx_sets_zero_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.sp = 0x00
    mpu.y = 0xFF
    # $0000 TSX
    mpu.memory[0x0000] = 0xBA
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.sp
    assert 0x00 == mpu.x
    assert mpu.ZERO == mpu.p & mpu.ZERO


# TXA


def test_txa_transfers_x_into_a():
    mpu = _make_mpu()
    mpu.x = 0xAB
    mpu.a = 0x00
    # $0000 TXA
    mpu.memory[0x0000] = 0x8A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xAB == mpu.a
    assert 0xAB == mpu.x


def test_txa_sets_negative_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.x = 0x80
    mpu.a = 0x00
    # $0000 TXA
    mpu.memory[0x0000] = 0x8A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x80 == mpu.a
    assert 0x80 == mpu.x
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_txa_sets_zero_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.x = 0x00
    mpu.a = 0xFF
    # $0000 TXA
    mpu.memory[0x0000] = 0x8A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.a
    assert 0x00 == mpu.x
    assert mpu.ZERO == mpu.p & mpu.ZERO


# TXS


def test_txs_transfers_x_into_stack_pointer():
    mpu = _make_mpu()
    mpu.x = 0xAB
    # $0000 TXS
    mpu.memory[0x0000] = 0x9A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xAB == mpu.sp
    assert 0xAB == mpu.x


def test_txs_does_not_set_negative_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.x = 0x80
    # $0000 TXS
    mpu.memory[0x0000] = 0x9A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x80 == mpu.sp
    assert 0x80 == mpu.x
    assert 0 == mpu.p & mpu.NEGATIVE


def test_txs_does_not_set_zero_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.x = 0x00
    # $0000 TXS
    mpu.memory[0x0000] = 0x9A
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x00 == mpu.sp
    assert 0x00 == mpu.x
    assert 0 == mpu.p & mpu.ZERO


# TYA


def test_tya_transfers_y_into_a():
    mpu = _make_mpu()
    mpu.y = 0xAB
    mpu.a = 0x00
    # $0000 TYA
    mpu.memory[0x0000] = 0x98
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0xAB == mpu.a
    assert 0xAB == mpu.y


def test_tya_sets_negative_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.NEGATIVE)
    mpu.y = 0x80
    mpu.a = 0x00
    # $0000 TYA
    mpu.memory[0x0000] = 0x98
    mpu.step()
    assert 0x0001 == mpu.pc
    assert 0x80 == mpu.a
    assert 0x80 == mpu.y
    assert mpu.NEGATIVE == mpu.p & mpu.NEGATIVE


def test_tya_sets_zero_flag():
    mpu = _make_mpu()
    mpu.p &= ~(mpu.ZERO)
    mpu.y = 0x00
    mpu.a = 0xFF
    # $0000 TYA
    mpu.memory[0x0000] = 0x98
    mpu.step()
    assert 0x00 == mpu.a
    assert 0x00 == mpu.y
    assert mpu.ZERO == mpu.p & mpu.ZERO
    assert 0x0001 == mpu.pc


def test_decorated_addressing_modes_are_valid():
    valid_modes = [x[0] for x in py65.assembler.Assembler.Addressing]
    mpu = _make_mpu()
    for name, mode in mpu.disassemble:
        assert mode in valid_modes


def test_brk_interrupt():
    mpu = _make_mpu()
    mpu.p = 0x00
    _write(mpu.memory, 0xFFFE, (0x00, 0x04))

    _write(
        mpu.memory,
        0x0000,
        (
            0xA9,
            0x01,  # LDA #$01
            0x00,
            0xEA,  # BRK + skipped byte
            0xEA,
            0xEA,  # NOP, NOP
            0xA9,
            0x03,
        ),
    )  # LDA #$03

    _write(mpu.memory, 0x0400, (0xA9, 0x02, 0x40))  # LDA #$02  # RTI

    mpu.step()  # LDA #$01
    assert 0x01 == mpu.a
    assert 0x0002 == mpu.pc
    mpu.step()  # BRK
    assert 0x0400 == mpu.pc
    mpu.step()  # LDA #$02
    assert 0x02 == mpu.a
    assert 0x0402 == mpu.pc
    mpu.step()  # RTI

    assert 0x0004 == mpu.pc
    mpu.step()  # A NOP
    mpu.step()  # The second NOP

    mpu.step()  # LDA #$03
    assert 0x03 == mpu.a
    assert 0x0008 == mpu.pc


# Test Helpers


def _write(memory, start_address, bytes):
    memory[start_address : start_address + len(bytes)] = bytes


def _make_mpu(*args, **kargs):
    klass = _get_target_class()
    mpu = klass(*args, **kargs)
    if "memory" not in kargs:
        mpu.memory = 0x10000 * [0xAA]
    return mpu


def test_repr():
    mpu = _make_mpu()
    assert "6502" in repr(mpu)


# ADC Indirect, Indexed (X)


def test_adc_ind_indexed_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.p = 0x00
    mpu.a = 0x01
    mpu.x = 0xFF
    # $0000 ADC ($80,X)
    # $007f Vector to $BBBB (read if page wrapped)
    # $017f Vector to $ABCD (read if no page wrap)
    _write(mpu.memory, 0x0000, (0x61, 0x80))
    _write(mpu.memory, 0x007F, (0xBB, 0xBB))
    _write(mpu.memory, 0x017F, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x01
    mpu.memory[0xBBBB] = 0x02
    mpu.step()
    assert 0x03 == mpu.a


# ADC Indexed, Indirect (Y)


def test_adc_indexed_ind_y_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.pc = 0x1000
    mpu.p = 0
    mpu.a = 0x42
    mpu.y = 0x02
    # $1000 ADC ($FF),Y
    _write(mpu.memory, 0x1000, (0x71, 0xFF))
    # Vector
    mpu.memory[0x00FF] = 0x10  # low byte
    mpu.memory[0x0100] = 0x20  # high byte if no page wrap
    mpu.memory[0x0000] = 0x00  # high byte if page wrapped
    # Data
    mpu.memory[0x2012] = 0x14  # read if no page wrap
    mpu.memory[0x0012] = 0x42  # read if page wrapped
    mpu.step()
    assert 0x84 == mpu.a


# LDA Zero Page, X-Indexed


def test_lda_zp_x_indexed_page_wraps():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0xFF
    # $0000 LDA $80,X
    _write(mpu.memory, 0x0000, (0xB5, 0x80))
    mpu.memory[0x007F] = 0x42
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x42 == mpu.a


# AND Indexed, Indirect (Y)


def test_and_indexed_ind_y_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.pc = 0x1000
    mpu.a = 0x42
    mpu.y = 0x02
    # $1000 AND ($FF),Y
    _write(mpu.memory, 0x1000, (0x31, 0xFF))
    # Vector
    mpu.memory[0x00FF] = 0x10  # low byte
    mpu.memory[0x0100] = 0x20  # high byte if no page wrap
    mpu.memory[0x0000] = 0x00  # high byte if page wrapped
    # Data
    mpu.memory[0x2012] = 0x00  # read if no page wrap
    mpu.memory[0x0012] = 0xFF  # read if page wrapped
    mpu.step()
    assert 0x42 == mpu.a


# BRK


def test_brk_preserves_decimal_flag_when_it_is_set():
    mpu = _make_mpu()
    mpu.p = mpu.DECIMAL
    # $C000 BRK
    mpu.memory[0xC000] = 0x00
    mpu.pc = 0xC000
    mpu.step()
    assert mpu.BREAK == mpu.p & mpu.BREAK
    assert mpu.DECIMAL == mpu.p & mpu.DECIMAL


def test_brk_preserves_decimal_flag_when_it_is_clear():
    mpu = _make_mpu()
    mpu.p = 0
    # $C000 BRK
    mpu.memory[0xC000] = 0x00
    mpu.pc = 0xC000
    mpu.step()
    assert mpu.BREAK == mpu.p & mpu.BREAK
    assert 0 == mpu.p & mpu.DECIMAL


# CMP Indirect, Indexed (X)


def test_cmp_ind_x_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.p = 0
    mpu.a = 0x42
    mpu.x = 0xFF
    # $0000 CMP ($80,X)
    # $007f Vector to $BBBB (read if page wrapped)
    # $017f Vector to $ABCD (read if no page wrap)
    _write(mpu.memory, 0x0000, (0xC1, 0x80))
    _write(mpu.memory, 0x007F, (0xBB, 0xBB))
    _write(mpu.memory, 0x017F, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.memory[0xBBBB] = 0x42
    mpu.step()
    assert mpu.ZERO == mpu.p & mpu.ZERO


# CMP Indexed, Indirect (Y)


def test_cmp_indexed_ind_y_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.pc = 0x1000
    mpu.p = 0
    mpu.a = 0x42
    mpu.y = 0x02
    # $1000 CMP ($FF),Y
    _write(mpu.memory, 0x1000, (0xD1, 0xFF))
    # Vector
    mpu.memory[0x00FF] = 0x10  # low byte
    mpu.memory[0x0100] = 0x20  # high byte if no page wrap
    mpu.memory[0x0000] = 0x00  # high byte if page wrapped
    # Data
    mpu.memory[0x2012] = 0x14  # read if no page wrap
    mpu.memory[0x0012] = 0x42  # read if page wrapped
    mpu.step()
    assert mpu.ZERO == mpu.p & mpu.ZERO


# EOR Indirect, Indexed (X)


def test_eor_ind_x_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.p = 0
    mpu.a = 0xAA
    mpu.x = 0xFF
    # $0000 EOR ($80,X)
    # $007f Vector to $BBBB (read if page wrapped)
    # $017f Vector to $ABCD (read if no page wrap)
    _write(mpu.memory, 0x0000, (0x41, 0x80))
    _write(mpu.memory, 0x007F, (0xBB, 0xBB))
    _write(mpu.memory, 0x017F, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x00
    mpu.memory[0xBBBB] = 0xFF
    mpu.step()
    assert 0x55 == mpu.a


# EOR Indexed, Indirect (Y)


def test_eor_indexed_ind_y_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.pc = 0x1000
    mpu.a = 0xAA
    mpu.y = 0x02
    # $1000 EOR ($FF),Y
    _write(mpu.memory, 0x1000, (0x51, 0xFF))
    # Vector
    mpu.memory[0x00FF] = 0x10  # low byte
    mpu.memory[0x0100] = 0x20  # high byte if no page wrap
    mpu.memory[0x0000] = 0x00  # high byte if page wrapped
    # Data
    mpu.memory[0x2012] = 0x00  # read if no page wrap
    mpu.memory[0x0012] = 0xFF  # read if page wrapped
    mpu.step()
    assert 0x55 == mpu.a


# LDA Indirect, Indexed (X)


def test_lda_ind_indexed_x_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0xFF
    # $0000 LDA ($80,X)
    # $007f Vector to $BBBB (read if page wrapped)
    # $017f Vector to $ABCD (read if no page wrap)
    _write(mpu.memory, 0x0000, (0xA1, 0x80))
    _write(mpu.memory, 0x007F, (0xBB, 0xBB))
    _write(mpu.memory, 0x017F, (0xCD, 0xAB))
    mpu.memory[0xABCD] = 0x42
    mpu.memory[0xBBBB] = 0xEF
    mpu.step()
    assert 0xEF == mpu.a


# LDA Indexed, Indirect (Y)


def test_lda_indexed_ind_y_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.pc = 0x1000
    mpu.a = 0x00
    mpu.y = 0x02
    # $1000 LDA ($FF),Y
    _write(mpu.memory, 0x1000, (0xB1, 0xFF))
    # Vector
    mpu.memory[0x00FF] = 0x10  # low byte
    mpu.memory[0x0100] = 0x20  # high byte if no page wrap
    mpu.memory[0x0000] = 0x00  # high byte if page wrapped
    # Data
    mpu.memory[0x2012] = 0x14  # read if no page wrap
    mpu.memory[0x0012] = 0x42  # read if page wrapped
    mpu.step()
    assert 0x42 == mpu.a


# LDA Zero Page, X-Indexed


def test_lda_zp_x_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.a = 0x00
    mpu.x = 0xFF
    # $0000 LDA $80,X
    _write(mpu.memory, 0x0000, (0xB5, 0x80))
    mpu.memory[0x007F] = 0x42
    mpu.step()
    assert 0x0002 == mpu.pc
    assert 0x42 == mpu.a


# JMP Indirect


def test_jmp_jumps_to_address_with_page_wrap_bug():
    mpu = _make_mpu()
    mpu.memory[0x00FF] = 0
    # $0000 JMP ($00)
    _write(mpu.memory, 0, (0x6C, 0xFF, 0x00))
    mpu.step()
    assert 0x6C00 == mpu.pc
    assert 5 == mpu.processorCycles


# ORA Indexed, Indirect (Y)


def test_ora_indexed_ind_y_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.pc = 0x1000
    mpu.a = 0x00
    mpu.y = 0x02
    # $1000 ORA ($FF),Y
    _write(mpu.memory, 0x1000, (0x11, 0xFF))
    # Vector
    mpu.memory[0x00FF] = 0x10  # low byte
    mpu.memory[0x0100] = 0x20  # high byte if no page wrap
    mpu.memory[0x0000] = 0x00  # high byte if page wrapped
    # Data
    mpu.memory[0x2012] = 0x00  # read if no page wrap
    mpu.memory[0x0012] = 0x42  # read if page wrapped
    mpu.step()
    assert 0x42 == mpu.a


# SBC Indexed, Indirect (Y)


def test_sbc_indexed_ind_y_has_page_wrap_bug():
    mpu = _make_mpu()
    mpu.pc = 0x1000
    mpu.p = mpu.CARRY
    mpu.a = 0x42
    mpu.y = 0x02
    # $1000 SBC ($FF),Y
    _write(mpu.memory, 0x1000, (0xF1, 0xFF))
    # Vector
    mpu.memory[0x00FF] = 0x10  # low byte
    mpu.memory[0x0100] = 0x20  # high byte if no page wrap
    mpu.memory[0x0000] = 0x00  # high byte if page wrapped
    # Data
    mpu.memory[0x2012] = 0x02  # read if no page wrap
    mpu.memory[0x0012] = 0x03  # read if page wrapped
    mpu.step()
    assert 0x3F == mpu.a


def _get_target_class():
    return py65.devices.mpu6502.MPU
