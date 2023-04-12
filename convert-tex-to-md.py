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
         "G": "Γ",
         "aj": "ἀ", "aJ": "ἁ", "a;": "ὰ", "av": "ά", "a*": "ἅ", "a’": "ᾶ", "a/": "ᾳ", "a[": "ἄ",
         "ej": "ἐ", "eJ": "ἑ", "e;": "ὲ", "ev": "έ", "e*": "ἕ", "e[": "ἔ",
         "hj": "ἠ", "hJ": "ἡ", "h;": "ὴ", "hv": "ή", "h*": "ἥ", "h’": "ῆ", "h/": "ῃ", "h[": "ἤ",
         "ij": "ἰ", "iJ": "ἱ", "i;": "ὶ", "iv": "ί", "i*": "ἵ", "i’": "ῖ", "i[": "ἴ", "lv": "ƛ",
         "oj": "ὀ", "oJ": "ὁ", "o;": "ὸ", "ov": "ό", "o*": "ὅ", "o[": "ὄ",
         "uj": "ὐ", "uJ": "ὑ", "u;": "ὺ", "uv": "ύ", "u*": "ὕ", "u’": "ῦ", "u[": "ὔ", "u@": "ὕ",
         "wj": "ὠ", "wJ": "ὡ", "w;": "ὼ", "wv": "ώ", "w*": "ὥ", "w’": "ῶ", "w/": "ῳ", "w[": "ὤ",
         " ": " ", "/": "/"
         }
hebrew = {"a": "א", "b": "ב", "B": "בּ", "g": "ג", "G": "גּ", "d": "ד", "D": "דּ", "h": "ה", "H": "הּ", "w": "ו",
          "W": "וּ", "z": "ז", "Z": "זּ", "j": "ח", "f": "ט", "F": "טּ", "y": "י", "Y": "יּ", "k": "כ", "K": "כּ",
          "û": "ך", "ò": "ךָ", "è": "ךְ", "l": "ל", "L": "לּ", "m": "מ", "M": "מּ", "µ": "ם", "n": "נ", "N": "סּ",
          "ö": "ן", "s": "ס", "S": "ףּ", "[": "ע", "p": "פ", "P": "פּּ", "¹": "ף", "x": "צ", "X": "קּ", "Å": "ץ",
          "q": "ק", "Q": "רּ", "r": "ר", "R": "שּ", "c": "שׂ", "C": "שּׂ", "v": "שׁ", "V": "שּׁ", "t": "ת", "T": "תֹּ",
          "": "ש", "ç": "ש", "ˆ": "ו", "&": "ף", "π": "ף", "A": "&thinsp;־", "/": "/"
          }
hebrew_points = {"]": 0x05B0, "Ò": 0x05B0, "“": 0x05B0, "Ô": 0x05B1, "*": 0x05B2, "Õ": 0x05B3, "i": 0x05B4, "I": 0x05B4,
                 "e": 0x05B5, "E": 0x05B5, ",": 0x05B6, "<": 0x05B6, "'": 0x05B7, '"': 0x05B7, ";": 0x05B8,
                 ":": 0x05B8, "o": 0x05B9, "O": 0x05B9, "¿": 0x05B9, "u": 0x05BB, "U": 0x05BB, "ø": 0x05C2}

metadata = """
---
word_english: name_of_the_document (e.g. beka_half_a_shekel)
word_hebrew: lemma in hebrew (e.g. אַח)
title: optional English title (e.g. empty or 'Sack, Donkey Bag')
semantic_fields: semantic_field_1, semantic_field_2, ... (e.g. deliverance)
contributors: author_1, author_2, ... (e.g. jan_smit)
first_published: date of publishing (e.g. 2023-01-09)
revised: last revision date (e.g. 2023-04-11 or empty)
---
"""


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
        line = re.sub(r"(.*)\\textit\\textit{(.*?)}}(.*)", r"\1*\2*\3", line)
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
    conversion = {"A": "αʹ", "AS": "αʹσʹ", "ASTh": "αʹσʹθʹ", "ATh": "αʹθʹ",
                  "G": "LXX", "GA": "LXXαʹ", "GAS": "LXXαʹσʹ", "GASTh": "LXXαʹσʹθʹ",
                  "GATh": "LXXαʹθʹ", "GS": "LXXσʹ", "GSTh": "LXXσʹθʹ", "GTh": "LXXθʹ",
                  "J": "J", "K": "K", "M": "MT", "N": "N", "NSm": "N,Smr", "O": "O",
                  "ON": "O,N", "ONSm": "O,N,Smr", "OPs": "O,PsJ", "OPsN": "O,PsJ,N",
                  "OPsNSm": "O,PsJ,N,Smr", "OPsSm": "O,PsJ,Smr", "OSm": "O,Smr",
                  "Ps": "PsJ", "S": "σʹ", "Sm": "Smr", "STh": "σʹθʹ", "Th": "θʹ"
                  }
    for i in range(5):
        m = re.search(r"(.*)\\sup([a-zA-Z]*)(|\\|;|.)(.*)", line)
        if m:
            sup = m.group(2)
            if sup in conversion:
                sup = conversion[sup]
            line = m.group(1) + f"<sup>{sup}</sup>" + m.group(3) + m.group(4)
    return line


def replace_hebrew_part(hbr):
    # print(hbr)
    h = ""
    i = 0
    point = False
    while i < len(hbr):
        char = hbr[i]
        if char in hebrew_points:
            point_char = chr(hebrew_points[char])
            point = True
        else:
            if point:
                h += hebrew[char] + point_char
                point = False
            else:
                if char not in hebrew:
                    print(f"character {char} found in Hebrew word {hbr}")
                    h += char
                else:
                    h += hebrew[char]
        i += 1
    return '<span dir="rtl">' + h + '</span>'


def replace_hebrew(line):
    if "{\\Hbr" in line:
        for i in range(5):
            line = re.sub(r"(.*)\\RL{\\Hbr (.*?)}(.*)", r"\1\2 \3", line)
        for i in range(5):
            line = re.sub(r"(.*){\\Hbr (.*?)}(.*)", r"\1\2 \3", line)
    elif "\\smhebr" in line or "\\nmhebr" in line:
        line = replace_hebrew_coded(line)
    return line


def replace_hebrew_coded(line):
    for i in range(50):
        m = re.search(r"(.*)\\beginR{\\[sn]mhebr *\\beginR{\\[sn]mhebr (.*?)}\\endR}\\endR(.*)", line) # a situation where erroneously double definitions
        if not m:
            m = re.search(r"(.*)\\beginR{\\[sn]mhebr \\[sn]mhebr (.*?)}\\endR(.*)", line) # another erroneous situation
        if not m:
            m = re.search(r"(.*)\\beginR{\\[sn]mhebr (.*?)}\\endR(.*)", line)
        if m:
            hbr = m.group(2).split()
            i = len(hbr) - 1
            all_parts = ""
            while i >= 0:
                all_parts += replace_hebrew_part(hbr[i]) + " "
                i -= 1
            line = m.group(1) + all_parts + m.group(3)
        else:
            break
    return line


def replace_greek(line):
    if "\Gr" in line:
        for i in range(5):
            line = re.sub(r"(.*){\\Gr (.*)}(.*)", r"\1\2 \3", line)
    elif "\\nmody" in line or "\\smody" in line:
        line = replace_greek_coded(line)
    return line


def replace_greek_coded(line):
    # print(line)
    for i in range(5):
        m = re.search(r'(.*){\\[ns]mody (.*?)}(.*)', line)
        if m:
            gr = m.group(2)
            # print(gr)
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
                    if char not in greek:
                        print(f"character {char} found in Greek expression {gr}")
                        g += char
                    else:
                        g += greek[char]
                i += 1
            line = m.group(1) + g + m.group(3)
        else:
            break
    return line


def replace_syrian(line):
    if "\Syr" in line:
        for i in range(5):
            line = re.sub(r"(.*){\\Syr (.*)}(.*)", r"\1\2 \3", line)
    return line


def replace_textsc(line):
    for i in range(5):
        line = re.sub(r'(.*)\\textsc{(.*?)}(.*)', r'\1<span style="text-transform:uppercase;">\2</span>\3', line)
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
    return re.sub(r'(.*)\\pslabel{(.*?)}(.*)', r'\1<span id="\2">\3</span>', line)


def replace_enlargethispage(line):
    return re.sub(r"(.*)\\enlargethispage{(.*?)}(.*)", r"\1\3", line)


def replace_mbox(line):
    return re.sub(r"(.*)\\mbox{(.*?)}(.*)", r"\1\2\3", line)


def replace_sil(line):
    for i in range(5):
        line = re.sub(r"(.*){\\Sil(.*?)}(.*)", r"\1\2\3", line)
    return line


def replace_includegraphics(line):
    for i in range(5):
        line = re.sub(r"(.*){\\includegraphics{(.*?)}(.*?)}(.*)", r"\1![](../photos/\2)\3", line)
    return line


# def replace_hangindent(line):
#     for i in range(5):
#         line = re.sub(r"(.*)\\hangindent ([0-9.]*)cm(.*)", r"\1\3", line)
#     return line
#

def replace_href(line):
    for i in range(5):
        line = re.sub(r'(.*)\\href{(.*?)}{(.*?)}(.*)', r'\1<a href=\2 target="_blank">\3</a>\4', line)
    return line


def replace_section_header(line):
    return re.sub(r"^\\sect*{(.*)}(.+)", r"##\1\2", line)


def replace_subsection_header(line):
    return re.sub(r"^\\subsect*{(.*)}(.+)", r"###\1\2", line)


def replace_introduction(line):
    return re.sub(r"\*\*(.*)Introduction\*\*(.*)", r"##\1Introduction\2", line)


def replace_last_backslash(line):
    line = re.sub(r"(.*)\\\\ *$", r"\1<br>", line)
    line = re.sub(r"(.*)\\ *$", r"\1<br>", line)
    return line


def remove_hspace(line):
    for i in range(5):
        line = re.sub(r"(.*)\\hspace\*?{.*}(.*)", r"\1   \2", line)
    return line


def remove_scalebox(line):
    for i in range(5):
        line = re.sub(r"(.*)\\scalebox{.*?}(.*)", r"\1\2", line)
    return line


def remove_large(line):
    return re.sub(r"(.*)\\(LARGE|large)(.*)", r"\1\3", line)


def remove_small(line):
    return re.sub(r"(.*)\\(SMALL|small)(.*)", r"\1\3", line)


def remove_comment(line):
    for i in range(5):
        line = re.sub(r"(.)(.*)%.*$", r"\1\2", line)
    return line


def remove_renewcommand(line):
    return re.sub(r"(.*)\\renewcommand{.*?}{.*}(.*)", r"\1\2", line)


def multiline_replacements(input, output):
    footnotes = []
    i = 0
    with open(output, "w") as f:
        with open(input, 'r') as file:
            text = file.read()
            new_text = ""
            # Footnotes
            while "endnote" in text or "footnote" in text:
                m = re.search(r"([.\s\S]*?)\\(?:endnote|footnote){([.\s\S]*?)}([.\s\S]*)", text)
                if m:
                    footnote = m.group(2).replace("	", " ") # replace tab with a space
                    footnotes.append(footnote)
                    new_text += m.group(1) + f"[^{i + 1}]"
                    text = m.group(3)
                else:
                    break
                i += 1
            # Italics
            text = new_text + text
            while "textit" in text:
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


def replace_special_characters(line):

    line = line.replace("*", "\*")

    line = line.replace("\symbol{123}", "@")        # replacement to handle greek
    line = line.replace("\symbol{125}", "*")        # replacement to handle hebrew and greek
    line = line.replace("\symbol{185}", "&")        # replacement to handle hebrew

    # line = line.replace("	", "&emsp;&emsp;")      # tab
    line = line.replace("\\ ", " ")                 # space
    line = line.replace("\\xx", "x")                # x
    line = line.replace("\\&", "&")                 # &
    line = line.replace("$<$", "&lt;")              # <
    line = line.replace("$>$", "&gt;")              # >
    line = line.replace("$/$", "/")                 # /
    line = line.replace("{/}", "/")                 # /
    line = line.replace("\\ldots", "...")           # ...
    line = line.replace("\\dots", "...")            # ...
    line = line.replace("$\\surd$", "√")            # √
    line = line.replace("$\\rightarrow$", "→")      # →
    line = line.replace("\\S\\,", "§")              # §
    line = line.replace("{\\S}", "§")               # §
    line = line.replace("\\nsupscr{$\\prime$}", "′")# ′
    line = line.replace("`", "\'")                  # '
    line = line.replace("{\\ain}", "ʿ")             # ʿ
    line = line.replace("\\ain", "ʿ")               # ʿ
    line = line.replace("{\\alef}", "ʾ")            # ʾ
    line = line.replace("{\\ss}", "ß")              # ß
    line = line.replace('\\"{A}', "Ä")              # Ä
    line = line.replace('\\"{a}', "ä")              # ä
    line = line.replace("\\={a}", "ā")              # ā
    line = line.replace("\\'{a}", "á")              # á
    line = line.replace("\\`{a}", "à")              # à
    line = line.replace("\\={e}", "ē")              # ē
    line = line.replace("\\^{e}", "ê")              # ê
    line = line.replace("\\'{e}", "é")              # é
    line = line.replace("\\'{E}", "É")              # É
    line = line.replace('\\"{O}', "Ö")              # Ö
    line = line.replace("\\'{\\i}", "í")            # í
    line = line.replace('\\={\\i}', "ī")            # ī
    line = line.replace('\\^{\\i}', "î")            # î
    line = line.replace('{\\i}', "ī")               # ī
    line = line.replace("\\'{o}", "ó")              # ó
    line = line.replace('\\^{o}', "ô")              # ô
    line = line.replace('\\"{o}', "ö")              # ö
    line = line.replace('\\"{u}', "ü")              # ü
    line = line.replace('\\"{u*', "ü")              # ü
    line = line.replace('\\^{u}', "û")              # û
    line = line.replace('\\={u}', "ū")              # ū
    line = line.replace('\\^{U}', "Û")              # Û
    line = line.replace('\\"{U}', "Ü")              # Û
    line = line.replace("\\v{g}", "ǧ")              # ǧ
    line = line.replace("{\\sh}", "ḫ")              # ḫ
    line = line.replace("\\s{h}", "ḫ")              # ḫ
    line = line.replace("\\sh ", "ḫ")               # ḫ
    line = line.replace("\\b{h}", "ẖ")              # ẖ
    line = line.replace("\\d{h}", "ḥ")              # ḥ
    line = line.replace("\\d{H}", "Ḥ")              # Ḥ
    line = line.replace("\\b{h}", "ẖ")              # ẖ
    line = line.replace("\\v{s}", "š")              # š
    line = line.replace("\\v{S}", "Š")              # Š
    line = line.replace("\\'{s}", "ś")              # ś
    line = line.replace("\\d{t}", "ṭ")              # ṭ
    line = line.replace("\\st ", "ṯ")               # ṯ

    line = line.replace("\\aq", "α´")               # α´
    line = line.replace("\\orig", "οʹ")             # οʹ
    line = line.replace("\\sym", "σ´")              # σ´

    # doubtful
    line = line.replace("\\#\\,", "#")              # #
    line = line.replace("\\/,", "’")                # ’
    line = line.replace("\\/", "")                  # empty
    line = line.replace("\\,", " ")                 # space
    line = line.replace("\\ ,", "")                 # space
    line = line.replace("\\-", "")                  # empty

    return line


def replace_book_references(line):

    line = line.replace("\\mta", "MT<sup>A</sup>")        # MTA
    line = line.replace("\\mtl", "MT<sup>L</sup>")        # MTL
    line = line.replace("\\mtz", "MT<sup>Z</sup>")        # MTZ
    line = line.replace("\\mt", "MT")                     # MT
    line = line.replace("\\qum", "Qum.")                  # Qum.
    line = line.replace("\\lxx", "LXX")                   # LXX
    line = line.replace("\\septant", "LXX<sup>Ant</sup>") # LXXAnt
    line = line.replace("\\septa", "LXX<sup>a</sup>")     # LXXa
    line = line.replace("\\septb", "LXX<sup>a</sup>")     # LXXb
    line = line.replace("\\septs", "LXX<sup>s</sup>")     # LXXs
    line = line.replace("{\\sept}", "LXX")                # LXX
    line = line.replace("\\sept", "LXX")                  # LXX

    line = line.replace("{\\tg}", "Tg.")                  # Tg.
    line = line.replace("\\tg", "Tg.")                    # Tg.
    line = line.replace("{\\targ}", "Tg.")                # Tg.
    line = line.replace("\\targ", "Tg.")                  # Tg.
    line = line.replace("{\\peshi}", "Syr.")              # Syr.
    line = line.replace("\\peshi", "Syr.")                # Syr.
    line = line.replace("{\\pesh}", "Syr.")               # Syr.
    line = line.replace("\\pesh", "Syr.")                 # Syr.
    line = line.replace("{\\sam}", "SP")                  # SP
    line = line.replace("\\sam", "SP")                    # SP
    line = line.replace("{\\vulg}", "Vulg.")              # Vulg.
    line = line.replace("\\vulg", "Vulg.")                # Vulg.

    return line


def replace_commands(line):
    line = line.replace("\\item", "  - ")                  #  -
    line = line.replace("\\linebreak", "<br>")             # <br>
    line = line.replace("\\newline", "<br>")               # <br>
    line = line.replace("\\hspace\\*", "   ")              # spaces
    line = line.replace("\\hspace", "   ")                 # spaces
    # line = line.replace("\\noindent", "")                # empty
    line = line.replace("\\theendnotes", "")               # empty
    line = line.replace("\\hfill", "")                     # empty
    line = line.replace("\\bigskip", "")                   # empty
    line = line.replace("{\\fill}", "")                    # empty
    line = line.replace("\\fill", "")                      # empty
    line = line.replace("\\normalsize", "")                # empty

    return line


def final_replacements(line):
    line = line.replace("\\th", "θ´")               # θ´
    return line


def skip_line(line):
    s = line.strip()
    return s.startswith("\\pagebreak") or s.startswith("\\setlength") \
            or s.startswith("\\markboth") or s.startswith("\\vspace") or s.startswith("\\thispagestyle") \
            or s.startswith("\\setcounter") or s.startswith("\\normalsize") or s.startswith("\\newpage") \
            or s.startswith("\\pagestyle") or s.startswith("\\def") or s.startswith("\\setlength") \
            or s.startswith("\\usepackage") or s.startswith("\\geometry") or s.startswith("\\TeXXeTstate") \
            or s.startswith("\\backgroundsetup") or s.startswith("\\setdefaultlanguage") or s.startswith("\\setdefaultlanguage") \
            or s.startswith("\\newfontfamily") or s.startswith("\\newcommand") or s.startswith("\\renewcommand") \
            or s.startswith("\\newcounter") or s.startswith("\\setcounter") or s.startswith("\\addtocounter") \
            or s.startswith("\\hyperref") or s.startswith("\\phantomsection") or s.startswith("\\newlength") \
            or s.startswith("\\font") or s.startswith("\\refstepcounter") or s.startswith("\\parbox") \
            or s.startswith("\\documentclass") or s.startswith("\\setotherlanguage") \
            or s.startswith("\\begin{") or s.startswith("\\end{") or s == "}"


def replacements(input, output):
    with open(output, "w") as f:
        f.write(metadata)
        with open(input, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip().startswith("%"):
                    continue                    # skip comments
                if line.strip() == "":
                    line = "\n\n"

                line = replace_special_characters(line)

                line = replace_label(line)
                line = replace_bold(line)
                line = replace_italics(line)
                line = replace_vspace(line)
                line = replace_superscript_1(line)
                line = replace_superscript_2(line)
                line = replace_textsc(line)
                line = replace_footnotesize(line)
                line = replace_reference(line)
                line = replace_sil(line)
                line = replace_includegraphics(line)
                # line = replace_hangindent(line)
                line = replace_href(line)
                line = replace_section_header(line)
                line = replace_subsection_header(line)
                line = replace_introduction(line)
                line = replace_mbox(line)
                line = replace_enlargethispage(line)
                line = replace_last_backslash(line)
                line = replace_hebrew(line)
                line = replace_greek(line)
                line = replace_syrian(line)

                line = remove_hspace(line)
                line = remove_scalebox(line)
                line = remove_large(line)
                line = remove_small(line)
                line = remove_comment(line)     # check occurences!
                line = remove_renewcommand(line)

                line = replace_def(line)
                line = replace_defined_reference(line)
                line = replace_book_references(line)
                line = replace_commands(line)

                if skip_line(line):
                    continue
                if line.startswith("{"):
                    line = line[1:]
                # if "\\" in line and not line.startswith("\\noindent") and not "\\textit" in line and not "\\*" in line:
                #     print(line)
                line = final_replacements(line)
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
