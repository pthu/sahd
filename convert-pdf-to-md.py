import fitz
import re
import argparse
from os import remove

TEMP = "temp.txt"


def read_args():
    parser = argparse.ArgumentParser(description='converts .pdf file into text-file and reformats some lines to better suit Markdown in SAHD',
                                     usage='use "%(prog)s --help" for more information',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("input", help="input pdf-file")
    parser.add_argument("output", help="ouput text-file")
    parser.add_argument("md_formatting", nargs='?', default=True, help="is Markdown formatting applied?")
    args = parser.parse_args()
    input = args.input
    output = args.output
    formatting = not str(output).startswith("temp.") or args.md_formatting

    return input, output, formatting


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


def convert(input, output, md_formatting):
    doc = fitz.open(input)
    text = ""
    for i in range(doc.page_count):
        text += doc[i].get_text("text")
    with open(TEMP, "w") as fi:
        fi.write(text)

    with open(output, "w") as f:
        with open(TEMP, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if md_formatting:
                    line = re.sub(r"^\s*([0-9]+).?(\s*↑)(.*)", r"[^\1]: \3", line)        # footnotes
                    line = re.sub(r"^\s*([0-9]+\.\s.*)", r"## \1", line)                  # headers
                    line = re.sub(r"^\s*([0-9]\.[0-9])(\s.*$)", r"###\1 \2", line)        # main sub-headers
                    line = re.sub(r"^\s*([a-zA-Z]?[0-9.]+)(\s.*$)", r"**\1** \2", line)   # other sub-headers
                    line = hebrew(line)
                    if line.strip().lower() == "introduction":
                        line = "##Introduction\n"
                    if line.strip().lower() == "conclusion":
                        line = "##Conclusion\n"
                    if line.strip().lower() == "bibliography":
                        line = "##Bibliography\n"
                    if line.strip().lower() == "notes":
                        line = "##Notes\n"
                    if line.strip().startswith("**"):
                        line = "\n" + line
                else:
                    line += "<br>"
                f.write(line)

    remove(TEMP)
    print(f"{input} converted to {output}")


input, output, md_formatting = read_args()
convert(input, output, md_formatting)