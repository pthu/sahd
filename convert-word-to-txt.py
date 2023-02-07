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
                f.write(line)

    remove(TEMP)
    print(f"{input} converted to {output}")


input, output = read_args()
convert(input, output)