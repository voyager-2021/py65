import re
import sys


def convert_method_signature(line):
    # def test_foo(self): -> def test_foo():
    return re.sub(r"def (\w+)\(self.*\):", r"def \1():", line)


def convert_asserts(line):
    # assertEqual(a, b)
    line = re.sub(r"self\.assertEqual\s*\((.+?),\s*(.+?)\)", r"assert \1 == \2", line)
    # assertNotEqual(a, b)
    line = re.sub(
        r"self\.assertNotEqual\s*\((.+?),\s*(.+?)\)", r"assert \1 != \2", line
    )
    # assertTrue(x) and assertTrue(x, msg) --> assert x
    line = re.sub(r"self\.assertTrue\s*\(([^,)]+)(?:,.*)?\)", r"assert \1", line)
    # assertFalse(x) and assertFalse(x, msg) --> assert not x
    line = re.sub(r"self\.assertFalse\s*\(([^,)]+)(?:,.*)?\)", r"assert not \1", line)
    return line


def remove_self_calls(line):
    # Remove self. from calls like self._make_mpu(), self._write()
    # But do NOT remove from docstrings/comments (handled outside)
    # Also avoid removing in strings
    # We'll keep it simple: remove self. only if followed by a word and '('
    # and line is not a comment line (starts with #)
    if line.lstrip().startswith("#"):
        return line
    # Remove self. before method calls
    return re.sub(r"\bself\.(\w+)\(", r"\1(", line)


def line_uses_helper(line, helper_names):
    for h in helper_names:
        if f"{h}(" in line:
            return True
    return False


def process_lines(lines):
    in_class = False
    in_docstring = False
    docstring_delim = None
    new_lines = []
    class_indent = None
    current_func = None
    helper_names = ["_make_mpu", "_write"]
    params_for_funcs = {}

    for line in lines:
        stripped = line.lstrip()

        # Detect start/end of docstring (""" or ''')
        if not in_docstring:
            m = re.match(r'\s*(?P<quote>["\']{3})', stripped)
            if m:
                in_docstring = True
                docstring_delim = m.group("quote")
        else:
            if docstring_delim in stripped:
                in_docstring = False

        # Detect class line
        if not in_docstring and re.match(r"\s*class .*Tests.*:", line):
            in_class = True
            class_indent = len(line) - len(stripped)
            # Don't append the class line (remove class)
            continue

        if in_class:
            # Dedent all lines inside the class by class_indent
            # But blank lines stay blank
            if line.strip() == "":
                new_lines.append("")
                continue

            # Remove class indent spaces from line (if possible)
            if len(line) > class_indent:
                line = line[class_indent:]
            else:
                line = line.lstrip()

            # Detect method def lines
            if not in_docstring and re.match(r"\s*def ", line):
                line = convert_method_signature(line)
                # Record current function
                m = re.match(r"def (\w+)\(", line)
                current_func = m.group(1) if m else None
                params_for_funcs[current_func] = set()
                new_lines.append(line)
                continue

            if in_docstring or stripped.startswith("#"):
                # docstrings or comments, just add line as is (already dedented)
                new_lines.append(line)
                continue

            # Regular code inside method
            line = convert_asserts(line)
            line = remove_self_calls(line)

            # Check helper usage
            if current_func and line_uses_helper(line, helper_names):
                if "_make_mpu(" in line:
                    params_for_funcs[current_func].add("make_mpu")
                if "_write(" in line:
                    params_for_funcs[current_func].add("write_memory")

            new_lines.append(line)

        else:
            # Outside class, just copy line as-is
            new_lines.append(line)

    # Add function params (make_mpu, write_memory) where needed
    for i, line in enumerate(new_lines):
        m = re.match(r"def (\w+)\(\):", line)
        if m:
            func = m.group(1)
            params = params_for_funcs.get(func, set())
            if params:
                params_str = ", ".join(sorted(params))
                new_lines[i] = f"def {func}({params_str}):"

    return new_lines


def main(filename):
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = process_lines(lines)
    sys.stdout.write(
        "".join(line if line.endswith("\n") else line + "\n" for line in new_lines)
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_unittest_to_pytest.py <test_file.py>")
        sys.exit(1)
    main(sys.argv[1])
