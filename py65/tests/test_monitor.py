import os
import tempfile

from py65.monitor import Monitor

try:
    from StringIO import StringIO  # type: ignore[import-error]
except ImportError:  # Python 3
    from io import StringIO

# line processing


def test__preprocess_line_removes_leading_dots_after_whitespace():
    mon = Monitor()
    assert "help" == mon._preprocess_line("  ...help")


def test__preprocess_line_removes_leading_and_trailing_whitespace():
    mon = Monitor()
    assert "help" == mon._preprocess_line(" \t help \t ")


def test__preprocess_line_rewrites_shortcut_when_alone_on_line():
    mon = Monitor()
    assert "assemble" == mon._preprocess_line(" a")


def test__preprocess_line_rewrites_shortcut_with_arguments_on_line():
    mon = Monitor()
    assert "assemble c000" == mon._preprocess_line("a c000")


def test__preprocess_line_removes_semicolon_comments():
    mon = Monitor()
    assert "assemble" == mon._preprocess_line("a ;comment")


def test__preprocess_line_does_not_remove_semicolons_in_quotes():
    mon = Monitor()
    assert 'assemble lda #$";"' == mon._preprocess_line('a lda #$";" ;comment')


def test__preprocess_line_does_not_remove_semicolons_in_apostrophes():
    mon = Monitor()
    assert "assemble lda #$';'" == mon._preprocess_line("assemble lda #$';' ;comment")


# add_breakpoint


def test_shortcut_for_add_breakpoint():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("ab")

    out = stdout.getvalue()
    assert out.startswith("add_breakpoint")


def test_do_add_breakpoint_syntax_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_add_breakpoint("")
    out = stdout.getvalue()
    assert out.startswith("Syntax error:")


def test_do_add_breakpoint_adds_number():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_add_breakpoint("ffd2")
    out = stdout.getvalue()
    assert out.startswith("Breakpoint 0 added at $FFD2")
    assert 0xFFD2 in mon._breakpoints


def test_do_add_breakpoint_adds_label():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    address_parser = mon._address_parser
    address_parser.labels["chrout"] = 0xFFD2
    mon.do_add_breakpoint("chrout")
    out = stdout.getvalue()
    assert out.startswith("Breakpoint 0 added at $FFD2")
    assert 0xFFD2 in mon._breakpoints


# add_label


def test_shortcut_for_add_label():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("al")

    out = stdout.getvalue()
    assert out.startswith("add_label")


def test_do_add_label_syntax_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_add_label("should be address space label")
    out = stdout.getvalue()
    err = "Syntax error: should be address space label\n"
    assert out.startswith(err)


def test_do_add_label_overflow_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_add_label("$10000 toobig")
    out = stdout.getvalue()
    err = "Overflow error: $10000 toobig\n"
    assert out.startswith(err)


def test_do_add_label_label_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_add_label("nonexistent foo")
    out = stdout.getvalue()
    err = "Label not found: nonexistent\n"
    assert out.startswith(err)


def test_do_add_label_adds_label():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_add_label("$c000 foo")
    address_parser = mon._address_parser
    assert 0xC000 == address_parser.number("foo")


def test_help_add_label():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_add_label()
    out = stdout.getvalue()
    assert out.startswith("add_label")


# assemble


def test_shortcut_for_assemble():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("a")

    out = stdout.getvalue()
    assert out.startswith("assemble")


def test_do_assemble_assembles_valid_statement():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_assemble("c000 lda #$ab")

    mpu = mon._mpu
    assert 0xA9 == mpu.memory[0xC000]
    assert 0xAB == mpu.memory[0xC001]


def test_do_assemble_outputs_disassembly():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_assemble("c000 lda #$ab")

    out = stdout.getvalue()
    assert "$c000  a9 ab     LDA #$ab\n" == out


def test_do_assemble_parses_start_address_label():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_add_label("c000 base")
    mon.do_assemble("base rts")

    mpu = mon._mpu
    assert 0x60 == mpu.memory[0xC000]


def test_do_assemble_shows_bad_label_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_assemble("nonexistent rts")

    out = stdout.getvalue()
    assert "Label not found: nonexistent\n" == out


def test_do_assemble_shows_bad_syntax_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_assemble("c000 foo")

    out = stdout.getvalue()
    assert "Syntax error: foo\n" == out


def test_do_assemble_shows_overflow_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_assemble("c000 lda #$fff")

    out = stdout.getvalue()
    assert "Overflow error: c000 lda #$fff\n" == out


def test_do_assemble_passes_addr_for_relative_branch_calc():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_assemble("4000 bvs $4005")

    out = stdout.getvalue()
    assert "$4000  70 03     BVS $4005\n" == out


def test_do_assemble_constrains_address_to_valid_range():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_assemble("-1 lda #$ab")

    out = stdout.getvalue()
    assert "Overflow error: -1 lda #$ab\n" == out


def test_help_assemble():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_assemble()

    out = stdout.getvalue()
    assert "assemble <address>" in out


# cd


def test_help_cd():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_cd()

    out = stdout.getvalue()
    assert out.startswith("cd <directory>")


def test_do_cd_with_no_dir_shows_help():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_cd("")

    out = stdout.getvalue()
    assert out.startswith("cd <directory>")


def test_do_cd_changes_cwd():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    here = os.path.abspath(os.path.dirname(__file__))
    mon.do_cd(here)

    out = stdout.getvalue()
    assert out.startswith(here)
    assert here == os.getcwd()


def test_do_cd_with_bad_dir_shows_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_cd("/path/to/a/nonexistent/directory")

    out = stdout.getvalue()
    assert out.startswith("Cannot change directory")


# cycles


def test_help_cycles():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_cycles()

    out = stdout.getvalue()
    assert out.startswith("Display the total number of cycles")


def test_do_cycles_shows_zero_initially():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_cycles("")

    out = stdout.getvalue()
    assert out == "0\n"


def test_do_cycles_shows_count_after_step():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._mpu.memory[0x0000] = 0xEA  # => NOP (2 cycles)
    mon._mpu.step()
    mon.do_cycles("")

    out = stdout.getvalue()
    assert out == "2\n"


# delete_label


def test_shortcut_for_delete_label():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("dl")

    out = stdout.getvalue()
    assert out.startswith("delete_label")


def test_do_delete_label_no_args_displays_help():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_delete_label("")
    out = stdout.getvalue()
    assert out.startswith("delete_label")


def test_do_delete_label_with_bad_label_fails_silently():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_delete_label("non-existant-label")
    out = stdout.getvalue()
    assert "" == out


def test_do_delete_label_with_delete_label():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._address_parser.labels["foo"] = 0xC000
    mon.do_delete_label("foo")
    assert "foo" not in mon._address_parser.labels
    out = stdout.getvalue()
    assert "" == out


# disassemble


def test_shortcut_for_disassemble():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("d")

    out = stdout.getvalue()
    assert out.startswith("disassemble")


def test_help_disassemble():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_disassemble()
    out = stdout.getvalue()
    assert out.startswith("disassemble <address_range>")


def test_disassemble_shows_help_when_given_extra_args():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_disassemble("c000 c001")
    out = stdout.getvalue()
    assert out.startswith("disassemble <address_range>")


def test_disassemble_will_disassemble_one_address():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._mpu.memory[0xC000] = 0xEA  # => NOP
    mon._mpu.step()
    mon.do_disassemble("c000")

    out = stdout.getvalue()
    disasm = "$c000  ea        NOP\n"
    assert out == disasm


def test_disassemble_will_disassemble_an_address_range():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._mpu.memory[0xC000] = 0xEA  # => NOP
    mon._mpu.memory[0xC001] = 0xEA  # => NOP
    mon._mpu.step()
    mon.do_disassemble("c000:c001")

    out = stdout.getvalue()
    disasm = "$c000  ea        NOP\n$c001  ea        NOP\n"
    assert out == disasm


def test_disassemble_wraps_an_instruction_around_memory():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._mpu.memory[0xFFFF] = 0x20  # => JSR
    mon._mpu.memory[0x0000] = 0xD2  #
    mon._mpu.memory[0x0001] = 0xFF  # => $FFD2
    mon.do_disassemble("ffff")

    out = stdout.getvalue()
    disasm = "$ffff  20 d2 ff  JSR $ffd2\n"
    assert out == disasm


def test_disassemble_wraps_disassembly_list_around_memory():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._mpu.memory[0xFFFF] = 0x20  # => JSR
    mon._mpu.memory[0x0000] = 0xD2
    mon._mpu.memory[0x0001] = 0xFF  # => $FFD2
    mon._mpu.memory[0x0002] = 0x20  # => JSR
    mon._mpu.memory[0x0003] = 0xE4
    mon._mpu.memory[0x0004] = 0xFF  # => $FFE4
    mon._mpu.memory[0x0005] = 0xEA  # => NOP
    mon.do_disassemble("ffff:5")
    out = stdout.getvalue()
    disasm = (
        "$ffff  20 d2 ff  JSR $ffd2\n"
        "$0002  20 e4 ff  JSR $ffe4\n"
        "$0005  ea        NOP\n"
    )
    assert out == disasm


# fill


def test_shortcut_f_for_fill():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("f")

    out = stdout.getvalue()
    assert out.startswith("fill <address_range>")


def test_shortcut_gt_for_fill():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help(">")

    out = stdout.getvalue()
    assert out.startswith("fill <address_range>")


def test_help_fill():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_fill()

    out = stdout.getvalue()
    assert out.startswith("fill <address_range>")


def test_do_fill_with_no_args_shows_help():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_fill("")

    out = stdout.getvalue()
    assert out.startswith("fill <address_range>")


def test_do_fill_will_fill_one_address():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._mpu.memory[0xC000] = 0x00
    mon.do_fill("c000 aa")

    assert 0xAA == mon._mpu.memory[0xC000]
    out = stdout.getvalue()
    assert out.startswith("Wrote +1 bytes from $c000 to $c000")


def test_do_fill_will_fill_an_address_range_with_a_single_byte():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._mpu.memory[0xC000] = 0x00
    mon._mpu.memory[0xC001] = 0x00
    mon._mpu.memory[0xC002] = 0x00
    mon.do_fill("c000:c001 aa")

    assert 0xAA == mon._mpu.memory[0xC000]
    assert 0xAA == mon._mpu.memory[0xC001]
    assert 0x00 == mon._mpu.memory[0xC002]
    out = stdout.getvalue()
    assert out.startswith("Wrote +2 bytes from $c000 to $c001")


def test_do_fill_will_fill_an_address_range_with_byte_sequence():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._mpu.memory[0xC000] = 0x00
    mon._mpu.memory[0xC001] = 0x00
    mon._mpu.memory[0xC002] = 0x00
    mon._mpu.memory[0xC003] = 0x00
    mon.do_fill("c000:c003 aa bb")

    assert 0xAA == mon._mpu.memory[0xC000]
    assert 0xBB == mon._mpu.memory[0xC001]
    assert 0xAA == mon._mpu.memory[0xC002]
    assert 0xBB == mon._mpu.memory[0xC003]
    out = stdout.getvalue()
    assert out.startswith("Wrote +4 bytes from $c000 to $c003")


def test_do_fill_bad_label_in_address_shows_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_fill("nonexistent 0")

    out = stdout.getvalue()
    assert out.startswith("Label not found: nonexistent")


def test_do_fill_bad_label_in_value_shows_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_fill("0 nonexistent")

    out = stdout.getvalue()
    assert out.startswith("Label not found: nonexistent")


def test_do_fill_bad_start_address():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_fill("10000 00")

    out = stdout.getvalue()
    assert out.startswith("Overflow: $10000")


def test_do_fill_bad_end_address():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_fill("ffff:10000 00 00")

    out = stdout.getvalue()
    assert out.startswith("Overflow: $10000")


def test_do_fill_bad_data():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_fill("0 100")

    out = stdout.getvalue()
    assert out.startswith("Overflow: $100")


# goto


def test_shortcut_for_goto():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("g")

    out = stdout.getvalue()
    assert out.startswith("goto")


def test_goto_without_args_shows_command_help():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.onecmd("goto")
    out = stdout.getvalue()
    assert "goto <address>" in out


def test_goto_with_breakpoints_stops_execution_at_breakpoint():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._breakpoints = [0x03]
    mon._mpu.memory = [0xEA, 0xEA, 0xEA, 0xEA]
    mon.do_goto("0")
    out = stdout.getvalue()
    assert out.startswith("Breakpoint 0 reached")
    assert 0x03 == mon._mpu.pc


def test_goto_with_breakpoints_stops_execution_at_brk():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._breakpoints = [0x02]
    mon._mpu.memory = [0xEA, 0xEA, 0x00, 0xEA]
    mon.do_goto("0")
    assert 0x02 == mon._mpu.pc


def test_goto_without_breakpoints_stops_execution_at_brk():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._breakpoints = []
    mon._mpu.memory = [0xEA, 0xEA, 0x00, 0xEA]
    mon.do_goto("0")
    assert 0x02 == mon._mpu.pc


# help


def test_help_without_args_shows_documented_commands():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.onecmd("help")
    out = stdout.getvalue()
    assert "Documented commands" in out

    stdout.truncate(0)
    mon.onecmd("h")
    out = stdout.getvalue()
    assert "Documented commands" in out

    stdout.truncate(0)
    mon.onecmd("?")
    out = stdout.getvalue()
    assert "Documented commands" in out


def test_help_with_args_shows_command_help():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.onecmd("help assemble")
    out = stdout.getvalue()
    assert "assemble <address>" in out

    stdout.truncate(0)
    mon.onecmd("h a")
    out = stdout.getvalue()
    assert "assemble <address>" in out


def test_help_with_invalid_args_shows_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.onecmd("help foo")
    out = stdout.getvalue()
    assert out.startswith("*** No help on foo")


def test_shortcut_for_show_breakpoints():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("shb")
    out = stdout.getvalue()
    assert out.startswith("show_breakpoints")


def test_show_breakpoints_shows_breakpoints():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._breakpoints = [0xFFD2]
    mon._address_parser.labels = {"chrout": 0xFFD2}
    mon.do_show_breakpoints("")
    out = stdout.getvalue()
    assert out.startswith("Breakpoint 0: $FFD2 chrout")


def test_show_breakpoints_ignores_deleted_breakpoints():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._breakpoints = [None, 0xFFD2]
    mon.do_show_breakpoints("")
    out = stdout.getvalue()
    assert out.startswith("Breakpoint 1: $FFD2")


# load


def test_shortcut_for_load():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("l")

    out = stdout.getvalue()
    assert out.startswith("load")


def test_load_with_less_than_two_args_syntax_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_load("")
    out = stdout.getvalue()
    assert out.startswith("Syntax error")


def test_load_with_more_than_two_args_syntax_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_load("one two three")
    out = stdout.getvalue()
    assert out.startswith("Syntax error")


def test_load():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)

    filename = tempfile.mktemp()
    try:
        f = open(filename, "wb")
        f.write(b"\xaa\xbb\xcc")
        f.close()

        mon.do_load("'%s' a600" % filename)
        assert "Wrote +3 bytes from $a600 to $a602\n" == stdout.getvalue()
        assert [0xAA == 0xBB, 0xCC], mon._mpu.memory[0xA600:0xA603]
    finally:
        os.unlink(filename)


def test_help_load():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_load()
    out = stdout.getvalue()
    assert out.startswith("load")


# mem


def test_shortcut_for_mem():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("m")

    out = stdout.getvalue()
    assert out.startswith("mem <address_range>")


def test_do_mem_shows_help_when_given_no_args():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_mem("")

    out = stdout.getvalue()
    assert out.startswith("mem <address_range>")


def test_do_mem_shows_help_when_given_extra_args():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_mem("c000 c001")

    out = stdout.getvalue()
    assert out.startswith("mem <address_range>")


def test_do_mem_shows_memory_for_a_single_address():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._mpu.memory[0xC000] = 0xAA
    mon.do_mem("c000")

    out = stdout.getvalue()
    assert "c000:  aa\n" == out


def test_do_mem_shows_memory_for_an_address_range():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._mpu.memory[0xC000] = 0xAA
    mon._mpu.memory[0xC001] = 0xBB
    mon._mpu.memory[0xC002] = 0xCC
    mon.do_mem("c000:c002")

    out = stdout.getvalue()
    assert "c000:  aa  bb  cc\n" == out


def test_do_mem_wraps_at_terminal_width():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._width = 14
    mon.do_mem("c000:c003")

    out = stdout.getvalue()
    assert "c000:  00  00\nc002:  00  00\n" == out


# mpu


def test_mpu_with_no_args_prints_current_lists_available_mpus():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_mpu("")

    lines = stdout.getvalue().splitlines()
    assert 2 == len(lines)
    assert lines[0].startswith("Current MPU is ")
    assert lines[1].startswith("Available MPUs:")


def test_mpu_with_bad_arg_gives_error_lists_available_mpus():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_mpu("z80")

    lines = stdout.getvalue().splitlines()
    assert 2 == len(lines)
    assert "Unknown MPU: z80" == lines[0]
    assert lines[1].startswith("Available MPUs:")


def test_mpu_selects_6502():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_mpu("6502")

    lines = stdout.getvalue().splitlines()
    assert 1 == len(lines)
    assert "Reset with new MPU 6502" == lines[0]
    assert "6502" == mon._mpu.name


def test_mpu_selects_65C02():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_mpu("65C02")

    lines = stdout.getvalue().splitlines()
    assert 1 == len(lines)
    assert "Reset with new MPU 65C02" == lines[0]
    assert "65C02" == mon._mpu.name


def test_mpu_select_is_not_case_sensitive():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_mpu("65c02")
    assert "65C02" == mon._mpu.name


def test_help_mpu():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_mpu()

    lines = stdout.getvalue().splitlines()
    assert "mpu\t\tPrint available microprocessors." == lines[0]
    assert "mpu <type>\tSelect a new microprocessor." == lines[1]


# quit


def test_shortcuts_for_quit():
    for shortcut in ["exit", "x", "q", "EOF"]:
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help(shortcut)

        out = stdout.getvalue()
        assert out.startswith("To quit")


def test_do_quit():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    exitnow = mon.do_quit("")
    assert True == exitnow


def test_help_quit():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_quit()
    out = stdout.getvalue()
    assert out.startswith("To quit,")


# pwd


def test_pwd_shows_os_getcwd():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_pwd()

    out = stdout.getvalue()
    assert "%s\n" % os.getcwd() == out


def test_help_pwd():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_pwd()
    out = stdout.getvalue()
    assert out.startswith("Show the current working")


# radix


def test_shortcut_for_radix():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("rad")

    out = stdout.getvalue()
    assert out.startswith("radix")


def test_help_radix():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_radix()
    out = stdout.getvalue()
    assert out.startswith("radix [H|D|O|B]")


def test_radix_no_arg_displays_radix():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_radix("")
    out = stdout.getvalue()
    assert out.startswith("Default radix is Hexadecimal")


def test_radix_invalid_radix_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_radix("f")
    out = stdout.getvalue()
    assert out.startswith("Illegal radix: f")


def test_radix_sets_binary():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_radix("b")
    out = stdout.getvalue()
    assert out.startswith("Default radix is Binary")


def test_radix_sets_decimal():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_radix("d")
    out = stdout.getvalue()
    assert out.startswith("Default radix is Decimal")


def test_radix_sets_hexadecimal():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_radix("h")
    out = stdout.getvalue()
    assert out.startswith("Default radix is Hexadecimal")


def test_radix_sets_octal():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_radix("o")
    out = stdout.getvalue()
    assert out.startswith("Default radix is Octal")


# registers


def test_shortcut_for_registers():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("r")

    out = stdout.getvalue()
    assert out.startswith("registers")


def test_registers_display_returns_to_prompt():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_registers("")
    out = stdout.getvalue()
    assert "" == out


def test_registers_syntax_error_bad_format():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_registers("x")
    out = stdout.getvalue()
    assert "Syntax error: x\n" == out


def test_registers_label_error_bad_value():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_registers("x=pony")
    out = stdout.getvalue()
    assert "Label not found: pony\n" == out


def test_registers_invalid_register_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_registers("z=3")
    out = stdout.getvalue()
    assert "Invalid register: z\n" == out


def test_registers_updates_single_register():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_registers("x=42")
    out = stdout.getvalue()
    assert "" == out
    assert 0x42 == mon._mpu.x


def test_registers_updates_all_registers():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_registers("a=42,x=43,y=44,p=45, sp=46, pc=4600")
    out = stdout.getvalue()
    assert "" == out
    assert 0x42 == mon._mpu.a
    assert 0x43 == mon._mpu.x
    assert 0x44 == mon._mpu.y
    assert 0x45 == mon._mpu.p
    assert 0x46 == mon._mpu.sp
    assert 0x4600 == mon._mpu.pc


def test_registers_pc_overflow():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_registers("pc=10000")
    out = stdout.getvalue()
    expected = "Overflow: '10000' too wide for register 'pc'"
    assert out.startswith(expected)


def test_registers_a_overflow():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_registers("a=100")
    out = stdout.getvalue()
    expected = "Overflow: '100' too wide for register 'a'"
    assert out.startswith(expected)


def test_help_registers():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_registers()
    out = stdout.getvalue()
    assert out.startswith("registers[<name>")


# return


def test_shortcut_for_return():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("ret")

    out = stdout.getvalue()
    assert out.startswith("return")


# reset


def test_do_reset():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    old_mpu = mon._mpu
    old_name = mon._mpu.name
    mon.do_reset("")
    assert old_mpu != mon._mpu
    assert old_name == mon._mpu.name


def test_help_reset():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_reset()
    out = stdout.getvalue()
    assert out.startswith("reset\t")


# save


def test_shortcut_for_save():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("s")

    out = stdout.getvalue()
    assert out.startswith("save")


def test_save_with_less_than_three_args_syntax_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_save("filename start")
    out = stdout.getvalue()
    assert out.startswith("Syntax error")


def test_save():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._mpu.memory[0:3] = [0xAA, 0xBB, 0xCC]

    filename = tempfile.mktemp()
    try:
        mon.do_save("'%s' 0 2" % filename)
        assert "Saved +3 bytes to %s\n" % filename == stdout.getvalue()

        f = open(filename, "rb")
        contents = f.read()
        f.close()
        assert b"\xaa\xbb\xcc" == contents
    finally:
        os.unlink(filename)


def test_help_save():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_save()
    out = stdout.getvalue()
    assert out.startswith("save")


# step


def test_shortcut_for_step():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("z")

    out = stdout.getvalue()
    assert out.startswith("step")


# tilde


def test_tilde_shortcut_with_space():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.onecmd("~ $10")
    out = stdout.getvalue()
    expected = "+16\n$10\n0020\n00010000\n"
    assert out.startswith(expected)


def test_tilde_shortcut_without_space_for_vice_compatibility():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.onecmd("~$10")
    out = stdout.getvalue()
    expected = "+16\n$10\n0020\n00010000\n"
    assert out.startswith(expected)


def test_do_tilde():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_tilde("$10")
    out = stdout.getvalue()
    expected = "+16\n$10\n0020\n00010000\n"
    assert out.startswith(expected)


def test_do_tilde_with_no_arg_shows_help():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_tilde("")
    out = stdout.getvalue()
    expected = "~ <number>"
    assert out.startswith(expected)


def test_do_tilde_with_bad_label_shows_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_tilde("bad_label")
    out = stdout.getvalue()
    expected = "Bad label: bad_label"
    assert out.startswith(expected)


def test_do_tilde_with_overflow_shows_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_tilde("$FFFFFFFFFFFF")
    out = stdout.getvalue()
    expected = "Overflow error: $FFFFFFFFFFFF"
    assert out.startswith(expected)


def test_help_tilde():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_tilde()
    out = stdout.getvalue()
    expected = "~ <number>"
    assert out.startswith(expected)


# show_labels


def test_shortcut_for_show_labels():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_help("shl")

    out = stdout.getvalue()
    assert out.startswith("show_labels")


def test_show_labels_displays_labels():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._address_parser.labels = {"chrin": 0xFFC4, "chrout": 0xFFD2}
    mon.do_show_labels("")
    out = stdout.getvalue()
    assert "ffc4: chrin\nffd2: chrout\n" == out


def test_help_show_labels():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon._address_parser.labels = {"chrin": 0xFFC4, "chrout": 0xFFD2}
    mon.do_show_labels("")
    out = stdout.getvalue()
    assert "ffc4: chrin\nffd2: chrout\n" == out


# version


def test_do_version():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_version("")
    out = stdout.getvalue()
    assert out.startswith("\nPy65")


def test_help_version():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_version()
    out = stdout.getvalue()
    assert out.startswith("version\t")


# width


def test_do_width_with_no_args_shows_current_width():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_width("")
    out = stdout.getvalue()
    assert "Terminal width is 78\n" == out


def test_do_width_with_arg_changes_width():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_width("38")
    out = stdout.getvalue()
    assert "Terminal width is 38\n" == out


def test_do_width_with_less_than_min_shows_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_width("3")
    out = stdout.getvalue()
    expected = "Minimum terminal width is 10\nTerminal width is 78\n"
    assert expected == out


def test_do_width_with_bad_arg_shows_error():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.do_width("bad")
    out = stdout.getvalue()
    expected = "Illegal width: bad\nTerminal width is 78\n"
    assert expected == out


def test_help_width():
    stdout = StringIO()
    mon = Monitor(stdout=stdout)
    mon.help_width()
    out = stdout.getvalue()
    assert out.startswith("width <columns>")


def test_external_memory():
    stdout = StringIO()
    memory = bytearray(65536)
    memory[10] = 0xFF
    mon = Monitor(memory=memory, stdout=stdout, putc_addr=None, getc_addr=None)
    assert 0xFF == memory[10], "memory must remain untouched"
    mon.do_mem("0008:000c")
    mon.do_fill("0000:0020 ab")
    assert 0xAB == memory[10], "memory must have been modified"
    out = stdout.getvalue()
    assert out.startswith(
        "0008:  00  00  ff  00  00"
    ), "monitor must see pre-initialized memory"


# command line options


def test_argv_mpu():
    argv = ["py65mon", "--mpu", "65c02"]
    stdout = StringIO()
    mon = Monitor(argv=argv, stdout=stdout)
    assert "65C02" == mon._mpu.name


def test_argv_mpu_invalid():
    argv = ["py65mon", "--mpu", "bad"]
    stdout = StringIO()
    try:
        Monitor(argv=argv, stdout=stdout)
    except SystemExit as exc:
        assert 1 == exc.code
    assert "Fatal: no such MPU." in stdout.getvalue()


def test_argv_goto():
    argv = ["py65mon", "--goto", "c000"]
    stdout = StringIO()
    memory = bytearray(0x10000)
    memory[0xC000] = 0xEA  # c000 nop
    memory[0xC001] = 0xEA  # c001 nop
    memory[0xC002] = 0x00  # c002 brk
    mon = Monitor(argv=argv, stdout=stdout, memory=memory)
    assert 0xC002 == mon._mpu.pc


def test_argv_load():
    try:
        with tempfile.NamedTemporaryFile("wb+", delete=False) as f:
            data = bytearray([0xAB, 0xCD])
            f.write(data)

        argv = ["py65mon", "--load", f.name]
        stdout = StringIO()
        mon = Monitor(argv=argv, stdout=stdout)
        assert list(data) == mon._mpu.memory[: len(data)]
    finally:
        os.unlink(f.name)


def test_argv_rom():
    try:
        with tempfile.NamedTemporaryFile("wb+", delete=False) as f:
            rom = bytearray(4096)
            rom[0] = 0xEA  # f000 nop
            rom[1] = 0xEA  # f001 nop
            rom[2] = 0x00  # f002 brk
            rom[-2] = 0xF000 & 0xFF  # fffc reset vector low
            rom[-3] = 0xF000 >> 8  # fffd reset vector high
            f.write(rom)

        argv = ["py65mon", "--rom", f.name]
        stdout = StringIO()
        mon = Monitor(argv=argv, stdout=stdout)
        assert list(rom) == mon._mpu.memory[-len(rom) :]
        assert 0xF002 == mon._mpu.pc
    finally:
        os.unlink(f.name)


def test_argv_input():
    argv = ["py65mon", "--input", "abcd"]
    stdout = StringIO()
    mon = Monitor(argv=argv, stdout=stdout)
    read_subscribers = mon._mpu.memory._read_subscribers
    assert 1 == len(read_subscribers)
    assert "getc" in repr(read_subscribers[0xABCD])


def test_argv_output():
    argv = ["py65mon", "--output", "dcba"]
    stdout = StringIO()
    mon = Monitor(argv=argv, stdout=stdout)
    write_subscribers = mon._mpu.memory._write_subscribers
    assert 1 == len(write_subscribers)
    assert "putc" in repr(write_subscribers[0xDCBA])


def test_argv_combination_rom_mpu():
    try:
        with tempfile.NamedTemporaryFile("wb+", delete=False) as f:
            rom = bytearray(4096)
            rom[0] = 0xEA  # f000 nop
            rom[1] = 0xEA  # f001 nop
            rom[2] = 0x00  # f002 brk
            rom[-2] = 0xF000 & 0xFF  # fffc reset vector low
            rom[-3] = 0xF000 >> 8  # fffd reset vector high
            f.write(rom)

        argv = [
            "py65mon",
            "--rom",
            f.name,
            "--mpu",
            "65c02",
        ]
        stdout = StringIO()
        mon = Monitor(argv=argv, stdout=stdout)
        assert "65C02" == mon._mpu.name
        assert list(rom) == mon._mpu.memory[-len(rom) :]
        assert 0xF002 == mon._mpu.pc
    finally:
        os.unlink(f.name)
