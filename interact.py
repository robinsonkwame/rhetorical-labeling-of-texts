import pickle
from pathlib import Path
import json
import os
from label_stases import (get_interpretive_stasis, get_legal_stasis)

SOURCE_DIRECTORY = "" # "collective and peer production"

AUTHOR = "0LGO24_author_to_lines.pkl"
STASIS = "0LGO24_stasis_to_lines.pkl"

# TODO: make Path interation over *_author_*.pkl and stasis

author_to_lines = None
stasis_to_lines = None

def load_files_of(template="*_author*.pkl"):
    add_to = dict()
    for author_filename in Path(SOURCE_DIRECTORY).glob(template):
        #import pdb; pdb.set_trace()
        with open(os.path.join(author_filename), 'rb') as handle:
            loaded_dict =\
                pickle.load(handle)
            add_to.update(loaded_dict)
            print(f"\t setting with {author_filename}")
    return add_to

author_to_lines = load_files_of(template="*_author*.pkl")
stasis_to_lines = load_files_of(template="*_stasis*.pkl")

assert author_to_lines is not None
assert stasis_to_lines is not None

INTERPRETIVE_STASIS = {
    1: "SPIRIT OR LETTER",
    2: "CONTRADICTION",
    3: "AMBIGUITY",
    4: "I_DEFINITION",
    5: "ASSIMILATION",
    6: "JURISDICTION"
}

STASIS = {
    1: "FACT",
    2: "L_DEFINITION",
    3: "CAUSAL",
    4: "VALUE",
    5: "POLICY",    
    '01': INTERPRETIVE_STASIS[1],
    '02': INTERPRETIVE_STASIS[2],
    '03': INTERPRETIVE_STASIS[3],
    '04': INTERPRETIVE_STASIS[4],
    '05': INTERPRETIVE_STASIS[5],
    '06': INTERPRETIVE_STASIS[6]
}

def list_all_of(stasis: list):
    for a_stasis in stasis:
        # can we use python's new loop setter syntax? hard to parse
        for the_statis in [get_interpretive_stasis(a_stasis), get_legal_stasis(a_stasis)]:
            if the_statis and the_statis in stasis_to_lines:
                    print(
                        f"({the_statis})",
                        json.dumps(
                            stasis_to_lines[the_statis],
                            indent=2
                        )
                    )

def print_all(arg):
    print(
        json.dumps(
            stasis_to_lines,
            indent=2
        )
    )

def list_authors():
    pass

OPTIONS = {
    1: list_all_of,
    2: print_all
    # union of list_all_of (see we can combine statis, iterp stasis together)
}

while True:
    the_choice_with_arguments = input(
        "\noptions:"
        "\n\t 1: list all args: stasis (or anythign else to quit)"
        "\n\t 2: dump everything to screen"
        "\n> "
    )

    if the_choice_with_arguments:
        the_choice_with_arguments = the_choice_with_arguments.replace(',', ' ').split()

        the_choice = int(the_choice_with_arguments[0])
        an_argument = the_choice_with_arguments[1:]

        if the_choice in OPTIONS:
            OPTIONS[the_choice](an_argument)
    else: 
        break
    