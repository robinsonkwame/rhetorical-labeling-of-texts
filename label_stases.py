import string
import pickle
import re
import random
from collections import defaultdict
import sys

author_to_lines = defaultdict(defaultdict(dict).copy)
stasis_to_lines = defaultdict(defaultdict(dict).copy)

N = 6
TAG_FOR_THIS_RUN = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

author_pkl_filename = f"{TAG_FOR_THIS_RUN}_author_to_lines.pkl"
stasis_pkl_filename = f"{TAG_FOR_THIS_RUN}_stasis_to_lines.pkl"

DOCUMENT = "document-worker-collectives.txt"

INTERPRETIVE_STASIS = {
    1: "SPIRIT OR LETTER",
    2: "CONTRADICTION",
    3: "AMBIGUITY",
    4: "I_DEFINITION",
    5: "ASSIMILATION",
    6: "JURISDICTION"
}

legend_interpretive_stasis = " ".join(f"|{value} => {key}|" for key, value in  INTERPRETIVE_STASIS.items())

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
    '06': INTERPRETIVE_STASIS[6],
    '*': 'notable' # for items that I should take special note of
}

legend_legal_stasis = " ".join(f"{key} <= {value};" for key, value in [(1, 'Fact'), (2, 'Definition'), (3, 'Causal'), (4, 'Value'), (5, 'Policy')])

def make_stasis(content, line_no, citation, stasis):
    stasis_to_lines[stasis][citation][line_no] = content

def make_author(content, line_no, citation, stasis):
    author_to_lines[citation][stasis][line_no] = content

def make_notable(content, line_no, citation, stasis):
    # essentially making the author "*" or notable
    author_to_lines['*'][citation][line_no] = content

# should be a util function
def get_interpretive_stasis(a_combined_stasis):
    """
        user can enter stuff like
            1 <- no interpretive stasis
            11 <- contradiction
            06 <- no (legal) stasis, only interpretive
    """
    the_interpretive_stasis = None

    if len(a_combined_stasis) > 1: # then we've got something
        the_interpretive_stasis = a_combined_stasis[1:]
        the_interpretive_stasis =\
            STASIS.get('0'+the_interpretive_stasis, None) # this smells but whatever

    return the_interpretive_stasis


def get_legal_stasis(a_combined_stasis):
    """
        user can enter stuff like 
            1 <- Fact stasis
            11 <- fact
            06 <- no (legal) stasis, only interpretive
    """
    the_legal_stasis = None

    if a_combined_stasis[0] != '0' and a_combined_stasis[0] != ' ':
        the_legal_stasis = int(a_combined_stasis[0])
        the_legal_stasis =\
            STASIS.get(the_legal_stasis, None) # None for typos,e tc

    return the_legal_stasis

if __name__ == "__main__":

    SKIP_TO_LINE_NO = 0
    if len(sys.argv) > 1:
        SKIP_TO_LINE_NO = int(sys.argv[1])

    # todo: make a skip to line_no, read in former data structure
    the_authors_to_skip = set()
    with open(DOCUMENT, 'r') as snippets:
        for a_paragraph in snippets:
            content = re.search(r'#\d+ (.+?) \|', a_paragraph)
            if content:
                content = content.group(1)

                line_no = int(re.search(r'#(\d+)', a_paragraph).group(1))
                citation = re.search(r'\| \((.+)\)', a_paragraph).group(1)

                # SKip logic
                if line_no < SKIP_TO_LINE_NO:
                    continue

                # Case 1: we already have authors we want to skip
                if citation in the_authors_to_skip:
                    print(f"\t\t ... skipping {citation}")
                    continue

                print(
                    f"\n* {citation} [{line_no}]"
                    f"\t {content}"
                    "\n",
                    f"\n{legend_interpretive_stasis}",
                    f"\n{legend_legal_stasis}",
                    f"\n (star ('*') for notable snippet)"
                )

                stases = input('Enter stases (enter to skip/stop to stop/author(or line no) to skip author(to line no))')
                if "" == stases or " " == stases:
                    continue

                if "author" == stases.lower(): # ideally we could skip by author but bleh
                    the_authors_to_skip.add( citation )
                    print(the_authors_to_skip)

                if "skip" in stases.lower():
                    # so we can examine the text file for the next relevant author or location
                    # to skip ahead to
                    new_line_number = int(stases.split()[1])
                    SKIP_TO_LINE_NO = new_line_number
                    continue

                if "stop" == stases.lower():
                    break

                # Case 2: we read a new line or have enough and wish to skip
                if citation in the_authors_to_skip:
                    continue

                for a_stasis in stases.split(','):
                    a_legal_stasis = get_legal_stasis(a_stasis)
                    a_interpretive_stasis = get_interpretive_stasis(a_stasis)
                    a_notable_snippet = None
                    if a_stasis.strip() == '*':
                        a_notable_snippet = '*'
                    # bug, when given 2, 04, does 2 but skips ?
                    for the_type, the_stasis in [
                        ('legal', a_legal_stasis),
                        ('interpretive', a_interpretive_stasis),
                        ('notable', a_notable_snippet)]:
                        if the_stasis: # in case of a typo
                            print(f"\t adding {the_type} {the_stasis} ")
                            make_stasis(
                                content=content,
                                line_no=line_no,
                                citation=citation,
                                stasis=the_stasis
                            )
                            make_author(
                                content=content,
                                line_no=line_no,
                                citation=citation,
                                stasis=the_stasis
                            )
                            make_notable(
                                content=content,
                                line_no=line_no,
                                citation=citation,
                                stasis=the_stasis
                            )                            
                if True: # no need to incrementally write
                    print(f"\t... silently saving")
                    with open(author_pkl_filename, 'wb') as handle:
                        pickle.dump(author_to_lines, handle, protocol=pickle.HIGHEST_PROTOCOL)
                    with open(stasis_pkl_filename, 'wb') as handle:
                        pickle.dump(stasis_to_lines, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(author_pkl_filename, 'wb') as handle:
        pickle.dump(author_to_lines, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(stasis_pkl_filename, 'wb') as handle:
        pickle.dump(stasis_to_lines, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print(" DONE!  BE SURE TO NAME THE PICKLED FILES SO THE DON'T GET OVER WRITTEN!!!!")
