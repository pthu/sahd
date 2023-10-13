import pypandoc
import argparse
import re
from os import remove

TEMP = "temp.txt"


def read_args():
    parser = argparse.ArgumentParser(description='converts Word file into text-file and reformats some lines to better suit Markdown in SAHD',
                                     usage='use "%(prog)s --help" for more information',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("input", help="input Word-file")
    parser.add_argument("output", help="ouput text-file")
    args = parser.parse_args()
    input = args.input
    output = args.output

    return input, output


def hebrew_character(c):
    return 0x0590 <= ord(c) <= 0x05FF or 0xFB1D <= ord(c) <= 0xFB4F


def hebrew(line):
    s = ""
    in_hebrew = False
    char = line[0]
    prev_char = char
    i = 1
    while i < len(line):
        next_char = line[i]
        if hebrew_character(char):
            if not in_hebrew:
                if not prev_char == "":
                    s += ' '
                s += '<span dir="rtl">'
                in_hebrew = True
        else:
            if in_hebrew:
                if char == " " and hebrew_character(next_char):
                    in_hebrew = True
                else:
                    s += '</span>'
                    in_hebrew = False
        s += char
        prev_char = char
        char = next_char
        i += 1

    s += char
    if in_hebrew:
        s += '<span dir="rtl">'

    return s


def footnotes(line):
    superscripts ={0x00B2: 0x0032, 0x00B3: 0x33, 0x00B9: 0x31, 0x2070: 0x30, 0x2074: 0x34, 0x2075: 0x35, 0x2076: 0x36, 0x2077: 0x37, 0x2078: 0x38, 0x2079: 0x39}
    s = ""
    i = 0
    while i < len(line):
        char = line[i]
        if 0x2080 <= ord(char) <= 0x2089:
            # subscript numbers
            next_char = line[i + 1] if i < len(line) else ""
            if 0x2080 <= ord(next_char) <= 0x2089:
                s += f"[^{chr(ord(char) - 0x2050)}{chr(ord(next_char) - 0x2050)}]"
                i += 1
            else:
                s += f"[^{chr(ord(char) - 0x2050)}]"
        if ord(char) in superscripts:
            # supercript numbers
            next_char = line[i + 1] if i < len(line) else ""
            if ord(next_char) in superscripts:
                s += f"[^{chr(superscripts[ord(char)])}{chr(superscripts[ord(next_char)])}]"
                i += 1
            else:
                s += f"[^{chr(superscripts[ord(char)])}]"
        else:
            s += char
        i += 1
    return s


def convert(input, output):

    headers = ["Introduction", "Root and Comparative Material", "Formal Characteristics", "Syntagmatics", "Versions",
               "Ancient Versions", "Lexical/Semantic Fields", "Lexical/Semantic Field(s)", "Exegesis", "Conclusion", "Bibliography"]
    pypandoc.convert_file(input, 'plain', outputfile=TEMP)

    with open(output, "w") as f:
        with open(TEMP, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = re.sub(r"^\s*([0-9]+).?(\s*↑)(.*)", r"[^\1]: \3", line)        # footnotes
                line = re.sub(r"^\s*([0-9]+\.\s.*)", r"## \1", line)                  # headers
                line = re.sub(r"^\s*([0-9]\.[0-9])(\s.*$)", r"###\1 \2", line)        # main sub-headers
                line = re.sub(r"^\s*([a-zA-Z]?[0-9.]+)(\s.*$)", r"**\1** \2", line)   # other sub-headers
                if line.strip() in headers:
                    line = "##" + line.strip()
                if line.strip().startswith("**"):
                    line = "\n" + line
                line = hebrew(line)
                line = footnotes(line)
                f.write(line)

    remove(TEMP)
    print(f"{input} converted to {output}")


input, output = read_args()
convert(input, output)