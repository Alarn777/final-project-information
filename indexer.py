from json import JSONDecodeError
from os.path import curdir, sep
import os
import json
import re


def cleaning2(text):
    text = re.sub(r'\b(?:(?:https?|ftp)://)?\w[\w-]*(?:\.[\w-]+)+\S*', ' ', text.lower())
    words = re.findall(r'[a-z]+', text)
    return ' '.join(words)


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def index_file():
    path = '/files/'
    json_path = "/indexes/"
    for filename in os.listdir(curdir + path):
        if filename.startswith("."):
            continue
        filename_with_txt = filename
        try:
            filename = filename[:-4]
            filename = filename + ".json"
            f = open(curdir + json_path + filename, 'w')
            index_file_json = {"name": filename_with_txt}
            words_in_txt_file = {}
            read = open(curdir + path + filename_with_txt, 'r')
            for line in read:
                line = cleaning2(line)
                line_arr = line.split()
                for word in line_arr:
                    if is_ascii(word):
                        if word in words_in_txt_file:
                            words_in_txt_file[word] = words_in_txt_file[word] + 1
                        else:
                            words_in_txt_file[word] = 1

            index_file_json["words"] = words_in_txt_file
            json.dump(index_file_json, f)
            f.close()

        except IOError:
            print("Error while indexing file!")
            continue

    for filename in os.listdir(curdir + path):
        if filename.startswith("."):
            continue
        try:
            f = open(curdir + json_path + filename, 'r')

            try:
                datastore = json.load(f)
            except JSONDecodeError:
                print("Faulty file detected!" + filename)
                if os.path.exists(filename):
                    os.remove(filename)
                    print("Removed file: " + filename)
                else:
                    print("The file does not exist")

        except IOError:
            if os.path.exists(filename):
                os.remove(filename)
                print("Removed file: " + filename)
            else:
                print("The file does not exist")
            print("Error opening while checking file!")



    # f = open(curdir + json_path + filename, 'r')
    # try:
    #     datastore = json.load(f)
    # except IOError:
    #     pass
    #
    # if "words" in datastore:
    #     if search_array[0] in datastore["words"]:
    #         max_occurences_in_file[datastore["name"]] = int(datastore["words"][search_array[0]])
