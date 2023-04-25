from pathlib import Path
import docx
import PyPDF2
import re

def split_reference(reference):
    match = re.match(r'^(.*?)\s\((\d{4})\)\s(.+)$', reference)
    if match:
        name_year = match.group(1) + " " + match.group(2)
        title = match.group(3)
        return (name_year, title)
    else:
        return None

SOURCE_DIRECTORY = "collective and peer production"
SOURCE_DIRECTORY = "worker collectives"

THE_PARAGRAPHS = []

start_from = 0
for the_docx in Path(SOURCE_DIRECTORY).glob('*.docx'):
    prepend_citation, _ = split_reference(
                the_docx.name
        )
    print(f"... working on {prepend_citation}")
    doc = docx.Document(the_docx.absolute())
    for number, para in enumerate(doc.paragraphs, start_from):
        if number - start_from > 1: # skip the made by wordtune read preamble
            THE_PARAGRAPHS.append(
                f"#{number} " + para.text + f" | ({prepend_citation})\n\n"
            )
    start_from = number # so that we count upwards always

with open('document-worker-collectives.txt', 'w') as the_text_file:
    for para in THE_PARAGRAPHS:
        the_text_file.write(para)

