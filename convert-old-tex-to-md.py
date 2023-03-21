import argparse
import re
from os import remove

TEMP = "temp.txt"


def read_args():
    parser = argparse.ArgumentParser(description='converts Tex file to Markdown text file',
                                     usage='use "%(prog)s --help" for more information',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("input", help="input text-file")
    parser.add_argument("output", help="ouput text-file")
    args = parser.parse_args()
    input = args.input
    output = args.output

    return input, output


def replace_bold(line):
    for i in range(5):
        line = re.sub(r"(.*)\\textbf\s*{(.*)}(.*)", r"\1**\2**\3", line)
    return line


def replace_italics(line):
    for i in range(5):
        line = re.sub(r"(.*)\\textit\s*{(.*?)}(.*)", r"\1*\2*\3", line)
    return line


def replace_vspace(line):
    for i in range(5):
        line = re.sub(r"(.*)\\vspace{.*}(.*)", r"\1\2", line)
    return line


def replace_superscript_1(line):
    for i in range(5):
        line = re.sub(r"(.*)\\sup(.*?)[)\\;.](.*)", r"\1<sup>\2</sup>\3", line)
    return line


def replace_superscript_2(line):
    for i in range(5):
        line = re.sub(r"(.*)\\nsupscr{(.*?)}(.*)", r"\1<sup>\2</sup>\3", line)
    return line


def replace_hebrew(line):
    for i in range(5):
        line = re.sub(r"(.*)\\RL{\\Hbr (.*)}(.*)", r"\1\2\3", line)
    for i in range(5):
        line = re.sub(r"(.*){\\Hbr (.*)}(.*)", r"\1\2\3", line)
    return line


def replace_greek(line):
    for i in range(5):
        line = re.sub(r"(.*){\\Gr (.*)}(.*)", r"\1\2\3", line)
    return line


def replace_syrian(line):
    for i in range(5):
        line = re.sub(r"(.*){\\Syr (.*)}(.*)", r"\1\2\3", line)
    return line


def replace_textsc(line):
    for i in range(5):
        line = re.sub(r"(.*)\\textsc{(.*?)}(.*)", r"\1\2\3", line)
    return line


def replace_label(line):
    m = re.search(r"(.*)\\pslabel{(.*?)}(.*)", line)
    if m:
        return m.group(1) + m.group(3) + " {#" + m.group(2).lower() + "}"
    else:
        return line


# def footnotes(input, output):
#     with open(output, "w") as f:
#         with open(input, 'r') as file:
#             lines = file.readlines()
#             in_comment = False
#             for line in lines:
#                 c_start = line.find("\\endnote{")
#                 if c_start >= 0:
#                     in_comment = True
#                     line_begin = line[0:c_start]
#                     line_rest = ""
#                     comment = ""
#                     for c in line[c_start + 9:]:
#                         if c == "}":
#                             in_comment = False
#                             print(comment)
#                         elif c == "}":
#                             in_comment = True
#                         if in_comment:
#                             comment += c
#                         else:
#                             line_rest += c
#                     f.write(line_begin + line_rest)
#                 else:
#                     f.write(line)
#         f.close()
#
#
def footnotes(input, output):
    with open(output, "w") as f:
        with open(input, 'r') as file:
            text = file.read()
            for i in range(100):
                text = text
                # text = re.sub(r"(.*)Root([.\s\S]*?)word", r"\1\2", text)
                text = re.sub(r"(.*)\\endnote{([.\s\S]*?)}([.\s\S]*)", r"\1\3", text)
                # text = re.sub(r"(.*)\\endnote{([.|\n]*)}([.|\n]*)", r"\1\3", text)
        f.write(text)
    f.close()


def replacements(input, output):
    beqa = "בֶּקַע"
    with open(output, "w") as f:
        with open(input, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = replace_bold(line)
                line = replace_italics(line)
                line = replace_vspace(line)
                line = replace_superscript_1(line)
                line = replace_superscript_2(line)
                line = replace_hebrew(line)
                line = replace_greek(line)
                line = replace_syrian(line)
                line = replace_textsc(line)

                line = replace_label(line)
                # line = re.sub(r"(.*)\\pslabel{(.*?)}(.*)", r"\1\3{#\2}", line)              # label
                line = re.sub(r"(.*)(\\noindent)(.*)", r"\1\3", line)              # noindent
                line = re.sub(r"(.*)(\\newline)(.*)", r"\1<br>\3", line)              # newline
                # line = re.sub(r"(.*)\\endnote.*", r"\1", line)              # endnote
                line = re.sub(r"^\\sect\s*{(.*)}(.+)", r"##\1\2", line)              # section header
                line = re.sub(r"^\\subsect\s*{(.*)}(.+)", r"###\1\2", line)              # subsection header
                line = re.sub(r"^\*\*Introduction\*\*\s*({.*})\s*", r"##Introduction\1", line)              # Introduction

                line = line.replace("\\ ", " ")              # space
                line = line.replace("\\xx", "x")              # beka
                line = line.replace("\\ldots", "...")              # dots
                line = line.replace("$\\surd$", "√")              # √
                line = line.replace("$\\rightarrow$", "→")              # →
                line = line.replace("\\S\\,", "§")              # §
                line = line.replace("\\nsupscr{$\\prime$}", "′")              # ′
                line = line.replace("\\beqa", beqa)              # beqa
                line = line.replace("]", "ְְ")              # beka
                line = line.replace("v", "שׁ")              # beka
                line = line.replace("'", "ַ")              # beka
                line = line.replace("p", "פַ")              # beka
                line = line.replace("T", "תּ")              # beka
                line = line.replace("Iy", "יִ")              # beka
                line = line.replace("µ", "ם")              # beka


                line = line.replace("`", "\'")

                s = line.strip()
                if s.startswith("\\hangindent") or s.startswith("\\pagebreak")  or s.startswith("\\setlength")\
                        or  s.startswith("%") :
                    continue

                f.write(line)
        f.close()


def convert(input, output):
    replacements(input, TEMP)
    footnotes(TEMP, output)
    remove(TEMP)
    print(f"{input} converted to {output}")


input, output = read_args()
convert(input, output)