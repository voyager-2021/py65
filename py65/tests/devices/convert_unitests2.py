import re
import sys


def convert_unittest_to_pytest(lines):
    out = []
    in_class = False
    class_indent = None
    in_docstring = False
    docstring_delim = None
    current_func = None
    helper_names = ["_make_mpu", "_write"]

    for line in lines:
        # Detect class start
        if not in_class:
            m = re.match(r"^(\s*)class .*Tests", line)
            if m:
                in_class = True
                class_indent = len(m.group(1))
                # skip class line
                continue
            else:
                out.append(line)
                continue

        # Inside class: dedent by class_indent
        if len(line.strip()) == 0:
            # blank line: output newline
            out.append("\n")
            continue

        if len(line) > class_indent:
            dedented = line[class_indent:]
        else:
            dedented = line.lstrip()

        # Handle docstring start/end
        stripped = dedented.lstrip()
        if not in_docstring and re.match(r'^[ruRU]*("""|\'\'\')', stripped):
            in_docstring = True
            docstring_delim = stripped[:3]
        elif in_docstring and docstring_delim in stripped:
            in_docstring = False

        if not in_docstring:
            # Convert def line
            if re.match(r"^def ", dedented):
                dedented = re.sub(r"def (\w+)\(self.*\):", r"def \1():", dedented)
            # Convert asserts
            dedented = re.sub(
                r"self\.assertEqual\((.+?), (.+?)\)", r"assert \1 == \2", dedented
            )
            dedented = re.sub(
                r"self\.assertNotEqual\((.+?), (.+?)\)", r"assert \1 != \2", dedented
            )
            dedented = re.sub(
                r"self\.assertTrue\(([^,)]+)(?:,.*)?\)", r"assert \1", dedented
            )
            dedented = re.sub(
                r"self\.assertFalse\(([^,)]+)(?:,.*)?\)", r"assert not \1", dedented
            )
            # Remove self. from helper calls
            for helper in helper_names:
                dedented = re.sub(
                    r"self\.({})".format(re.escape(helper)), r"\1", dedented
                )
            # Also remove self. from any other calls if desired:
            dedented = re.sub(r"self\.(\w+)\(", r"\1(", dedented)

        out.append(dedented)

    return out


def main():
    if len(sys.argv) != 2:
        print("Usage: python convert.py input.py > output.py")
        return
    filename = sys.argv[1]
    with open(filename) as f:
        lines = f.readlines()
    new_lines = convert_unittest_to_pytest(lines)
    sys.stdout.writelines(new_lines)


if __name__ == "__main__":
    main()
