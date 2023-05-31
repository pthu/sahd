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
         "D": "Δ", "G": "Γ",
         "aj": "ἀ", "aJ": "ἁ", "a;": "ὰ", "av": "ά", "a*": "ἅ", "a’": "ᾶ", "a'": "ᾶ", "a/": "ᾳ", "a[": "ἄ",
         "ej": "ἐ", "eJ": "ἑ", "e;": "ὲ", "ev": "έ", "e*": "ἕ", "e[": "ἔ", "e@": "ἕ",
         "hj": "ἠ", "hJ": "ἡ", "h;": "ὴ", "hv": "ή", "h*": "ἥ", "h’": "ῆ", "h/": "ῃ", "h[": "ἤ", "h'": "ῆ",
         "ij": "ἰ", "iJ": "ἱ", "i;": "ὶ", "iv": "ί", "i*": "ἵ", "i’": "ῖ", "i[": "ἴ", "i'": "ῖ",
         "lv": "ƛ",
         "oj": "ὀ", "oJ": "ὁ", "o;": "ὸ", "ov": "ό", "o*": "ὅ", "o[": "ὄ", "o@": "ὅ",
         "rJ": "ῥ",
         "uj": "ὐ", "uJ": "ὑ", "u;": "ὺ", "uv": "ύ", "u*": "ὕ", "u’": "ῦ", "u[": "ὔ", "u@": "ὕ", "u'": "ῦ",
         "wj": "ὠ", "wJ": "ὡ", "w;": "ὼ", "wv": "ώ", "w*": "ὥ", "w’": "ῶ", "w/": "ῳ", "w[": "ὤ", "w'": "ῶ",
         "Æ": "΄", "»": "[", "Œ": "]", " ": " ", "/": "/", ",": ","
         }
hebrew = {"a": "א", "b": "ב", "B": "בּ", "g": "ג", "G": "גּ", "d": "ד", "D": "דּ", "h": "ה", "H": "הּ", "w": "ו",
          "W": "וּ", "z": "ז", "Z": "זּ", "j": "ח", "f": "ט", "F": "טּ", "y": "י", "Y": "יּ", "k": "כ", "K": "כּ",
          "û": "ך", "ò": "ךָ", "è": "ךְ", "l": "ל", "L": "לּ", "m": "מ", "M": "מּ", "µ": "ם", "n": "נ", "N": "נּ",
          "ö": "ן", "s": "ס", "S": "סּ", "[": "ע", "p": "פ", "P": "פּּ", "¹": "ף", "x": "צ", "X": "ץ", "Å": "צּ",
          "q": "ק", "Q": "קּּ", "r": "ר", "R": "רּּ", "c": "שׂ", "C": "שּׂ", "v": "שׁ", "V": "שּׁ", "t": "ת", "T": "תֹּ",
          "": "ש", "ç": "ש", "ˆ": "ן", "&": "ף", "π": "ף", "≈": "ץ", "=": "ך", "˚": "ך", "A": "&thinsp;־",
          "€": "׳", "£": "ן", "/": "/", "(": "(", ")": ")", "÷": "/",
          "Ë": "ך" + chr(0x05B0), "Ú": "ך" + chr(0x05B8)
          }
hebrew_points = {"]": 0x05B0, "+": 0x05B0, "Ò": 0x05B0, "“": 0x05B0, "Ô": 0x05B1, "‘": 0x05B1, "*": 0x05B2, "Õ": 0x05B3, "’": 0x05B3, "i": 0x05B4,
                 "I": 0x05B4, "e": 0x05B5, "E": 0x05B5, ",": 0x05B6, "<": 0x05B6, "'": 0x05B7, '"': 0x05B7, ";": 0x05B8,
                 ":": 0x05B8, "o": 0x05B9, "O": 0x05B9, "¿": 0x05B9, "u": 0x05BB, "U": 0x05BB, "ø": 0x05C2}

metadata = """
---
word_english: name_of_the_document (e.g. beka_half_a_shekel)
word_hebrew: lemma in hebrew (e.g. אַח)
title: optional English title (e.g. empty or Sack, Donkey Bag)
semantic_fields: semantic_field_1, semantic_field_2, ... (e.g. deliverance)
contributors: author_1, author_2, ... (e.g. jan_smit)
first_published: date of publishing (e.g. 2023-01-09)
last_update: last update date (e.g. 2023-04-11 or empty)
update_info: info about last update(e.g. Jan Smit or empty)
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


def replace_hebrew_part(hbr):
    br = re.search(r"(.*)[¿À](.*?)\?(.*)", hbr) # character in brackets
    if br:
        hbr = f"{br.group(1)}{br.group(2)}{br.group(3)}"
    hbr = hbr.replace("$,$", "")
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
                if char not in hebrew:
                    print(f"character {char} found in Hebrew word {hbr}")
                    h += char + point_char
                else:
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


def replace_hebrew_coded(line):
    for i in range(50):
        m = re.search(r"(.*)(\\symbol{.*?})(.*)", line)
        if m:
            line = m.group(1) + m.group(2).replace("{", "(").replace("}", ")") + m.group(3)
        else:
            break

    for i in range(50):
        m = re.search(r"(.*)\\beginR{\\[sn]mhebr *\\beginR{\\[sn]mhebr (.*?)}\\endR}\\endR(.*)", line) # a situation where erroneously double definitions
        if not m:
            m = re.search(r"(.*)\\beginR{\\[sn]mhebr \\[sn]mhebr (.*?)}\\endR(.*)", line) # another erroneous situation
        if not m:
            m = re.search(r"(.*){\\beginR{\\[sn]mhebr (.*?)}\\endR}(.*)", line)
        if not m:
            m = re.search(r"(.*)\\beginR{\\[sn]mhebr (.*?)}\\endR(.*)", line)
        if not m:
            m = re.search(r"(.*)\\beginR{\\[sn]mhebr(.*?)}\\endR(.*)", line)
        if not m:
            m = re.search(r"(.*)\\beginR{→ \\[sn]mhebr (.*?)}\\endR(.*)", line)
        if not m:
            m = re.search(r"(.*)\\beginR{\\medhebr (.*?)}\\endR(.*)", line)
        if not m:
            m = re.search(r"(.*){\\[sn]mhebr (.*?)}(.*)", line)
        if not m:
            m = re.search(r"(.*)\\hebreeuws ?{(.*?)}(.*)", line)
        if not m:
            m = re.search(r"(.*){\\hebf?g? ?{(.*?)}}(.*)", line)
        if not m:
            m = re.search(r"(.*)\\hebf? ?{(.*?)}(.*)", line)
        if m:
            hebrew_parts = m.group(2)
            ms = re.search(r"(.*)(\\symbol\(.*?\))(.*)", hebrew_parts)
            while ms:
                print(f"{ms.group(2)} found in hebrew expression {hebrew_parts}")
                hebrew_parts = f"{ms.group(1)}?{ms.group(3)}"
                ms = re.search(r"(.*)(\\symbol\(.*?\))(.*)", hebrew_parts)

            hbr = hebrew_parts.split()
            i = len(hbr) - 1
            all_parts = ""
            while i >= 0:
                all_parts += replace_hebrew_part(hbr[i])
                if i > 0: all_parts += " "
                i -= 1
            line = m.group(1) + all_parts + m.group(3)
        else:
            break
    return line


def replace_hebrew(line):
    if "{\\Hbr" in line:
        for i in range(5):
            line = re.sub(r"(.*)\\RL{\\Hbr (.*?)}(.*)", r"\1\2 \3", line)
        for i in range(5):
            line = re.sub(r"(.*){\\Hbr (.*?)}(.*)", r"\1\2 \3", line)
    elif "\\smhebr" in line or "\\nmhebr" in line or "\\medhebr" in line or "\\heb" in line:
        line = replace_hebrew_coded(line)
    return line


def replace_greek_coded(line):
    for i in range(50):
        m = re.search(r"(.*)(\\symbol{.*?})(.*)", line)
        if m:
            line = m.group(1) + m.group(2).replace("{", "(").replace("}", ")") + m.group(3)
        else:
            break

    for i in range(50):
        m = re.search(r'(.*){\\[ns]mody (.*?)}(.*)', line)
        if not m:
            m = re.search(r'(.*){\\grieks ?{(.*?)}}(.*)', line)
        if not m:
            m = re.search(r'(.*)\\grieks ?{(.*?)}(.*)', line)
        if not m:
            m = re.search(r'(.*){\\grf? ?{(.*?)}}(.*)', line)
        if not m:
            m = re.search(r'(.*)\\grf? ?{(.*?)}(.*)', line)
        if m:
            gr = m.group(2)
            ms = re.search(r"(.*)(\\symbol\(.*?\))(.*)", gr)
            while ms:
                print(f"{ms.group(2)} found in greek word {gr}")
                gr = f"{ms.group(1)}?{ms.group(3)}"
                ms = re.search(r"(.*)(\\symbol\(.*?\))(.*)", gr)

            if gr.find("\\-") >= 0:
                gr = gr.replace("\\-", "")
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


def replace_greek(line):
    if "\Gr" in line:
        for i in range(5):
            line = re.sub(r"(.*){\\Gr (.*?)}(.*)", r"\1\2 \3", line)
    elif "\\nmody" in line or "\\smody" in line or "\\grieks" in line or "\\gr" in line:
        line = replace_greek_coded(line)
    return line


def replace_syrian(line):
    if "\Syr" in line:
        for i in range(5):
            line = re.sub(r"(.*){\\Syr (.*?)}(.*)", r"\1\2 \3", line)
    return line


def replace_bold(line):
    if "textbf" in line:
        for i in range(5):
            line = re.sub(r"(.*)\\textbf{(.*?)}(.*)", r"\1**\2**\3", line)
    return line


def replace_italics(line):
    if "textit" in line or "textsl" in line:
        for i in range(5):
            line = re.sub(r"(.*)\\textit\\textit{{(.*?)}}(.*)", r"\1*\2*\3", line)
            line = re.sub(r"(.*)\\textit{(.*?)}(.*)", r"\1*\2*\3", line)
            line = re.sub(r"(.*)\\textsl{(.*?)}(.*)", r"\1*\2*\3", line)
    return line


def replace_vspace(line):
    if "vspace" in line:
        for i in range(5):
            line = re.sub(r"(.*)\\vspace{.*}(.*)", r"\1\2", line)
    return line


def replace_superscript_1(line):
    if "sups" in line:
        for i in range(5):
            line = re.sub(r"(.*?)\\n?sups(?:cr)?{(.*?)}(.*)", r"\1<sup>\2</sup>\3", line)
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
    if "sup" in line:
        for i in range(10):
            m = re.search(r"(.*)\\sup([a-zA-Z]*)(|\\|;|.)(.*)", line)
            if m:
                sup = m.group(2)
                if sup in conversion:
                    sup = conversion[sup]
                line = m.group(1) + f"<sup>{sup}</sup>" + m.group(3) + m.group(4)
    return line


def replace_subscript(line):
    if "subs" in line:
        for i in range(5):
            line = re.sub(r"(.*)\\n?subs{(.*?)}(.*)", r"\1<sub>\2</sub>\3", line)
            line = re.sub(r"(.*)\\n?subscr{(.*?)}(.*)", r"\1<sub>\2</sub>\3", line)
    return line


def replace_textsc(line):
    if "textsc" in line:
        for i in range(5):
            line = re.sub(r'(.*)\\textsc{(.*?)}(.*)', r'\1<span style="text-transform:uppercase;">\2</span>\3', line)
    return line


def replace_tiny(line):
    if "tiny" in line:
        for i in range(5):
            line = re.sub(r'(.*){\\tiny (.*?)}(.*)', r'\1\2\3', line)
    return line


def replace_g_h(line):
    if "\\G" in line or "\\H" in line:
        for i in range(5):
            line = re.sub(r'(.*){\\G (.*?)}(.*)', r'\1\2\3', line)
            line = re.sub(r'(.*){\\H (.*?)}(.*)', r'\1\2\3', line)
    return line


def replace_footnotesize(line):
    if "footnotesize" in line:
        for i in range(5):
            line = re.sub(r'(.*?){\\footnotesize\\plaat(.*)}', r'\1\2', line)
            line = re.sub(r'(.*?)\\footnotesize\\plaat(.*)', r'\1\2', line)
            line = re.sub(r'(.*){\\footnotesize ([a-zA-Z0-9]*?)}(.*)', r'\1\2\3', line)
            line = re.sub(r'(.*)\\footnotesize{([a-zA-Z0-9]*?)}(.*)', r'\1\2\3', line)
    return line


def replace_reference(line):
    if "\\hyperref" in line or "\\pageref" in line or "\\ref" in line:
        for i in range(5):
            line = re.sub(r'(.*)\\hyperref\[(.*?)]{(.*?)}(.*)', r'\1<a href="#\2">\3</a>\4', line)
            line = re.sub(r'(.*)\\pageref{(.*?)}(.*)', r'\1<a href="#\2">REPLACE THIS WITH A SUITABLE LINK NAME</a>\3', line)
            line = re.sub(r'(.*)\\ref{(.*?)}(.*)', r'\1<a href="#\2">REPLACE THIS WITH A SUITABLE LINK NAME</a>\3', line)
    return line


def replace_label(line):
    if "\\pslabel" in line:
        for i in range(5):
            line = re.sub(r'(.*)\\pslabel{(.*?)}(.*)', r'\1<span id="\2">\3</span>', line)
    if "\\label" in line:
        for i in range(5):
            line = re.sub(r'(.*)\\label{(.*?)}(.*)', r'\1<span id="\2">\3</span>', line)
    return line


def replace_mbox(line):
    if "mbox" in line:
        for i in range(10):
            line = re.sub(r"(.*){\\mbox(\\hebf? ?{.*?})}(.*)", r"\1\2\3", line)
    if "mbox" in line:
        for i in range(10):
            line = re.sub(r"(.*)\\mbox{(\\hebf? ?{.*?})}(.*)", r"\1\2\3", line)
    if "mbox" in line:
        for i in range(10):
            line = re.sub(r"(.*)\\mbox{(.*?)}(.*)", r"\1\2\3", line)
    return line


def replace_sil(line):
    if "Sil" in line:
        for i in range(5):
            line = re.sub(r"(.*){\\Sil(.*?)}(.*)", r"\1\2\3", line)
    return line


def replace_includegraphics(line):
    if "includegraphics" in line:
        for i in range(5):
            line = re.sub(r"(.*){\\includegraphics{(.*?)}(.*?)}(.*)", r"\1![](../photos/\2)\3", line)
    return line


def replace_href(line):
    if "href" in line:
        for i in range(5):
            line = re.sub(r'(.*)\\href{(.*?)}{(.*?)}(.*)', r'\1<a href=\2 target="_blank">\3</a>\4', line)
    return line


def replace_section_header(line):
    return re.sub(r"^\\sect*{(.*)}(.+)", r"##\1\2", line)


def replace_subsection_header(line):
    return re.sub(r"^\\subsect*{(.*)}(.*)", r"###\1\2", line)

def replace_introduction(line):
    return re.sub(r"\*\*(.*)Introduction\*\*(.*)", r"##\1Introduction\2", line)


def replace_last_backslash(line):
    line = re.sub(r"(.*)\\\\ *$", r"\1<br>", line)
    line = re.sub(r"(.*)\\ *$", r"\1<br>", line)
    return line


def remove_enlargethispage(line):
    return re.sub(r"(.*)\\enlargethispage{(.*?)}(.*)", r"\1\3", line)


def remove_hspace(line):
    if "hspace" in line:
        for i in range(5):
            line = re.sub(r"(.*)\\hspace\*?{.*}(.*)", r"\1   \2", line)
    return line


def remove_scalebox(line):
    if "scalebox" in line:
        for i in range(5):
            line = re.sub(r"(.*)\\scalebox{.*?}(.*)", r"\1\2", line)
    return line


def remove_large(line):
    if "large" in line or "LARGE" in line or "Large" in line:
        for i in range(5):
            line = re.sub(r"(.*?){\\(LARGE|Large|large)(.*?)}(.*)", r"\1\3\4", line)
            line = re.sub(r"(.*)\\(LARGE|Large|large)(.*)", r"\1\3", line)
    return line


def remove_small(line):
    if "small" in line or "SMALL" in line:
        for i in range(5):
            line = re.sub(r"(.*?){\\(SMALL|small)(.*?)}(.*)", r"\1\3\4", line)
        for i in range(5):
            line = re.sub(r"(.*)\\(SMALL|small)(.*)", r"\1\3", line)
    return line


def remove_textsf(line):
    if "textsf" in line:
        for i in range(5):
            line = re.sub(r"(.*?)\\textsf{(.*?)}(.*)", r"\1\2\3", line)
    return line


def remove_rm(line):
    if "\\rm" in line:
        for i in range(5):
            line = re.sub(r"(.*?){\\rm{(.*?)}}(.*)", r"\1\2\3", line)
    return line


def remove_comment(line):
    if "\\%" in line:
        line = line.replace("\\%", "%")
    elif "%" in line:
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
            while "textit" in text or  "textsl" in text:
                m = re.search(r"([.\s\S]*?)\\(?:textit|textsl){([.\s\S]*?)}([.\s\S]*)", text)
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

    line = line.replace("\symbol{123}", "@")        # replacement to handle greek
    line = line.replace("\symbol{125}", "*")        # replacement to handle hebrew and greek
    line = line.replace("\symbol{152}", "€")        # replacement to handle hebrew
    line = line.replace("\symbol{185}", "&")        # replacement to handle hebrew
    line = line.replace("\symbol{246}", "£")        # replacement to handle hebrew

    line = line.replace("\\ ", " ")                 # space
    line = line.replace("\\xx", "x")                # x
    line = line.replace("{\\&}", "&")               # &
    line = line.replace("\\&", "&")                 # &
    line = line.replace("\\#", "#")                 # #
    line = line.replace("\\}", "}")                 # }
    line = line.replace("\\[", "[")                 # [
    line = line.replace("$<$", "&lt;")              # <
    line = line.replace("$>$", "&gt;")              # >
    line = line.replace("$[$", "[")                 # [
    line = line.replace("$]$", "]")                 # ]
    line = line.replace("$/$", "/")                 # /
    line = line.replace("$\pm$", "∓")               # ∓
    line = line.replace("{\\ast}", "∗")             # ∗
    line = line.replace("{/}", "/")                 # /
    line = line.replace("\\Sigma", "∑")             # ∑
    line = line.replace("{\\ldots}", "...")         # ...
    line = line.replace("\\ldots", "...")           # ...
    line = line.replace("\\dots", "...")            # ...
    line = line.replace("{$\\surd$}", "√")          # √
    line = line.replace("$\\surd$", "√")            # √
    line = line.replace("$\\rightarrow$", "→")      # →
    line = line.replace("$\\leftrightarrow$", "↔")  # ↔
    line = line.replace("{\\S\\S\\,}", "§§")        # §§
    line = line.replace("{\\S\\S}", "§§")           # §§
    line = line.replace("\\S\\S", "§§")             # §§
    line = line.replace("{\\S\\,}", "§")            # §
    line = line.replace("\\S\\,", "§")              # §
    line = line.replace("{\\S}", "§")               # §
    line = line.replace("\\nsupscr{$\\prime$}", "′")# ′
    line = line.replace("`", "\'")                  # '
    line = line.replace("{\\ain}", "ʿ")             # ʿ
    line = line.replace("\\ain", "ʿ")               # ʿ
    line = line.replace("{\\alef}", "ʾ")            # ʾ
    line = line.replace("\\alef", "ʾ")              # ʾ
    line = line.replace("\\={a}", "ā")              # ā
    line = line.replace("\\=a", "ā")                # ā
    line = line.replace('\\"{a}', "ä")              # ä
    line = line.replace('\\"a', "ä")                # ä
    line = line.replace("\\'{a}", "á")              # á
    line = line.replace("\\d{a}", "ạ")              # ạ
    line = line.replace("\\v{a}", "ă")              # ă
    line = line.replace("\\^{a}", "â")              # â
    line = line.replace("\\^a", "â")                # â
    line = line.replace("\\ae", "æ")                # æ
    line = line.replace("\\'{A}", "Á")              # Á
    line = line.replace('\\"{A}', "Ä")              # Ä
    line = line.replace('{\\AA}', "Å")              # Å
    line = line.replace("\\^{A}", "Â")              # Â
    line = line.replace("\\={e}", "ē")              # ē
    line = line.replace("\\^{e}", "ê")              # ê
    line = line.replace('\\"{e}', "ë")              # ë
    line = line.replace("\\'{e}", "é")              # é
    line = line.replace("\\'e", "é")                # é
    line = line.replace("\\c{e}", "ȩ")              # ȩ
    line = line.replace("\\'{E}", "É")              # É
    line = line.replace("\\'{\\i}", "í")            # í
    line = line.replace('\\={\\i}', "ī")            # ī
    line = line.replace('\\={i}', "ī")              # ī
    line = line.replace('\\^{\\i}', "î")            # î
    line = line.replace('\\"{\\i}', "ï")            # ï
    line = line.replace('{\\i}', "ī")               # ī
    line = line.replace("\\'{o}", "ó")              # ó
    line = line.replace('\\^{o}', "ô")              # ô
    line = line.replace('\\^o', "ô")                # ô
    line = line.replace('\\={o}', "ō")              # ō
    line = line.replace('\\"{o}', "ö")              # ö
    line = line.replace('\\"o', "ö")                # ö
    line = line.replace('\\"{O}', "Ö")              # Ö
    line = line.replace('\\"O', "Ö")                # Ö
    line = line.replace('\\"{u}', "ü")              # ü
    line = line.replace('\\^{u}', "û")              # û
    line = line.replace('\\^u', "û")                # û
    line = line.replace('\\={u}', "ū")              # ū
    line = line.replace("\\'{u}", "ú")              # ú
    line = line.replace('\\^{U}', "Û")              # Û
    line = line.replace('\\"{U}', "Ü")              # Û
    line = line.replace('\\={U}', "Ū")              # Ū
    line = line.replace('\\"{y}', "ÿ")              # ÿ

    line = line.replace("{\\ss}", "ß")              # ß
    line = line.replace("\\ss", "ß")                # ß
    line = line.replace("\\c{c}", "ç")              # ç
    line = line.replace("\\b{d}", "ḏ")              # ḏ
    line = line.replace("\\d{d}", "ḍ")              # ḍ
    line = line.replace("\\v{g}", "ǧ")              # ǧ
    line = line.replace("\\.{g}", "ġ")              # ġ
    line = line.replace("\\v{G}", "Ǧ")              # Ǧ
    line = line.replace("\\textit{\\sh}", "*ḫ*")    # ḫ
    line = line.replace("{\\sh}", "ḫ")              # ḫ
    line = line.replace("\\s{h}", "ḫ")              # ḫ
    line = line.replace("\\sh", "ḫ")                # ḫ
    line = line.replace("\\b{h}", "ẖ")              # ẖ
    line = line.replace("\\d{h}", "ḥ")              # ḥ
    line = line.replace("\\d{H}", "Ḥ")              # Ḥ
    line = line.replace("{\\rH}", "Ḫ")              # Ḫ
    line = line.replace("\\d{k}", "ḳ")              # ḳ
    line = line.replace("\\b{K}","Ḵ")               # Ḵ
    line = line.replace("\\'{n}", "ń")              # ń
    line = line.replace("\\~{n}", "ñ")              # ñ
    line = line.replace("\\~n", "ñ")                # ñ
    line = line.replace("\\v{g}", "ǧ")              # ǧ
    line = line.replace("\\v{r}", "ř")              # ř
    line = line.replace("\\'{s\\,}", "ś")           # ś
    line = line.replace("\\'{s}", "ś")              # ś
    line = line.replace("\\d{s}", "ṣ")              # ṣ
    line = line.replace("\\v{s}", "š")              # š
    line = line.replace("\\v{S}", "Š")              # Š
    line = line.replace("\\d{S}", "Ṣ")              # Ṣ
    line = line.replace("\\d{t}", "ṭ")              # ṭ
    line = line.replace("\\b{t}", "ṯ")              # ṯ
    line = line.replace("\\st ", "ṯ")               # ṯ
    line = line.replace("\\d{T}", "Ṭ")              # Ṭ
    line = line.replace("\\d{z}", "ẓ")              # ẓ
    line = line.replace("\\d{Z}", "Ẓ")              # Ẓ

    line = line.replace('\\"{p}', "p" + chr(0x0308))# p with diaresis

    line = line.replace("{\\aq}", "α´")             # α´
    line = line.replace("{\\orig}", "οʹ")           # οʹ
    line = line.replace("{\\theod}", "θ´")          # θ´
    line = line.replace("\\aq", "α´")               # α´
    line = line.replace("\\orig", "οʹ")             # οʹ
    line = line.replace("\\theod", "θ´")            # θ´

    line = line.replace("\\es3", "," + chr(0x0313)) #
    line = line.replace("{?'}", "¿")                # ¿
    line = line.replace("\\#\\,", "#")              # #
    line = line.replace("\\/,", "’")                # ’
    line = line.replace("$^\prime$", "′")           # ′
    line = line.replace("{\\B ʿ}", "ʿ")             # ʿ
    line = line.replace("\\/", "")                  # empty
    line = line.replace("\\,", " ")                 # space
    line = line.replace("\\ ,", "")                 # space
    line = line.replace("\\-", "")                  # empty
    line = line.replace("\\twosp", "&nbsp;&nbsp;")  # "  "
    line = line.replace("\\eightsp", "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")  # "        "

    line = line.replace("$\\frac{1}{2}$", "&frac12;")  # 1/2
    line = line.replace("$\\frac{1}{3}$", "&frac13;")  # 1/3
    line = line.replace("$\\frac{1}{4}$", "&frac14;")  # 1/4
    line = line.replace("$\\frac{2}{3}$", "&frac23;")  # 2/3
    line = line.replace("$\\frac{3}{4}$", "&frac34;")  # 3/4

    return line


def replace_book_references(line):

    line = line.replace("\\mta", "MT<sup>A</sup>")        # MTA
    line = line.replace("\\mtl", "MT<sup>L</sup>")        # MTL
    line = line.replace("\\mtz", "MT<sup>Z</sup>")        # MTZ
    line = line.replace("{\\mt}", "MT")                   # MT
    line = line.replace("\\mt", "MT")                     # MT
    line = line.replace("\\MT", "MT")                     # MT
    line = line.replace("\\qum", "Qum.")                  # Qum.
    line = line.replace("\\lxx", "LXX")                   # LXX
    line = line.replace("\\LXX", "LXX")                   # LXX
    line = line.replace("\\septant", "LXX<sup>Ant</sup>") # LXXAnt
    line = line.replace("\\septa", "LXX<sup>a</sup>")     # LXXa
    line = line.replace("\\septb", "LXX<sup>a</sup>")     # LXXb
    line = line.replace("\\septs", "LXX<sup>s</sup>")     # LXXs
    line = line.replace("{\\sept}", "LXX")                # LXX
    line = line.replace("\\sept", "LXX")                  # LXX
    line = line.replace("\\ges", "Ges")                   # Ges

    line = line.replace("{\\tg}", "Tg")                   # Tg
    line = line.replace("\\tg", "Tg")                     # Tg
    line = line.replace("{\\targ}", "Tg")                 # Tg
    line = line.replace("\\targ", "Tg")                   # Tg
    line = line.replace("\\Tar", "Tg")                    # Tg
    line = line.replace("{\\peshi}", "Pesh")              # Pesh
    line = line.replace("\\peshi", "Pesh")                # Pesh
    line = line.replace("{\\pesh}", "Pesh")               # Pesh
    line = line.replace("\\pesh", "Pesh")                 # Pesh
    line = line.replace("{\\sam}", "SP")                  # SP
    line = line.replace("\\sam", "SP")                    # SP
    line = line.replace("{\\vulg}", "Vg")                 # Vg
    line = line.replace("\\vulg", "Vg")                   # Vg
    line = line.replace("\\Vul", "Vg")                    # Vg

    return line


def replace_commands(line):
    line = line.replace("\\item", "  - ")                  #  -
    line = line.replace("\\prl", "|")                      # |
    line = line.replace("\\linebreak", "<br>")             # <br>
    line = line.replace("\\newline", "<br>")               # <br>
    line = line.replace("\\hspace\\*", "   ")              # spaces
    line = line.replace("\\hspace", "   ")                 # spaces
    line = line.replace("\\theendnotes", "")               # empty
    line = line.replace("\\hfill", "")                     # empty
    line = line.replace("\\vfill", "")                     # empty
    line = line.replace("\\bigskip", "")                   # empty
    line = line.replace("{\\fill}", "")                    # empty
    line = line.replace("\\fill", "")                      # empty
    line = line.replace("\\normalsize", "")                # empty
    line = line.replace("\\today", "")                     # empty
    line = line.replace("\\medskip", "")                   # empty

    return line


def final_replacements(line):
    line = line.replace("\\th", "θ´")               # θ´
    line = line.replace("SP<sup>T</sup>}", "SP<sup>T</sup>")
    line = line.replace('\\"u', "ü")                # ü
    line = line.replace("{\\sym}", " σ´")           # σ´
    line = line.replace("$\\to", "→")               # →
    line = line.replace("\\vg", "Vg")               # Vg
    line = line.replace("\\sym", " σ´")             # σ´
    line = line.replace("\\cr", "\n")               # \n
    line = line.replace("\\RL", "")                 # empty

    return line


def skip_line(line):
    s = line.strip()
    return s.startswith("\\pagebreak") or s.startswith("\\nopagebreak") or s.startswith("\\setlength") \
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
            or s.startswith("\\begin{") or s.startswith("\\end{")


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
                line = replace_textsc(line)
                line = replace_tiny(line)
                line = replace_superscript_1(line)
                line = replace_superscript_2(line)
                line = replace_subscript(line)
                line = replace_footnotesize(line)
                line = replace_reference(line)
                line = replace_sil(line)
                line = replace_includegraphics(line)
                line = replace_href(line)
                line = replace_section_header(line)
                line = replace_subsection_header(line)
                line = replace_introduction(line)
                line = replace_g_h(line)
                line = replace_mbox(line)
                line = replace_last_backslash(line)
                line = replace_hebrew(line)
                line = replace_greek(line)
                line = replace_syrian(line)

                line = remove_enlargethispage(line)
                line = remove_hspace(line)
                line = remove_scalebox(line)
                line = remove_large(line)
                line = remove_small(line)
                line = remove_textsf(line)
                line = remove_rm(line)
                line = remove_comment(line)
                line = remove_renewcommand(line)

                line = replace_def(line)
                line = replace_defined_reference(line)
                line = replace_book_references(line)
                line = replace_commands(line)

                line = final_replacements(line)

                if skip_line(line):
                    continue
                if line.startswith("{"):
                    line = line[1:]
                f.write(line)
        f.close()


def diacritic(line):
    return re.search(r'.*{[a-zA-Z]}.*', line)


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
