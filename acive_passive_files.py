from json import JSONDecodeError
from os.path import curdir, sep
import os
import json
import helpers

class ActivePassive:
    @staticmethod
    def initial_activation():
        filename = "active_passive_list.json"
        try:
            f = open(curdir + "/data/" + filename, 'r')
            if f:
                list_of_files = json.load(f)
                for doc_file in os.listdir("docs"):
                    if doc_file in list_of_files.keys():
                        continue
                    else:
                        list_of_files[doc_file] = True
                f.close()
                f = open(curdir + "/data/" + filename, 'w')
                json.dump(list_of_files, f)
                f.close()
                return
        except IOError:
            print("No initial activation was done, doing...")

        f = open(curdir + "/data/" + filename, 'w')
        index_file_json = {}
        for doc_file in os.listdir("docs"):
            index_file_json[doc_file] = True
        json.dump(index_file_json, f)
        f.close()
        return

    # returns True or False
    @staticmethod
    def check_if_active(doc_file):
        filename = "active_passive_list.json"
        try:
            f = open(curdir + "/data/" + filename, 'r')
            if f:
                list_of_files = json.load(f)
                if list_of_files[doc_file]:
                    return True
                else:
                    return False
            f.close()
        except IOError:
            print("Error opening file...")

    @staticmethod
    def deactivate_file(doc_file):
        filename = "active_passive_list.json"
        try:
            f = open(curdir + "/data/" + filename, 'r')
            if f:
                list_of_files = json.load(f)
                list_of_files[doc_file] = False
                f.close()
                f = open(curdir + "/data/" + filename, 'w')
                json.dump(list_of_files, f)
            f.close()

            #reindexing
            docs_path = os.path.abspath("./docs")
            data_path = os.path.abspath("./data")
            helpers.assert_dir(docs_path)
            helpers.assert_dir(data_path)
            helpers.index(docs_path, data_path)
            print('Index redone.')

        except IOError:
            print("Error opening file...")

    @staticmethod
    def activate_file(doc_file):
        # can be implemented if needed
        pass



# initial_activation()
# deactivate_file("1.txt")
# print(check_if_active("1.txt"))
# print(check_if_active("2.txt"))
