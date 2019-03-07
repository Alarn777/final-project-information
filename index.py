import os
import shutil

import helpers


def load_from_source():
    source_path = os.path.abspath("./source")
    docs_path = os.path.abspath("./docs")
    data_path = os.path.abspath("./data")

    # move files from source to docs
    files_detected = True
    for doc_file in os.listdir(source_path):
        if doc_file.startswith("."):
            continue
        # os.rename(source_path + "/" + doc_file, docs_path + "/" + doc_file)
        shutil.move(os.path.join(source_path, doc_file), os.path.join(docs_path, doc_file))
        files_detected = True
        print('New files detected!')

    if files_detected:
        helpers.assert_dir(docs_path)
        helpers.assert_dir(data_path)
        helpers.index(docs_path, data_path)
        print('Indexed new files done.')

    return


def do_index():
    source_path = os.path.abspath("./source")
    docs_path = os.path.abspath("./docs")
    data_path = os.path.abspath("./data")

    # move files from source to docs
    files_detected = True
    # for doc_file in os.listdir(source_path):
    #     # os.rename(source_path + "/" + doc_file, docs_path + "/" + doc_file)
    #     shutil.move(os.path.join(source_path, doc_file), os.path.join(docs_path, doc_file))
    #     files_detected = True
    #     print('New files detected!')

    if files_detected:
        helpers.assert_dir(docs_path)
        helpers.assert_dir(data_path)
        helpers.index(docs_path, data_path)
        print('Index done.')


# do_index()
