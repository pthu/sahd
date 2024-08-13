import os
from os.path import exists, isdir
from shutil import rmtree, copytree
from pathlib import Path
import argparse
from time import sleep
from subprocess import run, Popen
import csv
from datetime import datetime
import re

SAHD_BASE = Path(".")

MKDOCS_OUT = SAHD_BASE / "mkdocs.yml"
MKDOCS_IN = SAHD_BASE / "source/mkdocsIn.yml"

SRC = SAHD_BASE / "source"
DOCS = SAHD_BASE / "docs"
WORDS = SRC / "words"
SEMANTIC_FIELDS = SRC / "semantic_fields"
CONTRIBUTORS = SRC / "contributors"
EDITORIAL_BOARD = SRC / "editorial_board"
MISCELLANEOUS = SRC / "miscellaneous"
STORE = SRC / "store"
PHOTOS = SRC / "photos"
PDFS = SRC / "pdfs"
LEMMAS_INDEX = SRC / "lemmas_index.txt"

WORDS_DOCS = DOCS / "words"
SEMANTIC_FIELDS_DOCS = DOCS / "semantic_fields"
CONTRIBUTORS_DOCS = DOCS / "contributors"
EDITORIAL_BOARD_DOCS = DOCS / "editorial_board"
MISCELLANEOUS_DOCS = DOCS / "miscellaneous"
STORE_DOCS = DOCS / "store"
PHOTOS_DOCS = DOCS / "images/photos"
PDFS_DOCS = DOCS / "pdfs"

WORDS_LIST = SAHD_BASE / "word_list.csv"

HEADER_HOME = '<html><body><img id="banner" src="./images/banners/banner.png" alt="banner" /></body></html>\n\n'
HEADER = '<html><body><img id="banner" src="../../images/banners/banner.png" alt="banner" /></body></html>\n\n'
DOWNLOAD = '<div><input id="download" title="Download/print the document" type="image" onclick="print_document()" src="../../images/icons/download3.png" alt="download" /></div>'
SHEBANQ = '<div><a id="shebanq" title="Word in SHEBANQ" href="https://shebanq.ancient-data.org/hebrew/word?id=replace" target="_blank"><img src="../../images/icons/shebanq.png" alt="shebanq"></a></div>'
UBS = '<div><a id="ubs" title="Word in Semantic Dictionary of Biblical Hebrew" href="https://semanticdictionary.org/semdic.php?databaseType=SDBH&language=en&lemma=replace&startPage=1" target="_blank"><img src="../../images/icons/ubs.png" alt="ubs"></a></div>'

PHOTO_PATH = r"(.*!\[.*])(\(.*/(.*\.(png|PNG|jpg|JPG|jpeg|JPEG|gif|GIF|tiff|TIFF)))(.*)"
PHOTO_PATH_REPLACEMENT = r"\1(../images/photos/\3\5"
PDF_PATH = r'(.*src=")(\.\./pdfs/)(.*)'
PDF_PATH_REPLACEMENT = r"\1/sahd/pdfs/\3"

PREFIXES = ["de", "den", "der", "'t", "’t", "te", "ten", "ter", "van", "von"]

errors = []


def read_args():
    parser = argparse.ArgumentParser(description='build.py',
                                     usage='use "%(prog)s --help" for more information',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("action", help="make - compiles Markdown files from the source files "
                                       "\ndocs - does `make` and then serves the docs locally and shows them in your browser"
                                       "\ngithub - does `make`, and pushes the whole site to GitHub"
                                       "\n          where it will be published under <https://...>"
                                       "\n          the repo itself will also be committed and pushed to GitHub")
    args = parser.parse_args()

    action = args.action

    return action


def commit():
    run(["git", "add", "--all", "."])
    run(["git", "commit", "-m", datetime.now().strftime("%m/%d/%Y, %H:%M:%S")])
    run(["git", "push", "origin", "main"])


def ship_docs():
    run(["mkdocs", "gh-deploy"])


def build_docs():
    run(["mkdocs", "build"])


def serve_docs():
    proc = Popen(["mkdocs", "serve"])
    sleep(4)
    run("open http://127.0.0.1:8000", shell=True)
    try:
        proc.wait()
    except KeyboardInterrupt:
        pass
    proc.terminate()


def error(msg):
    errors.append(msg)


def show_errors():
    for msg in errors:
        print(f"ERROR: {msg}")
    return len(errors)


def capitalize(s):
    return s.replace('_', ' ').title()


def capitalize_name(s):
    name = ""
    parts = s.split("_")
    for part in parts:
        if part in PREFIXES:
            name += part + " "
        else:
            name += part.title() + " "
    return name.strip()


def get_value(line):
    return line[line.index(":") + 1:].strip()


def get_values(line):
    value_list = []
    values = line[line.index(":") + 1:].split(",")
    for value in values:
        if value.strip():
            value_list.append(value.strip())
    return value_list


def reverse(word):
    return "".join(reversed(word))


def get_number_of_points(word):
    points = 0
    for i in range(len(word)):
        if ord(word[i]) < 0x5D0:
            points += 1
    return points


def get_probable_index(word_hebrew, words_list):
    for i in range(len(words_list)):
        if word_hebrew == words_list[i]:
            return i

    points = get_number_of_points(word_hebrew)
    i = 0
    for word in words_list:
        if points <= get_number_of_points(word) or i == len(words_list) - 1:
            break
        i += 1

    return i


def convert_to_id(language, lex):
    return language + lex.replace(">", "A").replace("<", "O").replace("[", "v").replace("/", "n").replace("=", "i")


def create_shebanq_references():
    shebanq = {}

    with open('shebanq_words.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            language = "2" if row[0] == "Aramaic" else "1"
            word_id = convert_to_id(language, row[1])
            word_hebrew = row[3]
            key = word_hebrew[0]
            word_hebrew = reverse(word_hebrew)
            if key in shebanq.keys():
                shebanq[key][word_hebrew] = word_id
            else:
                shebanq[key] = {word_hebrew: word_id}

    return shebanq


def get_shebanq_id(word_hebrew, shebanq_dict):
    first_char = word_hebrew[len(word_hebrew) - 1]
    if first_char in shebanq_dict.keys() and word_hebrew in shebanq_dict[first_char]:
        return shebanq_dict[first_char][word_hebrew]
    else:
        return None


def create_ubs_references():
    ubs = {}

    with open('ubs_words.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            word_hebrew = row[0]
            vocal = row[1]
            key = word_hebrew[0]
            word_hebrew = reverse(word_hebrew)
            if key in ubs.keys():
                if word_hebrew in ubs[key]:
                    ubs[key][word_hebrew].append(vocal)
                else:
                    ubs[key][word_hebrew] = [vocal]
            else:
                ubs[key] = {word_hebrew: [vocal]}
    return ubs


def get_pointless(word_hebrew):
    pointless = ""
    for i in range(len(word_hebrew)):
        if ord(word_hebrew[i]) >= 0x5D0:
            pointless += word_hebrew[i]
    return pointless


def get_ubs_reference(word_hebrew, ubs_dict):
    pointless = get_pointless(word_hebrew)
    first_char = pointless[len(pointless) - 1]
    if pointless in ubs_dict[first_char]:
        index = 0
        if len(ubs_dict[first_char][pointless]) > 1:
            index = get_probable_index(word_hebrew, ubs_dict[first_char][pointless])
        return ubs_dict[first_char][pointless][index]
    else:
        return None


def modify_for_sorting(word_hebrew):
    # This method is called for sorting Hebrew words where all the letters
    # are the same and in same order.  Only the points marking vowels differ.
    # To sort these words according to the vowel markings we change all letters
    # to a letter "A", whose Unicode value is smaller than Unicode values of
    # Hebrew vowel markings. This way the Unicode values of vowel markings
    # define the sort order.
    word_to_sort = ""
    for i in range(len(word_hebrew)):
        if ord(word_hebrew[i]) >= 0x5D0:
            word_to_sort += "A"
        else:
            word_to_sort += word_hebrew[i]
    return word_to_sort


def sort_hebrew(source_dict):
    temp_dict = {}
    for key in source_dict:
        pointless = get_pointless(key)
        if pointless in temp_dict.keys():
            temp_dict[pointless].update({key: source_dict[key]})
        else:
            temp_dict[pointless] = {key: source_dict[key]}

    temp2_dict = {}
    for key in sorted(temp_dict):
        vocalized_variations = sorted(temp_dict[key].items(), key=lambda t: modify_for_sorting(t[0]))
        temp2_dict[key] = vocalized_variations

    result_list = []
    for value in temp2_dict.values():
        for i in range(len(value)):
            result_list.append((value[i][0], value[i][1]))

    return result_list


def sort_contributors(contributors_dict):
    sort_dict = {}
    target_dict = {}
    for key in contributors_dict:
        parts = key.split("_")
        surname_key = ""
        for i in range(len(parts)):
            if parts[i] in PREFIXES or i == len(parts) - 1:
                surname_key += parts[i]
        sort_dict[surname_key] = key
    for key in sorted(sort_dict):
        name = sort_dict[key]
        target_dict[name] = contributors_dict[name]

    return target_dict


def sort_latin(source_dict, contributors=False):
    target_dict = {}
    sorted_dict = sort_contributors(source_dict) if contributors else sorted(source_dict)
    for key in sorted_dict:
        for item in sorted(source_dict[key].keys()):
            if key in target_dict.keys():
                target_dict[key] = target_dict[key] + [(item, source_dict[key][item])]
            else:
                target_dict[key] = [(item, source_dict[key][item])]
    return target_dict


def get_relations():
    words, semantic_fields, contributors = {}, {}, {}

    for word in WORDS.glob("*"):
        if word.name == ".DS_Store":
            continue
        with open(WORDS / word.name, "r") as f:
            word_english, word_hebrew = "", ""
            lines = f.readlines()
            for line in lines:
                if line.startswith("word_english:"):
                    word_english = get_value(line)
                elif line.startswith("word_hebrew:"):
                    word_hebrew = get_value(line)
                    words[word_hebrew] = Path(word).stem
                elif line.startswith("semantic_fields:") or line.startswith("contributors:"):
                    if not word_english or not word_hebrew:
                        error(f"english and/or hebrew word in {word.name} metadata not given")
                        continue
                    keys = get_values(line)
                    for key in keys:
                        if line.startswith("semantic_fields:"):
                            if key in semantic_fields.keys():
                                semantic_fields[key][word_hebrew] = word_english
                            else:
                                semantic_fields[key] = {word_hebrew: word_english}
                        else:
                            if key in contributors.keys():
                                contributors[key][word_hebrew] = word_english
                            else:
                                contributors[key] = {word_hebrew: word_english}

    # sort dictionaries
    words_dict = sort_hebrew(words)
    semantic_fields_dict = sort_latin(semantic_fields)
    contributors_dict = sort_latin(contributors, True)

    return words_dict, semantic_fields_dict, contributors_dict


def write_index_file():
    filename = "index.md"
    text = [HEADER_HOME]
    with open(SRC / f"{filename}", 'r') as f:
        lines = f.readlines()
        for line in lines:
            text.append(line)

    with open(DOCS / f"{filename}", 'w') as f:
        f.write("".join(text))


def write_words(shebanq_dict, ubs_dict):
    if isdir(WORDS_DOCS):
        rmtree(WORDS_DOCS)
    os.mkdir(WORDS_DOCS)

    for word in WORDS.glob("*"):
        word_hebrew, word_english, title, shebanq_id, first_published, last_update, additional_info = "", "", "", "", "", "", ""
        semantic_fields, contributors = [], []
        text, first_dashes, second_dashes = [], False, False
        if word.name == ".DS_Store":
            continue
        filename = word.name
        with open(WORDS / filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                if second_dashes:
                    line = re.sub(PHOTO_PATH, PHOTO_PATH_REPLACEMENT, line) # modify possible photo path
                    line = re.sub(PDF_PATH, PDF_PATH_REPLACEMENT, line) # modify possible pdf path
                    if line.strip().startswith("<iframe") and DOWNLOAD in text:
                        text.remove(DOWNLOAD)
                    text.append(line)
                if line.strip() == "---" and not first_dashes:
                    first_dashes = True
                elif line.startswith("word_english:"):
                    word_english = get_value(line)
                elif line.startswith("word_hebrew:"):
                    word_hebrew = reverse(get_value(line))
                elif line.startswith("title:"):
                    title = get_value(line)
                elif line.startswith("semantic_fields:"):
                    semantic_fields = get_values(line)
                elif line.startswith("contributors:"):
                    contributors = get_values(line)
                elif line.startswith("first_published:"):
                    first_published = get_value(line)
                elif line.startswith("shebanq_id:"):
                    shebanq_id = get_value(line)
                elif line.startswith("last_update:") and line.replace("last_update:", "").strip() != "":
                    last_update = get_value(line)
                elif line.startswith("additional_info:"):
                    additional_info = get_value(line)
                elif line.strip() == "---" and not second_dashes:
                    second_dashes = True
                    text.append(HEADER)
                    text.append(DOWNLOAD)
                    if not shebanq_id:
                        shebanq_id = get_shebanq_id(word_hebrew, shebanq_dict)
                    if shebanq_id:
                        text.append(SHEBANQ.replace("replace", shebanq_id))
                    ubs_reference = get_ubs_reference(word_hebrew, ubs_dict)
                    if ubs_reference:
                        text.append(UBS.replace("replace", ubs_reference))
                    if not word_english or not word_hebrew:
                        error(f"Metadata for {filename} incomplete")
                    title_english = title if title else word_english.replace('_', ' ')
                    word_english_hebrew = f"{reverse(word_hebrew)} – {title_english}"
                    text.append(f"# {word_english_hebrew}\n\n")
                    if len(semantic_fields) > 0:
                        text.append("Semantic Fields:\n")
                        for sf in semantic_fields:
                            text.append(f"[{capitalize(sf)}](../semantic_fields/{sf}.md)&nbsp;&nbsp;&nbsp;")
                        text.append("<br>")
                    if len(contributors) > 0:
                        contributors_text, contributors_citing = "", ""
                        text.append("Author(s):\n")
                        first = True
                        for c in contributors:
                            if not first:
                                contributors_text += ",&nbsp;"
                                contributors_citing += ",&nbsp;"
                            contributors_text += f"[{capitalize_name(c)}](../contributors/{c}.md)"
                            contributors_citing += capitalize_name(c)
                            first = False
                        text.append(contributors_text + "<br>\n")
                    if first_published:
                        text.append(f"First published: {first_published}<br>")
                        if last_update:
                            text.append(f"Last update: {last_update} ")
                            text.append("<br>")
                    text.append(f"Citation: {contributors_citing}, {word_english_hebrew}, <br>\
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
                    Semantics of Ancient Hebrew Database (https://pthu.github.io/sahd)")
                    if first_published:
                        text.append(f", {first_published.split('-')[0]}")
                        if last_update:
                            text.append(f" (update: {last_update.split('-')[0]})")
                    if additional_info:
                        text.append("\n" + additional_info)
                    text.append("\n\n")

        if not second_dashes:
            error(f"Metadata for {filename} incomplete")

        with open(WORDS_DOCS / filename, "w") as f:
            f.write("".join(text))


def write_semantic_fields(semantic_fields_dict):
    if isdir(SEMANTIC_FIELDS_DOCS):
        rmtree(SEMANTIC_FIELDS_DOCS)
    copytree(SEMANTIC_FIELDS, SEMANTIC_FIELDS_DOCS)
    for s_field in semantic_fields_dict:
        name = s_field.capitalize().replace("_", " ")
        words = semantic_fields_dict[s_field]

        if not exists(SEMANTIC_FIELDS_DOCS / f"{s_field}.md"):
            with open(SEMANTIC_FIELDS_DOCS / f"{s_field}.md", 'w') as f:
                f.write(f'# **{name}**\n\n')
                f.close()

        text = [HEADER]
        with open(SEMANTIC_FIELDS_DOCS / f"{s_field}.md", 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = re.sub(PHOTO_PATH, PHOTO_PATH_REPLACEMENT, line) # modify possible photo path
                text.append(line)
            text.append("\n### Related words\n")
            for word in words:
                text.append(f"[{word[0]} – {word[1].replace('_', ' ')}](../words/{word[1]}.md)<br>")

        with open(SEMANTIC_FIELDS_DOCS / f"{s_field}.md", 'w') as f:
            f.write("".join(text))


def write_contributors(contributors_dict):
    if isdir(CONTRIBUTORS_DOCS):
        rmtree(CONTRIBUTORS_DOCS)
    copytree(CONTRIBUTORS, CONTRIBUTORS_DOCS)

    for contributor in contributors_dict:
        words = contributors_dict[contributor]

        if not exists(CONTRIBUTORS_DOCS / f"{contributor}.md"):
            with open(CONTRIBUTORS_DOCS / f"{contributor}.md", 'w') as f:
                f.write(f'# **{capitalize_name(contributor)}**\n\n')
                f.close()

        text = [HEADER]
        with open(CONTRIBUTORS_DOCS / f"{contributor}.md", 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = re.sub(PHOTO_PATH, PHOTO_PATH_REPLACEMENT, line) # modify possible photo path
                text.append(line)
            text.append("\n### Contributions\n")
            for word in words:
                text.append(f"[{word[0]} – {word[1].replace('_', ' ')}](../words/{word[1]}.md)<br>")

        with open(CONTRIBUTORS_DOCS / f"{contributor}.md", 'w') as f:
            f.write("".join(text))


def write_editorial_board(contributors_dict):
    if isdir(EDITORIAL_BOARD_DOCS):
        rmtree(EDITORIAL_BOARD_DOCS)
    copytree(EDITORIAL_BOARD, EDITORIAL_BOARD_DOCS)

    for filename in os.listdir(EDITORIAL_BOARD_DOCS):
        if filename != ".DS_Store":
            name = Path(filename).stem
            if name in contributors_dict:
                words = contributors_dict[name]
            else:
                words = []

            text = [HEADER]
            with open(EDITORIAL_BOARD_DOCS / filename, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = re.sub(PHOTO_PATH, PHOTO_PATH_REPLACEMENT, line) # modify possible photo path
                    text.append(line)
                if len(words) > 0:
                    text.append("\n### Contributions\n")
                    for word in words:
                        text.append(f"[{word[0]} – {word[1].replace('_', ' ')}](../words/{word[1]}.md)<br>")

            with open(EDITORIAL_BOARD_DOCS / f"{name}.md", 'w') as f:
                f.write("".join(text))


def write_miscellaneous_file(filename):
    text = [HEADER]
    with open(MISCELLANEOUS / filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            text.append(line)

    with open(f"{MISCELLANEOUS_DOCS / filename}", 'w') as f:
        f.write("".join(text))


def write_miscellaneous():
    if isdir(MISCELLANEOUS_DOCS):
        rmtree(MISCELLANEOUS_DOCS)
    copytree(MISCELLANEOUS, MISCELLANEOUS_DOCS)

    for filename in os.listdir(MISCELLANEOUS):
        if filename != ".DS_Store":
            write_miscellaneous_file(filename)


def write_store_file(filename):
    text = [HEADER]
    with open(STORE / f"{filename}.md", 'r') as f:
        lines = f.readlines()
        for line in lines:
            text.append(line)

    with open(f"{STORE_DOCS / filename}.md", 'w') as f:
        f.write("".join(text))


def write_store():
    if isdir(STORE_DOCS):
        rmtree(STORE_DOCS)
    copytree(STORE, STORE_DOCS)

    write_store_file("contact")
    write_store_file("contribution")
    write_store_file("partners")
    write_store_file("project_description")


def copy_photos():
    if isdir(PHOTOS_DOCS):
        rmtree(PHOTOS_DOCS)
    copytree(PHOTOS, PHOTOS_DOCS)


def copy_pdfs():
    if isdir(PDFS_DOCS):
        rmtree(PDFS_DOCS)
    copytree(PDFS, PDFS_DOCS)


def write_navigation(semantic_fields_dict, contributors_dict):

    text = []
    with open(SRC / "mkdocs_in.yml", 'r') as f:
        lines = f.readlines()
        for line in lines:
            text.append(line)
            if line.replace(" ", "").startswith("-Lemmas:"):
                with open(LEMMAS_INDEX, 'r') as f:
                    entries = f.readlines()
                    for entry in entries:
                        entry = entry.strip()
                        if entry and not entry.startswith("#"):
                            if len(entry) == 1:
                                letter = entry
                                letter_written = False
                            else:
                                if not letter_written:
                                    text.append(f"            - {letter}:\n")
                                    letter_written = True
                                parts = entry.split(':')
                                text.append(f"                - {parts[0].strip()} - {parts[1].strip()}: words/{parts[2].strip()}.md\n")
            elif line.replace(" ", "").startswith("-Semanticfields:"):
                for s_field in semantic_fields_dict:
                    text.append(f"            - {capitalize(s_field)}: semantic_fields/{s_field}.md\n")
            elif line.replace(" ", "").startswith("-Contributors:"):
                for contributor in contributors_dict:
                    text.append(f"            - {capitalize_name(contributor)}: contributors/{contributor}.md\n")
            elif line.replace(" ", "").startswith("-Editorialboard:"):
                for filename in os.listdir(EDITORIAL_BOARD_DOCS):
                    if filename != ".DS_Store":
                        name = Path(filename).stem
                        text.append(f"            - {capitalize_name(name)}: editorial_board/{name}.md\n")
            elif line.replace(" ", "").startswith("-Miscellaneous:"):
                for article in os.listdir(MISCELLANEOUS):
                    if article != ".DS_Store":
                        article_name = article[0:article.find(".md")]
                        text.append(f"            - {capitalize_name(article_name)}: miscellaneous/{article}\n")
    with open("mkdocs.yml", 'w') as f:
        f.write("".join(text))


def check_lemmas_index_consistency(words_dict):
    lemmas, files = [], []

    with open(LEMMAS_INDEX, 'r') as f:
        entries = f.readlines()
        for entry in entries:
            entry = entry.strip()
            if entry and not entry.startswith("#") and len(entry) > 1:
                lemmas.append(entry.split(':')[2].strip())

    for entry in words_dict:
        files.append(entry[1])

    for lemma in lemmas:
        if lemma not in files:
            error(f"The file '{lemma}' in lemmas index not found")

    for file in files:
        if file not in lemmas:
            error(f"The file '{file}' not found in lemmas index")


def write_word_list(words_dict):
    f = open(WORDS_LIST, 'w')
    writer = csv.writer(f)
    for word in words_dict:
        writer.writerow([word[0], word[1]])
    f.close()


def make_docs():
    shebanq_dict = create_shebanq_references()
    ubs_dict = create_ubs_references()
    words_dict, semantic_fields_dict, contributors_dict = get_relations()
    write_index_file()
    write_words(shebanq_dict, ubs_dict)
    write_semantic_fields(semantic_fields_dict)
    write_contributors(contributors_dict)
    write_editorial_board(contributors_dict)
    write_miscellaneous()
    write_store()
    copy_photos()
    copy_pdfs()
    write_navigation(semantic_fields_dict, contributors_dict)
    check_lemmas_index_consistency(words_dict)
    write_word_list(words_dict)
    return not show_errors()


def main():
    action = read_args()
    if not action:
        return
    elif action == "make":
        make_docs()
    elif action == "build":
        if make_docs():
            build_docs()
    elif action == "docs":
        if make_docs():
            serve_docs()
    elif action == "github":
        if make_docs():
            ship_docs()
            commit()


main()
