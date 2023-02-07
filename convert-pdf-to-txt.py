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
    parser.add_argument("md_formatting", nargs='?', default=False, help="is Markdown formatting applied?")
    args = parser.parse_args()
    input = args.input
    output = args.output
    formatting = not str(output).startswith("temp.") or args.md_formatting

    return input, output, formatting


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
                    line = re.sub(r"^\s*([a-zA-Z]?[0-9.]+)(\s.*$)", r"**\1** \2", line)   # sub-headers
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