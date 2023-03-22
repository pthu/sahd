import argparse
import re
import chardet
from os import remove

TEMP = "temp.txt"
TEMP2 = "temp2.txt"

definitions = {}
greek = {"a": "α", "b": "β", "g": "γ", "d": "δ", "e": "ε", "z": "ζ", "h": "η", "q": "θ", "i": "ι",
         "k": "κ", "l": "λ", "m": "μ", "n": "ν", "x": "ξ", "o": "ο", "p": "π", "r": "ρ", "s": "σ",
         "t": "τ", "u": "υ", "f": "φ", "c": "χ", "y": "ψ", "w": "ω", '"': "ς",
         "aj": "ἀ", "aJ": "ἁ", "a;": "ὰ", "av": "ά", "a*": "ἅ", "a’": "ᾶ", "a/": "ᾳ", "a[": "ᾰ",
         "ej": "ἐ", "eJ": "ἑ", "e;": "ὲ", "ev": "έ", "e*": "ἕ",
         "hj": "ἠ", "hJ": "ἡ", "h;": "ὴ", "hv": "ή", "h*": "ἥ", "h’": "ῆ", "h/": "ῃ",
         "ij": "ἰ", "iJ": "ἱ", "i;": "ὶ", "iv": "ί", "i*": "ἵ", "i’": "ῖ", "i[": "ῐ",
         "oj": "ὀ", "oJ": "ὁ", "o;": "ὸ", "ov": "ό", "o*": "ὅ",
         "uj": "ὐ", "uJ": "ὑ", "u;": "ὺ", "uv": "ύ", "u*": "ὕ", "u’": "ῦ", "u[": "ῠ",
         "wj": "ὠ", "wJ": "ὡ", "w;": "ὼ", "wv": "ώ", "w*": "ὥ", "w’": "ῶ", "w/": "ῳ",
         " ": " "
         }
hebrew = {"a": "א", "b": "ב", "B": "בּ", "g": "ג", "G": "גּ", "d": "ד", "D": "דּ", "h": "ה", "H": "הּ", "w": "ו",
          "W": "וּ", "z": "ז", "Z": "זּ", "j": "ח", "f": "ט", "F": "טּ", "y": "י", "Y": "יּ", "k": "כ", "K": "כּ",
          "û": "ך", "ò": "ךָ", "è": "ךְ", "l": "ל", "L": "לּ", "m": "מ", "M": "מּ", "µ": "ם", "n": "נ", "N": "סּ",
          "ö": "ן", "s": "ס", "S": "ףּ", "[": "ע", "p": "פ", "P": "צּ", "¹": "ף", "x": "צ", "X": "קּ", "Å": "ץ",
          "q": "ק", "Q": "רּ", "r": "ר", "R": "שּ", "c": "שׂ", "C": "שּׂ", "v": "שׁ", "V": "שּׁ", "t": "ת", "T": "וֹ",
          ";b": "בָ", ":g": "גָ", ":d": "דָ", "'b ": "בַ", '"g": "גַ", '"d": "דַ", "eb": "בֵ", "Eg": "גֵ", "Ed": "דֵ",
          ",b": "בֶ", "<g": "גֶ", "<d": "דֶ", "ib": "בִ", "Ig": "גִ", "Id": "דִ", "ob": "בֹ", "Og": "גֹ", "og": "גֹ",
          "od": "דֹ", "¿bw": "בֹו", "ub": "בֻ", "Ug": "גֻ", "Ud": "דֻ", "]b": "בְ", "Òg": "גְ", "*j": "חֲ", "Ôj": "חֱ",
          "Õj": "חֳ", "mA": "מ־"
          }
hebrew_points = {"]": 0x05B0, "<": 0x05B6, "'": 0x05B7, ";": 0x05B8, "A": 0x05BF, "e": 0x05B5, ",": 0x05B6, "A": 0x05BF}

def read_args():
    parser = argparse.ArgumentParser(description='converts TeX file to Markdown text file',
                                     usage='use "%(prog)s --help" for more information',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("input", help="input text-file")
    parser.add_argument("output", help="ouput text-file")
    args = parser.parse_args()
    input = args.input
    output = args.output

    return input, output


def reverse(word):
    return "".join(reversed(word))


def replace_def(line):
    m = re.search(r"(.*)\\def\\(.*?){(.*?)}(.*)", line)
    if m:
        line = m.group(1) + m.group(4)
        definitions[m.group(2)] = m.group(3)
    return line


def replace_defined_reference(line):
    for d in definitions.keys():
        line = line.replace("\\" + d, definitions[d])
    return line


def replace_bold(line):
    for i in range(5):
        line = re.sub(r"(.*)\\textbf{(.*?)}(.*)", r"\1**\2**\3", line)
    return line


def replace_italics(line):
    for i in range(5):
        line = re.sub(r"(.*)\\textit{(.*?)}(.*)", r"\1*\2*\3", line)
    return line


def replace_vspace(line):
    for i in range(5):
        line = re.sub(r"(.*)\\vspace{.*}(.*)", r"\1\2", line)
    return line


def replace_superscript_1(line):
    for i in range(5):
        line = re.sub(r"(.*)\\n?sups(?:cr)?{(.*?)}(.*)", r"\1<sup>\2</sup>\3", line)
    return line


def replace_superscript_2(line):
    conversion = {"G": "LXX", "M": "MT", "A": "αʹ", "Ps": "PsJ", "Sm": "Smr"}
    for i in range(5):
        m = re.search(r"(.*)\\sup([a-zA-Z]*)(|\\|;|.)(.*)", line)
        if m:
            sup = m.group(2)
            if sup in conversion:
                sup = conversion[sup]
            line = m.group(1) + f"<sup>{sup}</sup>" + m.group(3) + m.group(4)
    return line


def replace_hebrew(line):
    for i in range(5):
        m = re.search(r"(.*)\\RL{\\Hbr (.*?)}(.*)", line)
        if not m:
            m = re.search(r"(.*)\\beginR{\\[sn]mhebr (.*?)}\\endR(.*)", line)
        if m:
            hbr = m.group(2).replace("\symbol{125}", "*")
            # print(m.group(2))
            print(hbr)
            print(line)
            h = ""
            i = 0
            while i < len(hbr):
                char = hbr[i]
                if i < len(hbr) - 1:
                    next_char = hbr[i + 1]
                else:
                    next_char = ""
                two_chars = char + next_char
                if two_chars in hebrew.keys():
                    h += hebrew[two_chars]
                    i += 1
                else:
                    if char in hebrew_points:
                        h += chr(hebrew_points[char])
                    else:
                        h += hebrew[char]
                i += 1
            line = m.group(1) + reverse(h) + m.group(3)
        else:
            break
        print(line)
    return line


def replace_greek(line):
    # for i in range(5):
    #     line = re.sub(r"(.*){\\Gr (.*)}(.*)", r"\1\2\3", line)
    for i in range(5):
        m = re.search(r"(.*){\\[ns]mody (.*)}(.*)", line)
        if m:
            gr = m.group(2).replace("\symbol{123}", "*")
            if gr.find("\\-") >= 0:
                gr = gr.replace("\\-", "")
                print(f"\- removed {gr}")
            g = ""
            i = 0
            while i < len(gr):
                char = gr[i]
                if i < len(gr) - 1:
                    next_char = gr[i + 1]
                else:
                    next_char = ""
                two_chars = char + next_char
                if two_chars in greek.keys():
                    g += greek[two_chars]
                    i += 1
                else:
                    g += greek[char]
                i += 1
            line = m.group(1) + g + m.group(3)
        else:
            break
    return line


# def replace_syrian(line):
#     for i in range(5):
#         line = re.sub(r"(.*){\\Syr (.*)}(.*)", r"\1\2\3", line)
#     return line


def replace_textsc(line):
    for i in range(5):
        line = re.sub(r'(.*)\\textsc{(.*?)}(.*)', r'\1<span style="text-transform:uppercase;">\2</span>\3', line)
        # line = re.sub(r'(.*)\\textsc{(.*?)}(.*)', r'\1<span style="font-variant:small-caps;">\2</span>\3', line)
    return line


def replace_footnotesize(line):
    for i in range(5):
        line = re.sub(r'(.*?){\\footnotesize\\plaat(.*)}', r'\1\2', line)
        line = re.sub(r'(.*?)\\footnotesize\\plaat(.*)', r'\1\2', line)
        line = re.sub(r'(.*){\\footnotesize ([a-zA-Z0-9]*?)}(.*)', r'\1\2\3', line)
    return line


def replace_reference(line):
    for i in range(5):
        line = re.sub(r'(.*)\\hyperref\[(.*?)]{(.*?)}(.*)', r'\1<a href="#\2">\3</a>\4', line)
    return line


def replace_label(line):
    for i in range(1):
        line = re.sub(r'(.*)\\pslabel{(.*?)}(.*)', r'\1<span id="\2">\3</span>', line)
    return line


def replace_enlargethispage(line):
    for i in range(1):
        line = re.sub(r"(.*)\\enlargethispage{(.*?)}(.*)", r"\1\3", line)
    return line


def replace_sil(line):
    for i in range(5):
        line = re.sub(r"(.*){\\Sil(.*?)}(.*)", r"\1\2\3", line)
    return line


def replace_includegraphics(line):
    for i in range(5):
        line = re.sub(r"(.*){\\includegraphics{(.*?)}(.*?)}(.*)", r"\1![](../photos/\2)\3", line)
    return line


def replace_href(line):
    for i in range(5):
        line = re.sub(r'(.*)\\href{(.*?)}{(.*?)}(.*)', r'\1<a href=\2 target="_blank">\3</a>\4', line)
    return line


def replace_linebreak(line):
    for i in range(1):
        line = re.sub(r"(.*)\\linebreak(.*)", r"\1<br>\2", line)
    return line


def replace_tab(line):
    for i in range(5):
        line = re.sub(r"(.*)	(.*)", r"\1&emsp;&emsp;\2", line)
    return line


def remove_hfill(line):
    for i in range(5):
        line = re.sub(r"(.*)\\hfill(.*)", r"\1\2", line)
    return line


def remove_hspace(line):
    for i in range(5):
        line = re.sub(r"(.*)\\hspace\*?{.*?}(.*)", r"\1\2", line)
    return line


def remove_scalebox(line):
    for i in range(5):
        line = re.sub(r"(.*)\\scalebox{.*?}(.*)", r"\1\2", line)
    return line


def remove_large(line):
    for i in range(1):
        line = re.sub(r"(.*)\\(LARGE|large)(.*)", r"\1\3", line)
    return line


def remove_small(line):
    for i in range(1):
        line = re.sub(r"(.*)\\(SMALL|small)(.*)", r"\1\3", line)
    return line


def remove_comment(line):
    for i in range(1):
        line_orig = line
        line = re.sub(r"(.)(.*)%.*$", r"\1\2", line)
        # if line_orig != line:
        #     print("inline comment removed on line: " + line_orig)
    return line


def remove_theendnotes(line):
    for i in range(1):
        line = re.sub(r"(.*)\\theendnotes(.*)", r"\1\2", line)
    return line


def remove_renewcommand(line):
    for i in range(1):
        line = re.sub(r"(.*)\\renewcommand{.*?}{.*}(.*)", r"\1\2", line)
    return line


def remove_last_backslash(line):
    for i in range(1):
        line = re.sub(r"(.*)\\\\ *$", r"\1<br>", line)
        line = re.sub(r"(.*)\\ *$", r"\1", line)
    return line


def multiline_replacements(input, output):
    footnotes = []
    with open(output, "w") as f:
        with open(input, 'r') as file:
            text = file.read()
            # Footnotes
            for i in range(100):
                m = re.search(r"([.\s\S]*?)\\(?:endnote|footnote){([.\s\S]*?)}([.\s\S]*)", text)
                if m:
                    footnote = m.group(2)
                    footnotes.append(footnote)
                    text = m.group(1) + f"[^{i + 1}]" + m.group(3)
                else:
                    break
            # Italics
            for i in range(100):
                m = re.search(r"([.\s\S]*?)\\textit{([.\s\S]*?)}([.\s\S]*)", text)
                if m:
                    text = f"{m.group(1)}*{m.group(2)}*{m.group(3)}"
                else:
                    break

        for i, footnote in enumerate(footnotes):
            text += f"[^{i + 1}]: " + footnote.replace("\n", " ") + "\n"
        f.write(text)
    f.close()


def indents(input, output):
    indent = ""
    with open(output, "w") as f:
        with open(input, 'r') as file:
            lines = file.readlines()
            for line in lines:
                m = re.search(r"(.*)\\hangindent ([0-9.]*)cm(.*)", line)
                if m:
                    indent = m.group(2)
                    line = m.group(1) + m.group(3)
                m = re.search(r"(.*)\\noindent(.*)", line)
                if m:
                    indent = ""
                    line = m.group(1).strip() + m.group(2).strip()
                if indent and line.strip() != "":
                    tabs = ""
                    nr_tabs = round(float(indent) / 0.6)
                    for i in range(nr_tabs):
                        tabs += "&emsp;"
                    line = f"{tabs}{line}<br>"
                f.write(line)
        f.close()


def replace_special(line):
    line = line.replace("\\nsupscr{$\\prime$}", "′")# ′
    line = line.replace("\\ ", " ")                 # space
    line = line.replace("\\xx", "x")                # x
    line = line.replace("\\ldots", "...")           # ...
    line = line.replace("$\\surd$", "√")            # √
    line = line.replace("$\\rightarrow$", "→")      # →
    line = line.replace("\\S\\,", "§")              # §
    line = line.replace("{\\S}", "§")              # §
    # line = line.replace("\\beqa", "&rlm;" + beqa + "&lrm;")   # beqa
    line = line.replace("`", "\'")                  # '
    line = line.replace("{\\ain}", "ʿ")              # ʿ
    line = line.replace("\\ain", "ʿ")              # ʿ
    line = line.replace("{\\alef}", "ʾ")              # ʾ
    line = line.replace("{\\sh}", "ḫ")              # ḫ
    line = line.replace("\\d{h}", "ḥ")              # ḥ
    line = line.replace("\\d{H}", "Ḥ")              # Ḥ
    line = line.replace("\\v{s}", "š")              # š
    line = line.replace("\\v{S}", "Š")              # Š
    # \^{U}\b{K}
    line = line.replace("{\\ss}", "ß")              # ß
    line = line.replace('\\"{A}', "Ä")              # Ä
    line = line.replace('\\"{a}', "ä")              # ä
    line = line.replace('\\"{u}', "ü")              # ü
    line = line.replace('\\"{u*', "ü")              # ü
    line = line.replace('\\^{U}', "Û")              # Û
    line = line.replace('\\"{o}', "ö")              # ö
    line = line.replace("\\={a}", "ā")              # ā
    line = line.replace("\\'{\\i}", "í")              # í
    line = line.replace("\\b{K}", "Ḵ")              # Ḵ
    line = line.replace("\\ges", "Ges")              # Ges
    line = line.replace("\\mt", "MT")              # MT
    line = line.replace("\\lxx", "LXX")              # LXX
    line = line.replace("\\sept", "LXX")              # LXX
    line = line.replace("\\tg", "T")              # T
    line = line.replace("\\targ", "T")              # T
    line = line.replace("{\\peshi}", "S")              # S
    line = line.replace("\\peshi", "S")              # S
    line = line.replace("\\sam", "SP")              # SP
    line = line.replace("\\vulg", "V")              # V
    line = line.replace("\\aq", "α´")              # α´
    line = line.replace("\\th", "θ´")              # θ´
    line = line.replace("\\sym", "σ´")              # σ´

    # doubtful
    line = line.replace("\\#\\,", "#")              # #
    line = line.replace("\\/,", "’")              # ’
    line = line.replace("\\/", "")              # empty
    line = line.replace("\\,", " ")              # space
    line = line.replace("\\ ,", "")              # space

    return line


def replacements(input, output):
    with open(output, "w") as f:
        with open(input, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip().startswith("%"):
                    continue

                line = replace_special(line)

                line = replace_label(line)
                line = replace_enlargethispage(line)
                line = replace_bold(line)
                line = replace_italics(line)
                line = replace_vspace(line)
                line = replace_superscript_1(line)
                line = replace_superscript_2(line)
                line = replace_hebrew(line)
                line = replace_greek(line)
                # line = replace_syrian(line)
                line = replace_textsc(line)
                line = replace_footnotesize(line)
                line = replace_reference(line)
                line = replace_sil(line)
                line = replace_includegraphics(line)
                line = replace_href(line)
                line = replace_linebreak(line)

                line = remove_hfill(line)
                line = remove_hspace(line)
                line = remove_scalebox(line)
                line = remove_large(line)
                line = remove_small(line)
                line = remove_comment(line)     # check occurences!
                line = remove_theendnotes(line)
                line = remove_renewcommand(line)
                line = remove_last_backslash(line)
                # line = replace_tab(line)
                line = replace_def(line)
                line = replace_defined_reference(line)

                # line = re.sub(r"(.*)(\\noindent)(.*)", r"\1\3", line)              # noindent
                line = re.sub(r"(.*)(\\newline)(.*)", r"\1<br>\3", line)              # newline
                line = re.sub(r"^\\sect*{(.*)}(.+)", r"##\1\2", line)              # section header
                line = re.sub(r"^\\subsect*{(.*)}(.+)", r"###\1\2", line)              # subsection header
                line = re.sub(r"\*\*(.*)Introduction\*\*(.*)", r"##\1Introduction\2", line)              # Introduction
                line = re.sub(r"\\bigskip", r"", line)              # \bigskip => empty
                line = re.sub(r"\\-", r"", line)              # \- => empty


                s = line.strip()
                if s.startswith("\\pagebreak") or s.startswith("\\setlength") \
                        or s.startswith("\\markboth") or s.startswith("\\vspace") or s.startswith("\\thispagestyle")\
                        or s.startswith("\\setcounter") or s.startswith("\\normalsize") or s.startswith("\\newpage") \
                        or s.startswith("\\pagestyle") or s.startswith("%"):
                    continue
                # This needs still to be checked that no relevant information is missed (if we want to make md markings over more lines)
                if s.startswith("\\begin{") or s.startswith("\\end{"):
                    continue

                f.write(line)
        f.close()


def write_as_utf8(input, output):
    with open(input, 'rb') as rawdata:
        encoding = chardet.detect(rawdata.read())['encoding']
        print(encoding)
    with open(output, "w", encoding='utf8') as f_out:
        if encoding == "Windows-1254":
            with open(input, 'r') as f_in:
                text = f_in.read()
        else:
            with open(input, 'r', encoding=encoding) as f_in:
                text = f_in.read()
        f_out.write(text)


def convert(input, output):
    write_as_utf8(input,  TEMP)
    replacements(TEMP, TEMP2)
    multiline_replacements(TEMP2, TEMP)
    indents(TEMP, output)
    remove(TEMP)
    remove(TEMP2)
    print(f"{input} converted to {output}")


input, output = read_args()
convert(input, output)

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
# def replace_large(line):
#     for i in range(5):
#         line = re.sub(r"(.*)\\LARGE|\\large[ -]*(.*)", r"\1\2", line)
#     return line


