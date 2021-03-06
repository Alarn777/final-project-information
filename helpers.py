import json

import nltk
import re
import os
import pickle
import sys
from nltk.corpus import stopwords
import nltk
import ssl
import active_passive_files


def assert_dir(path):
    if not os.path.exists(path):
        print('ERROR: {} does not exists'.format(path))
        sys.exit(1)

    if not os.path.isdir(path):
        print('ERROR: {} is not a directory'.format(path))
        sys.exit(1)


def preprocess_text(text):
    processed_text = text.lower()
    processed_text = processed_text.replace("’", "'")
    processed_text = processed_text.replace("“", '"')
    processed_text = processed_text.replace("”", '"')

    non_words = re.compile(r"[^A-Za-z']+")
    processed_text = re.sub(non_words, ' ', processed_text)

    return processed_text


def get_text_from_file(filename):
    with open(filename, encoding='cp1252', mode='r') as f:
        text = f.read()

    return text


def get_words_from_text(text):
    stop_words = set(stopwords.words('english'))

    processed_text = preprocess_text(text)
    # words = {w for w in processed_text.split() if w not in stop_words}                                            changed!

    words = processed_text.split()
    words_count = {}
    for word in words:
        if word in words_count:
            words_count[word] = words_count[word] + 1
        else:
            words_count[word] = 1

    return words_count
    # words = {w for w in processed_text.split()}
    #
    # return words


def build_inverted_index(docs_path):
    inverted_index = {}
    Checker = active_passive_files.ActivePassive

    json_dict = {
    }

    for doc_file in os.listdir(docs_path):
        if doc_file.startswith("."):
            continue
        # check if doc_file is active
        if Checker.check_if_active(doc_file):
            filename = os.path.join(docs_path, doc_file)
            text = get_text_from_file(filename)
            words = get_words_from_text(text)
            json_dict[os.path.basename(filename)] = []
            for word in words.keys():
                json_dict[os.path.basename(filename)].append({word: words[word]})

                if inverted_index.get(word, None) is None:

                    # json_dict[word] = [{"filename": filename,
                    #                    "occurrences": words[word]}]
                    inverted_index[word] = {filename}
                else:

                    # json_dict[word].append({"filename": filename,
                    #                                      "occurrences": words[word]})
                    inverted_index[word].add(filename)

    data_path = os.path.abspath("./data")
    occurances_file = os.path.join(data_path, 'occurances_file.json')
    with open(occurances_file, "w") as write_file:
        json.dump(json_dict, write_file)
        write_file.close()
    return inverted_index


def index(docs_path, data_path):
    # initial activation of all files
    active_passive_files.ActivePassive.initial_activation()

    inverted_index = build_inverted_index(docs_path)
    dic_file = os.path.join(data_path, 'dictionary.txt')
    inverted_index_file = os.path.join(data_path, 'inverted_index.pickle')

    with open(dic_file, mode='w') as f:
        for word in inverted_index.keys():
            f.write(word + '\n')

    with open(inverted_index_file, mode='wb') as f:
        pickle.dump(inverted_index, f)
